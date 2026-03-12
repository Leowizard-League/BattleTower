import shutil
import json, os, datetime, time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

# ===================== 公共配置（和原代码一致） =====================
BASE = "https://play.limitlesstcg.com/api"
GAME_ID = os.environ.get("POCKET_GAME_ID", "POCKET")
DAYS_BACK = int(os.environ.get("DAYS_BACK", "14"))
MIN_PLAYERS = int(os.environ.get("MIN_PLAYERS", "32"))
REQUEST_GAP_SEC = float(os.environ.get("REQUEST_GAP_SEC", "0.35"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "8"))

# 全局变量：记录上一次请求时间（用于限流）
_last_request_ts = 0.0

# ===================== 公共工具函数（和原代码一致） =====================
def get_json(url: str):
    global _last_request_ts
    for attempt in range(MAX_RETRIES + 1):
        # 限流：两次请求间隔≥REQUEST_GAP_SEC
        now = time.time()
        wait = REQUEST_GAP_SEC - (now - _last_request_ts)
        if wait > 0:
            time.sleep(wait)
        
        # 发送请求
        req = Request(url, headers={"User-Agent": "ptcgp-tier-site/1.0"})
        try:
            with urlopen(req, timeout=60) as r:
                _last_request_ts = time.time()
                return json.loads(r.read().decode("utf-8"))
        # 429 限流错误：按 Retry-After 或指数退避重试
        except HTTPError as e:
            if e.code == 429:
                retry_after = e.headers.get("Retry-After")
                sleep_s = float(retry_after) if retry_after else min(60.0, 2.0 ** attempt)
                print(f"[429] Sleep {sleep_s:.1f}s then retry ({attempt+1}/{MAX_RETRIES})")
                time.sleep(sleep_s)
                continue
            raise
        # 网络抖动：指数退避重试
        except URLError:
            sleep_s = min(30.0, 2.0 ** attempt)
            print(f"[URLError] Sleep {sleep_s:.1f}s then retry ({attempt+1}/{MAX_RETRIES})")
            time.sleep(sleep_s)
            continue
    raise RuntimeError(f"Failed to fetch after retries: {url}")

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def iso_to_date(iso_str):
    """辅助函数：ISO时间转date对象（原代码中用到）"""
    if not iso_str:
        return None
    return datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00")).date()

def fetch_recent_tournaments():
    """抓取符合条件的赛事列表"""
    cutoff = datetime.date.today() - datetime.timedelta(days=DAYS_BACK)
    out = []
    page = 1
    while True:
        url = f"{BASE}/tournaments?game={GAME_ID}&limit=50&page={page}"
        arr = get_json(url)
        if not arr:
            break
        for t in arr:
            d = iso_to_date(t["date"])
            if d < cutoff:
                return out
            if t.get("players", 0) >= MIN_PLAYERS:
                out.append(t)
        page += 1
    return out

# ===================== 核心逻辑：仅抓取原始数据 =====================
def main():
    # 1. 清理旧的raw文件夹
    shutil.rmtree("web/src/data/raw", ignore_errors=True)
    print("清理旧的raw文件夹完成")
    
    # 2. 抓取符合条件的赛事列表并保存
    tournaments = fetch_recent_tournaments()
    write_json("web/src/data/tournaments.json", tournaments)
    print(f"抓取到 {len(tournaments)} 场符合条件的赛事")
    
    # 3. 遍历赛事，拉取并保存单场赛事的原始数据
    for idx, t in enumerate(tournaments):
        tid = t["id"]
        print(f"正在处理第 {idx+1}/{len(tournaments)} 场赛事，ID: {tid}")
        
        # 拉取单场赛事的3类数据
        details = get_json(f"{BASE}/tournaments/{tid}/details")
        standings = get_json(f"{BASE}/tournaments/{tid}/standings")
        pairings = get_json(f"{BASE}/tournaments/{tid}/pairings")
        
        # 保存到raw文件夹
        write_json(f"web/src/data/raw/{tid}/details.json", details)
        write_json(f"web/src/data/raw/{tid}/standings.json", standings)
        write_json(f"web/src/data/raw/{tid}/pairings.json", pairings)
    
    print("所有原始数据抓取并保存完成！")

if __name__ == "__main__":
    main()
