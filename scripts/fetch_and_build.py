import shutil
import json, os, datetime, math, time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

BASE = "https://play.limitlesstcg.com/api"
GAME_ID = os.environ.get("POCKET_GAME_ID", "POCKET")

# 你可以調整抓取範圍/門檻
DAYS_BACK = int(os.environ.get("DAYS_BACK", "14"))
MIN_PLAYERS = int(os.environ.get("MIN_PLAYERS", "32"))

# Tier 參數
USAGE_THRESHOLD = float(os.environ.get("USAGE_THRESHOLD", "0.01"))  # 1% = 0.01
TOP_CUT_N = int(os.environ.get("TOP_CUT_N", "32"))                  # 取前 32
W1, W2, W3 = 0.4, 0.5, 0.1                                         # 權重

# 每次請求之間至少間隔幾秒（避免打太快）
REQUEST_GAP_SEC = float(os.environ.get("REQUEST_GAP_SEC", "0.35"))

# 429 最多重試幾次
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "8"))

_last_request_ts = 0.0

def get_json(url: str):
    global _last_request_ts

    for attempt in range(MAX_RETRIES + 1):
        # 節流：確保兩次 request 至少間隔 REQUEST_GAP_SEC
        now = time.time()
        wait = REQUEST_GAP_SEC - (now - _last_request_ts)
        if wait > 0:
            time.sleep(wait)

        req = Request(url, headers={"User-Agent": "ptcgp-tier-site/1.0"})
        try:
            with urlopen(req, timeout=60) as r:
                _last_request_ts = time.time()
                return json.loads(r.read().decode("utf-8"))

        except HTTPError as e:
            _last_request_ts = time.time()

            # 遇到 429：照 Retry-After 等，沒有就用 exponential backoff
            if e.code == 429:
                retry_after = e.headers.get("Retry-After")
                if retry_after:
                    sleep_s = float(retry_after)
                else:
                    sleep_s = min(60.0, 2.0 ** attempt)  # 1,2,4,8... capped at 60
                print(f"[429] Too Many Requests. Sleep {sleep_s:.1f}s then retry ({attempt+1}/{MAX_RETRIES})")
                time.sleep(sleep_s)
                continue

            # 其他 HTTP error 直接丟出
            raise

        except URLError:
            _last_request_ts = time.time()
            # 網路抖動也稍等一下再試
            sleep_s = min(30.0, 2.0 ** attempt)
            print(f"[URLError] Sleep {sleep_s:.1f}s then retry ({attempt+1}/{MAX_RETRIES})")
            time.sleep(sleep_s)
            continue

    raise RuntimeError(f"Failed to fetch after retries: {url}")

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def iso_to_date(s):
    return datetime.date.fromisoformat(s[:10])

def fetch_recent_tournaments():
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

def load_tournament_full(tid):
    details = get_json(f"{BASE}/tournaments/{tid}/details")
    standings = get_json(f"{BASE}/tournaments/{tid}/standings")
    pairings = get_json(f"{BASE}/tournaments/{tid}/pairings")
    return details, standings, pairings

def get_deck_id_from_standing(s):
    deck = s.get("deck")
    if deck and deck.get("id"):
        return deck["id"]
    return "unknown"

def points_by_placing(placing: int) -> int:
    # 你的數據2給分規則
    if placing == 1:
        return 10
    if placing == 2:
        return 8
    if 3 <= placing <= 4:
        return 6
    if 5 <= placing <= 8:
        return 4
    if 9 <= placing <= 16:
        return 2
    if 17 <= placing <= 32:
        return 1
    return 0

def minmax_scale(values_by_key: dict) -> dict:
    # values_by_key: {key: value}
    if not values_by_key:
        return {}
    vals = list(values_by_key.values())
    vmin, vmax = min(vals), max(vals)
    if vmax == vmin:
        return {k: 0.0 for k in values_by_key.keys()}
    return {k: (v - vmin) / (vmax - vmin) for k, v in values_by_key.items()}

def tier_label(score: float) -> str:
    if score >= 0.9: return "S"
    if score >= 0.7: return "A"
    if score >= 0.5: return "B"
    if score >= 0.3: return "C"
    if score >= 0.1: return "D"
    return "E"

def main():
    
    # ✅ 清掉舊 raw，避免歷史 PTCG/其他遊戲混入前端
    shutil.rmtree("web/src/data/raw", ignore_errors=True)

    tournaments = fetch_recent_tournaments()
    write_json("web/src/data/tournaments.json", tournaments)

    # --- 全部牌組出場（用來算使用率>=1%）---
    deck_total_counts = {}  # deck -> total appearances in standings
    total_entries_all = 0

    # --- Top 32 統計（用來算數據1、數據2、數據3）---
    deck_top32_counts = {}     # deck -> data1
    deck_weighted_points = {}  # deck -> data2
    top32_total_slots = 0      # denominator for data3 (all decks, all events)

    # --- 玩家排名（我用同一套名次給分）---
    player_points = {}         # player -> points

    # --- 勝率矩陣 ---
    matchup = {}               # (deckA, deckB) -> (winsA, total)

    for t in tournaments:
        tid = t["id"]
        details, standings, pairings = load_tournament_full(tid)

        # ✅ 只保留 Pocket
        game = str(details.get("game", "")).upper()
        if game != "POCKET":
            print(f"[skip] tid={tid} details.game={details.get('game')}")
        continue

        # 存 raw（方便你除錯）
        write_json(f"web/src/data/raw/{tid}/details.json", details)
        write_json(f"web/src/data/raw/{tid}/standings.json", standings)
        write_json(f"web/src/data/raw/{tid}/pairings.json", pairings)     

        # 建 player->deck 對照（勝率矩陣用）
        p2deck = {}
        for s in standings:
            p2deck[s["player"]] = get_deck_id_from_standing(s)

        # 先更新「全部使用率」統計
        for s in standings:
            deck = get_deck_id_from_standing(s)
            if deck == "unknown":
                continue
            deck_total_counts[deck] = deck_total_counts.get(deck, 0) + 1
            total_entries_all += 1

        # Top 32（placing <= 32）
        for s in standings:
            placing = s.get("placing")
            if not placing:
                continue
            if placing > TOP_CUT_N:
                continue

            deck = get_deck_id_from_standing(s)
            if deck == "unknown":
                continue

            # 數據1：Top 32 登場數
            deck_top32_counts[deck] = deck_top32_counts.get(deck, 0) + 1
            top32_total_slots += 1

            # 數據2：加權數（依名次給分）
            pts = points_by_placing(int(placing))
            deck_weighted_points[deck] = deck_weighted_points.get(deck, 0) + pts

            # 玩家排名：同套給分
            player = s["player"]
            player_points[player] = player_points.get(player, 0) + pts

        # 勝率矩陣：用 pairings winner + 玩家 deck
        for m in pairings:
            p1, p2 = m.get("player1"), m.get("player2")
            winner = m.get("winner")
            if not p1 or not p2:
                continue
            if winner in (0, -1, None):
                continue

            d1, d2 = p2deck.get(p1, "unknown"), p2deck.get(p2, "unknown")
            if d1 == "unknown" or d2 == "unknown":
                continue

            # A vs B
            w, tot = matchup.get((d1, d2), (0, 0))
            tot += 1
            if winner == p1:
                w += 1
            matchup[(d1, d2)] = (w, tot)

            # B vs A（方便做矩陣）
            w, tot = matchup.get((d2, d1), (0, 0))
            tot += 1
            if winner == p2:
                w += 1
            matchup[(d2, d1)] = (w, tot)

    # --- 依「使用率>=1%」篩選牌組 ---
    if total_entries_all == 0:
        eligible_decks = []
    else:
        eligible_decks = [
            d for d, c in deck_total_counts.items()
            if (c / total_entries_all) >= USAGE_THRESHOLD
        ]

    # --- 數據1/2/3 計算（只保留 eligible）---
    data1 = {d: float(deck_top32_counts.get(d, 0)) for d in eligible_decks}
    data2 = {d: float(deck_weighted_points.get(d, 0)) for d in eligible_decks}
    if top32_total_slots > 0:
        data3 = {d: (data1[d] / top32_total_slots) * 100.0 for d in eligible_decks}
    else:
        data3 = {d: 0.0 for d in eligible_decks}

    # --- Log（用 log1p 避免 0 問題）---
    log1 = {d: math.log1p(v) for d, v in data1.items()}
    log2 = {d: math.log1p(v) for d, v in data2.items()}
    log3 = {d: math.log1p(v) for d, v in data3.items()}

    # --- 標準化（min-max）---
    std1 = minmax_scale(log1)
    std2 = minmax_scale(log2)
    std3 = minmax_scale(log3)

    # --- 綜合分數 + Tier ---
    tier_rows = []
    for d in eligible_decks:
        score = W1 * std1.get(d, 0.0) + W2 * std2.get(d, 0.0) + W3 * std3.get(d, 0.0)
        usage = deck_total_counts.get(d, 0) / total_entries_all if total_entries_all else 0.0
        tier_rows.append({
            "deck": d,

            # 使用率篩選用（也方便你畫 usage bar）
            "usage": usage,
            "total_samples": deck_total_counts.get(d, 0),

            # 你的三個數據（原始）
            "data1_top32_appearances": data1.get(d, 0.0),
            "data2_weighted_points": data2.get(d, 0.0),
            "data3_top32_share_pct": data3.get(d, 0.0),

            # log 後
            "log_data1": log1.get(d, 0.0),
            "log_data2": log2.get(d, 0.0),
            "log_data3": log3.get(d, 0.0),

            # 標準化後
            "std_data1": std1.get(d, 0.0),
            "std_data2": std2.get(d, 0.0),
            "std_data3": std3.get(d, 0.0),

            # 綜合分數與等級
            "score": score,
            "tier": tier_label(score),
        })

    tier_rows.sort(key=lambda x: x["score"], reverse=True)

    # 玩家排名
    players = [{"player": p, "points": pts} for p, pts in player_points.items()]
    players.sort(key=lambda x: x["points"], reverse=True)

    # 勝率矩陣輸出
    matchup_out = [
        {"deckA": a, "deckB": b, "winsA": w, "total": t, "winrateA": (w / t if t else None)}
        for (a, b), (w, t) in matchup.items()
    ]

    # 輸出
    write_json("web/src/data/tier.json", tier_rows)
    write_json("web/src/data/players.json", players)
    write_json("web/src/data/matchups.json", matchup_out)

    # 輸出一些全域資訊（可用來顯示「本期統計了幾場、多少Top32樣本」）
    meta = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "days_back": DAYS_BACK,
        "min_players": MIN_PLAYERS,
        "usage_threshold": USAGE_THRESHOLD,
        "top_cut_n": TOP_CUT_N,
        "tournaments_count": len(tournaments),
        "total_entries_all": total_entries_all,
        "top32_total_slots": top32_total_slots,
        "weights": {"data1": W1, "data2": W2, "data3": W3},
        "tier_thresholds": {"S": 0.9, "A": 0.7, "B": 0.5, "C": 0.3, "D": 0.1},
    }
    write_json("web/src/data/meta.json", meta)

if __name__ == "__main__":
    main()
