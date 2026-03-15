import shutil
import json, os, datetime, time, random
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

# ===================== 公共配置 =====================
BASE = "https://play.limitlesstcg.com/api"
GAME_ID = os.environ.get("POCKET_GAME_ID", "POCKET")
# 核心优化：新增不限天数开关（True=不限天数，False=按DAYS_BACK过滤）
UNLIMITED_DAYS = os.environ.get("UNLIMITED_DAYS", "False").lower() == "true"
# 兼容原有配置：仅当 UNLIMITED_DAYS=False 时生效
DAYS_BACK = int(os.environ.get("DAYS_BACK", "30"))
MIN_PLAYERS = int(os.environ.get("MIN_PLAYERS", "32"))
REQUEST_GAP_SEC = float(os.environ.get("REQUEST_GAP_SEC", 2.0))
BATCH_SIZE = 10
BATCH_SLEEP_SEC = 5.0
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", 8))
REQUEST_TIMEOUT = 120.0

# 全局变量
_last_request_ts = 0.0
failed_tournaments = []
# 赛事列表文件路径（抽离为常量，便于维护）
TOURNAMENTS_JSON_PATH = "web/src/data/tournaments.json"

# ===================== 工具函数 =====================
def get_json(url: str, api_type: str = "unknown", tid: str = "unknown"):
    global _last_request_ts
    for attempt in range(MAX_RETRIES + 1):
        now = time.time()
        wait = REQUEST_GAP_SEC - (now - _last_request_ts)
        if wait > 0:
            jitter = random.uniform(-0.5, 0.5)
            wait = max(0.1, wait + jitter)
            time.sleep(wait)
        
        req = Request(url, headers={"User-Agent": "ptcgp-tier-site/1.0"})
        try:
            print(f"[请求] 尝试{attempt+1}/{MAX_RETRIES+1} | 赛事{tid} | 接口{api_type} | URL: {url}")
            with urlopen(req, timeout=REQUEST_TIMEOUT) as r:
                _last_request_ts = time.time()
                resp_data = json.loads(r.read().decode("utf-8"))
                print(f"[成功] 赛事{tid} | 接口{api_type} | 返回数据长度: {len(resp_data) if isinstance(resp_data, list) else '非列表'}")
                return resp_data
        except HTTPError as e:
            if e.code == 429:
                retry_after = e.headers.get("Retry-After")
                sleep_s = float(retry_after) if retry_after else min(60.0, 2.0 ** attempt)
                print(f"[429限流] 赛事{tid} | 接口{api_type} | 等待{sleep_s:.1f}秒后重试")
                time.sleep(sleep_s)
                continue
            err_msg = f"[HTTP错误] 赛事{tid} | 接口{api_type} | 状态码{e.code}"
            print(err_msg)
            failed_tournaments.append({"tid": tid, "api": api_type, "error": err_msg})
            raise
        except TimeoutError:
            sleep_s = min(60.0, 2.0 ** attempt)
            print(f"[超时错误] 赛事{tid} | 接口{api_type} | 等待{sleep_s:.1f}秒后重试")
            time.sleep(sleep_s)
            continue
        except URLError as e:
            sleep_s = min(30.0, 2.0 ** attempt)
            print(f"[网络错误] 赛事{tid} | 接口{api_type} | 原因:{e.reason} | 等待{sleep_s:.1f}秒后重试")
            time.sleep(sleep_s)
            continue
    
    err_msg = f"[请求失败] 赛事{tid} | 接口{api_type} | 累计{MAX_RETRIES+1}次尝试超时"
    print(err_msg)
    failed_tournaments.append({"tid": tid, "api": api_type, "error": err_msg})
    raise RuntimeError(err_msg)

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def iso_to_date(iso_str):
    if not iso_str:
        return None
    return datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00")).date()

def fetch_recent_tournaments():
    """抓取赛事列表（支持不限天数/指定天数两种模式）"""
    out = []
    page = 1
    cutoff = None
    
    if not UNLIMITED_DAYS:
        cutoff = datetime.date.today() - datetime.timedelta(days=DAYS_BACK)
        print(f"📌 有限天数模式 | 抓取最近{DAYS_BACK}天的赛事 | 截止日期: {cutoff}")
    else:
        print(f"📌 不限天数模式 | 抓取所有可获取的赛事（直到API返回空数据）")
    
    while True:
        url = f"{BASE}/tournaments?game={GAME_ID}&limit=50&page={page}"
        print(f"\n----- 分页请求 | 第{page}页 -----")
        arr = get_json(url, api_type="tournament_list", tid=f"page_{page}")
        
        if not arr:
            print(f"第{page}页无数据，终止分页请求")
            break
        
        for t in arr:
            t_id = t.get("id", "未知ID")
            t_players = t.get("players", 0)
            t_date = iso_to_date(t["date"])
            
            if t_players < MIN_PLAYERS:
                print(f"  ❌ 赛事{t_id} | 参与人数{t_players} < {MIN_PLAYERS}，跳过")
                continue
            
            if not UNLIMITED_DAYS and t_date and t_date < cutoff:
                print(f"  ❌ 赛事{t_id} | 日期{t_date} < 截止日期{cutoff}，跳过")
                print(f"\n第{page}页出现过期赛事，终止分页请求")
                return out
            
            out.append(t)
            print(f"  ✅ 赛事{t_id} | 符合条件，加入列表")
        
        page += 1
    
    print(f"\n✅ 新抓取的赛事列表完成 | 总计符合条件的赛事数：{len(out)}")
    return out

def load_existing_tournaments():
    """加载已有的赛事列表（若文件不存在则返回空列表）"""
    if not os.path.exists(TOURNAMENTS_JSON_PATH):
        print(f"⚠️ 未找到旧的赛事列表文件 {TOURNAMENTS_JSON_PATH}，首次运行")
        return []
    try:
        with open(TOURNAMENTS_JSON_PATH, "r", encoding="utf-8") as f:
            existing = json.load(f)
        print(f"✅ 加载旧赛事列表完成 | 已有 {len(existing)} 场赛事")
        return existing
    except Exception as e:
        print(f"❌ 读取旧赛事列表失败：{str(e)} | 忽略旧数据，按新数据处理")
        return []

# ===================== 核心逻辑（增量更新） =====================
def main():
    global failed_tournaments
    failed_tournaments = []
    
    # 1. 移除「清理旧raw文件夹」的代码，保留历史数据
    # shutil.rmtree("web/src/data/raw", ignore_errors=True)  # 注释/删除这行
    
    # 2. 加载旧的赛事列表，提取已有的赛事ID
    existing_tournaments = load_existing_tournaments()
    existing_tids = {t["id"] for t in existing_tournaments if "id" in t}  # 转集合，方便快速查询
    
    # 3. 抓取新的赛事列表
    new_tournaments = fetch_recent_tournaments()
    
    # 4. 过滤新增赛事（排除已存在的ID）
    added_tournaments = [t for t in new_tournaments if t["id"] not in existing_tids]
    added_tids = {t["id"] for t in added_tournaments}
    print(f"\n📊 增量统计：")
    print(f"  - 旧赛事ID数量：{len(existing_tids)}")
    print(f"  - 新抓取赛事ID数量：{len({t['id'] for t in new_tournaments})}")
    print(f"  - 新增赛事ID数量：{len(added_tids)}")
    
    # 5. 合并新旧赛事列表（旧 + 新），去重并写入文件
    # 先去重（避免旧列表中可能的重复ID），再合并新增的
    all_tournaments = existing_tournaments + added_tournaments
    # 去重：按ID保留唯一值，保留首次出现的顺序
    unique_tournaments = []
    unique_tids = set()
    for t in all_tournaments:
        if t["id"] not in unique_tids:
            unique_tids.add(t["id"])
            unique_tournaments.append(t)
    write_json(TOURNAMENTS_JSON_PATH, unique_tournaments)
    print(f"✅ 合并后赛事列表已保存 | 总唯一赛事数：{len(unique_tournaments)}")
    
    # 6. 仅对新增的赛事抓取数据（无新增则直接结束）
    total_added = len(added_tournaments)
    if total_added == 0:
        print("\n⚠️ 无新增赛事，无需抓取数据，结束流程")
        return
    print(f"\n===== 开始抓取 {total_added} 场新增赛事的原始数据 =====")
    
    for idx, t in enumerate(added_tournaments):
        tid = t["id"]
        current_idx = idx + 1
        print(f"\n===== 处理第 {current_idx}/{total_added} 场新增赛事 | ID: {tid} =====")
        
        # 批次休息
        if current_idx % BATCH_SIZE == 0 and current_idx != total_added:
            print(f"📌 已抓取{current_idx}场新增赛事，休息{BATCH_SLEEP_SEC}秒缓解服务器压力...")
            time.sleep(BATCH_SLEEP_SEC)
        
        # 单场赛事请求（失败跳过）
        try:
            details = get_json(f"{BASE}/tournaments/{tid}/details", api_type="details", tid=tid)
            time.sleep(0.5)
            
            standings = get_json(f"{BASE}/tournaments/{tid}/standings", api_type="standings", tid=tid)
            time.sleep(0.5)
            
            pairings = get_json(f"{BASE}/tournaments/{tid}/pairings", api_type="pairings", tid=tid)
            
            # 保存数据（保留旧文件夹，直接写入新增赛事的文件夹）
            write_json(f"web/src/data/raw/{tid}/details.json", details)
            write_json(f"web/src/data/raw/{tid}/standings.json", standings)
            write_json(f"web/src/data/raw/{tid}/pairings.json", pairings)
            print(f"✅ 新增赛事{tid}数据保存完成")
        
        except Exception as e:
            print(f"❌ 新增赛事{tid}抓取失败：{str(e)} | 跳过该赛事，继续下一场")
            continue
    
    # 7. 最终统计
    print("\n===== 增量数据抓取流程结束 ======")
    print(f"📊 统计：")
    print(f"  - 新增赛事总数：{total_added}")
    print(f"  - 新增赛事抓取成功数：{total_added - len(failed_tournaments)}")
    print(f"  - 新增赛事抓取失败数：{len(failed_tournaments)}")
    if failed_tournaments:
        print(f"  - 失败详情：{json.dumps(failed_tournaments, ensure_ascii=False, indent=2)}")
        write_json("web/src/data/failed_tournaments.json", failed_tournaments)
    print("🎉 增量数据抓取完成！历史数据已保留，仅新增赛事数据已抓取")

if __name__ == "__main__":
    main()
