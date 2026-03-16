import json, os, datetime, math

# ===================== 公共配置（和原代码一致） =====================
MIN_PLAYERS = int(os.environ.get("MIN_PLAYERS", "32"))
USAGE_THRESHOLD = float(os.environ.get("USAGE_THRESHOLD", "0.01"))
TOP_CUT_N = int(os.environ.get("TOP_CUT_N", "32"))
W1, W2, W3 = 0.4, 0.5, 0.1  # 加权系数

# ===================== 公共工具函数 =====================
def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def get_deck_id_from_standing(standing):
    """从standings条目提取牌组ID（原代码中的逻辑，需和原代码保持一致）"""
    # 这里需要替换成你原代码中实际的牌组ID提取逻辑，示例如下：
    deck_info = standing.get("deck", {})
    return deck_info.get("id", "unknown") or "unknown"

def points_by_placing(placing):
    """根据排名计算得分（原代码中的逻辑，需和原代码保持一致）"""
    if placing == 1:
        return 10.0
    elif placing == 2:
        return 8.0
    elif 3 <= placing <= 4:
        return 6.0
    elif 5 <= placing <= 8:
        return 4.0
    elif 9 <= placing <= 16:
        return 2.0
    elif 17 <= placing <= 32:
        return 1.0
    else:
        return 0.0

def minmax_scale(data):
    """最小-最大标准化（缩放到0~1）"""
    if not data:
        return {}
    values = list(data.values())
    min_val = min(values)
    max_val = max(values)
    if max_val == min_val:
        return {k: 0.0 for k in data.keys()}
    return {k: (v - min_val) / (max_val - min_val) for k, v in data.items()}

def tier_label(score):
    """根据综合得分返回Tier等级"""
    if score >= 0.9:
        return "S"
    elif score >= 0.7:
        return "A"
    elif score >= 0.5:
        return "B"
    elif score >= 0.3:
        return "C"
    elif score >= 0.1:
        return "D"
    else:
        return "E"

# ===================== 核心逻辑：读取本地原始数据并统计 =====================
def main():
    # 1. 读取本地的赛事列表
    with open("web/public/data/tournaments.json", "r", encoding="utf-8") as f:
        tournaments = json.load(f)
    print(f"读取到本地 {len(tournaments)} 场赛事数据")
    
    # 2. 初始化统计字典
    deck_total_counts = {}  # 所有赛事牌组出场次数
    total_entries_all = 0
    deck_top32_counts = {}  # Top32牌组出场数
    deck_weighted_points = {}  # Top32牌组加权得分
    top32_total_slots = 0
    
    # 玩家相关统计（含新增的出场次数）
    player_points = {}
    player_country = {}
    player_games = {}  # 选手出场次数
    
    matchup = {}  # 胜率矩阵
    
    # 3. 遍历赛事，读取本地原始数据并统计
    for idx, t in enumerate(tournaments):
        tid = t["id"]
        print(f"正在统计第 {idx+1}/{len(tournaments)} 场赛事，ID: {tid}")
        
        # 读取本地raw文件夹中的数据
        try:
            with open(f"web/public/data/raw/{tid}/details.json", "r", encoding="utf-8") as f:
                details = json.load(f)
            with open(f"web/public/data/raw/{tid}/standings.json", "r", encoding="utf-8") as f:
                standings = json.load(f)
            with open(f"web/public/data/raw/{tid}/pairings.json", "r", encoding="utf-8") as f:
                pairings = json.load(f)
        except FileNotFoundError:
            print(f"警告：赛事 {tid} 的原始数据文件缺失，跳过")
            continue
        
        # 仅处理POCKET赛事
        game = str(details.get("game", "")).upper()
        if game != "POCKET":
            print(f"跳过非POCKET赛事：{tid}")
            continue
        
        # 构建「玩家→牌组ID」映射
        p2deck = {}
        for s in standings:
            p2deck[s["player"]] = get_deck_id_from_standing(s)
        
        # 统计：全赛事牌组出场数 + 选手出场次数
        for s in standings:
            deck = get_deck_id_from_standing(s)
            if deck == "unknown":
                continue
            deck_total_counts[deck] = deck_total_counts.get(deck, 0) + 1
            total_entries_all += 1
            
            # 统计选手出场次数
            player = s["player"]
            player_games[player] = player_games.get(player, 0) + 1
        
        # 统计：Top32数据
        for s in standings:
            placing = s.get("placing")
            if not placing or placing > TOP_CUT_N:
                continue
            deck = get_deck_id_from_standing(s)
            if deck == "unknown":
                continue
            
            # Top32出场数
            deck_top32_counts[deck] = deck_top32_counts.get(deck, 0) + 1
            top32_total_slots += 1
            
            # 加权得分
            pts = points_by_placing(int(placing))
            deck_weighted_points[deck] = deck_weighted_points.get(deck, 0) + pts
            
            # 玩家得分/国家
            player = s["player"]
            player_points[player] = player_points.get(player, 0) + pts
            player_country[player] = s.get("country", "")
        
        # 统计：胜率矩阵
        for m in pairings:
            p1, p2 = m.get("player1"), m.get("player2")
            winner = m.get("winner")
            if not p1 or not p2 or winner in (0, -1, None):
                continue
            
            d1, d2 = p2deck.get(p1, "unknown"), p2deck.get(p2, "unknown")
            if d1 == "unknown" or d2 == "unknown":
                continue
            
            # 记录A vs B的胜负
            w, tot = matchup.get((d1, d2), (0, 0))
            tot += 1
            if winner == p1:
                w += 1
            matchup[(d1, d2)] = (w, tot)
            
            # 反向记录B vs A
            w, tot = matchup.get((d2, d1), (0, 0))
            tot += 1
            if winner == p2:
                w += 1
            matchup[(d2, d1)] = (w, tot)
    
    # 4. 筛选有效牌组（使用率≥1%）
    if total_entries_all == 0:
        eligible_decks = []
    else:
        eligible_decks = [
            d for d, c in deck_total_counts.items()
            if (c / total_entries_all) >= USAGE_THRESHOLD
        ]
    print(f"筛选出 {len(eligible_decks)} 个有效牌组（使用率≥{USAGE_THRESHOLD*100}%）")
    
    # 5. 计算Tier核心指标（原始→对数→标准化）
    # 原始数据
    data1 = {d: float(deck_top32_counts.get(d, 0)) for d in eligible_decks}  # Top32出场数
    data2 = {d: float(deck_weighted_points.get(d, 0)) for d in eligible_decks}  # 加权得分
    data3 = {d: (data1[d] / top32_total_slots) * 100.0 if top32_total_slots > 0 else 0.0 for d in eligible_decks}  # Top32占比
    
    # 对数转换（平滑数据）
    log1 = {d: math.log1p(v) for d, v in data1.items()}
    log2 = {d: math.log1p(v) for d, v in data2.items()}
    log3 = {d: math.log1p(v) for d, v in data3.items()}
    
    # 标准化（0~1）
    std1 = minmax_scale(log1)
    std2 = minmax_scale(log2)
    std3 = minmax_scale(log3)
    
    # 6. 计算综合得分与Tier等级
    tier_rows = []
    for d in eligible_decks:
        score = W1 * std1.get(d, 0.0) + W2 * std2.get(d, 0.0) + W3 * std3.get(d, 0.0)
        usage = deck_total_counts.get(d, 0) / total_entries_all if total_entries_all else 0.0
        tier_rows.append({
            "deck": d,
            "usage": usage,
            "total_samples": deck_total_counts.get(d, 0),
            "data1_top32_appearances": data1.get(d, 0.0),
            "data2_weighted_points": data2.get(d, 0.0),
            "data3_top32_share_pct": data3.get(d, 0.0),
            "log_data1": log1.get(d, 0.0),
            "log_data2": log2.get(d, 0.0),
            "log_data3": log3.get(d, 0.0),
            "std_data1": std1.get(d, 0.0),
            "std_data2": std2.get(d, 0.0),
            "std_data3": std3.get(d, 0.0),
            "score": score,
            "tier": tier_label(score),
        })
    # 按综合得分降序排序
    tier_rows.sort(key=lambda x: x["score"], reverse=True)
    
    # 7. 生成玩家排名（含出场次数）
    players = [
        {
            "player": p,
            "points": pts,
            "country": player_country.get(p, ""),
            "games": player_games.get(p, 0)  # 新增的出场次数字段
        }
        for p, pts in player_points.items()
    ]
    players.sort(key=lambda x: x["points"], reverse=True)
    
    # 8. 格式化胜率矩阵
    matchup_out = [
        {"deckA": a, "deckB": b, "winsA": w, "total": t, "winrateA": (w / t if t else None)}
        for (a, b), (w, t) in matchup.items()
    ]
    
    # 9. 生成元信息
    meta = {
        "generated_at": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
        "days_back": int(os.environ.get("DAYS_BACK", "14")),
        "min_players": MIN_PLAYERS,
        "usage_threshold": USAGE_THRESHOLD,
        "top_cut_n": TOP_CUT_N,
        "tournaments_count": len(tournaments),
        "total_entries_all": total_entries_all,
        "top32_total_slots": top32_total_slots,
        "weights": {"data1": W1, "data2": W2, "data3": W3},
        "tier_thresholds": {"S": 0.9, "A": 0.7, "B": 0.5, "C": 0.3, "D": 0.1},
    }
    
    # 10. 保存所有结果文件
    write_json("web/public/data/tier.json", tier_rows)
    write_json("web/public/data/players.json", players)
    write_json("web/public/data/matchups.json", matchup_out)
    write_json("web/public/data/meta.json", meta)
    
    print("统计分析完成！已生成：")
    print("- tier.json（牌组Tier数据）")
    print("- players.json（玩家排名，含出场次数）")
    print("- matchups.json（胜率矩阵）")
    print("- meta.json（统计元信息）")

if __name__ == "__main__":
    main()