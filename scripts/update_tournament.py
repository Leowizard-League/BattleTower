import json
from pathlib import Path
from datetime import datetime

# ===================== 核心修改点1：调整基准路径 =====================
# 脚本位于 scripts/ 目录下，基准路径改为「项目根目录」（scripts的上级目录）
# 这样才能正确定位到 web/ 目录
BASE_DIR = Path(__file__).resolve().parent  # 原：Path(__file__).resolve().parent
# 赛事主文件路径（如果 tournaments.json 也需要调整，可同步修改，当前保留原逻辑）
TOURNAMENTS_FILE = BASE_DIR / "web/public/data/tournaments.json"  

# ===================== 核心修改点2：修改 RAW_DIR 路径 =====================
# 从 web/public/data/raw 读取原始赛事详情
RAW_DIR = BASE_DIR / "web/public/data/raw"  # 原：BASE_DIR / "raw"

# ===================== 核心修改点3：定义游戏版本文件路径 =====================
# 从 web/public/data/game_version.json 读取版本数据
GAME_VERSION_FILE = BASE_DIR / "web/public/data/game_version.json"


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iso_to_ms(iso_str):
    if not iso_str:
        return None
    s = str(iso_str).strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return int(datetime.fromisoformat(s).timestamp() * 1000)


# ===================== 核心修改点4：加载游戏版本（从文件读取） =====================
# 读取 game_version.json 并处理版本数据
GAME_VERSIONS = load_json(GAME_VERSION_FILE, default=[])
# 校验版本数据格式（可选，增强鲁棒性）
if not isinstance(GAME_VERSIONS, list):
    raise ValueError(f"{GAME_VERSION_FILE} 内容不是数组格式")

# 为每个版本补充毫秒时间戳、排序、生成编码映射（保留原逻辑）
for v in GAME_VERSIONS:
    v["releaseMs"] = iso_to_ms(v.get("releaseUtcIso"))

GAME_VERSIONS.sort(key=lambda v: v["releaseMs"] or 0)  # 兼容空值
VERSION_BY_CODE = {v["code"]: v for v in GAME_VERSIONS if "code" in v}  # 兼容缺失code的情况


def infer_version_code(date_iso):
    ms = iso_to_ms(date_iso)
    if ms is None:
        return None

    matched = None
    for v in GAME_VERSIONS:
        if ms >= (v["releaseMs"] or 0):
            matched = v
        else:
            break

    return matched["code"] if matched else None


def normalize_format(row_format, details_format, name=""):
    raw = details_format if details_format is not None else row_format
    s = str(raw or "").strip().upper()

    if s in {"NOEX", "NO_EX", "NO-EX"}:
        return "NOEX"
    if s in {"CUSTOM", "SPECIAL"}:
        return "CUSTOM"
    if s == "STANDARD":
        return "STANDARD"

    # 若原始 format 為 null，預設當 STANDARD
    n = (name or "").upper()
    if any(x in n for x in ["NOEX", "NO EX", "NO-EX", "NO_EX"]):
        return "NOEX"

    return "STANDARD"


def find_phase_mode(details: dict, phase_type: str):
    phases = details.get("phases") or []
    for phase in phases:
        if str(phase.get("type", "")).upper() == phase_type.upper():
            mode = phase.get("mode")
            if mode:
                return str(mode).upper()
    return None


def enrich_tournaments():
    print("BASE_DIR =", BASE_DIR)
    print("TOURNAMENTS_FILE =", TOURNAMENTS_FILE)
    print("RAW_DIR =", RAW_DIR)
    print("GAME_VERSION_FILE =", GAME_VERSION_FILE)  # 新增：打印版本文件路径（调试用）

    tournaments = load_json(TOURNAMENTS_FILE, default=[])
    if not isinstance(tournaments, list):
        raise ValueError("tournaments.json 不是陣列")

    out = []

    for row in tournaments:
        tid = str(row.get("id", "")).strip()
        if not tid:
            out.append(row)
            continue

        details_path = RAW_DIR / tid / "details.json"
        details = load_json(details_path, default={}) or {}

        name = details.get("name") or row.get("name") or ""
        date_iso = details.get("date") or row.get("date")

        swiss = find_phase_mode(details, "SWISS")
        top_cut = find_phase_mode(details, "SINGLE_ELIMINATION")
        fmt = normalize_format(
            row.get("format"),
            details.get("format"),
            name=name,
        )
        set_code = infer_version_code(date_iso)

        new_row = dict(row)
        new_row["format"] = fmt
        new_row["swiss"] = swiss
        new_row["topCut"] = top_cut
        new_row["set"] = set_code

        # 如果你之後想前端直接顯示中文名，也可以保留這兩個
        if set_code and set_code in VERSION_BY_CODE:
            new_row["setNameZh"] = VERSION_BY_CODE[set_code].get("nameZh")
            new_row["setNameEn"] = VERSION_BY_CODE[set_code].get("nameEn")
        else:
            new_row["setNameZh"] = None
            new_row["setNameEn"] = None

        out.append(new_row)

    # 備份原本 tournaments.json
    backup_file = BASE_DIR / "tournaments.backup.json"
    if TOURNAMENTS_FILE.exists():
        backup_file.write_text(
            TOURNAMENTS_FILE.read_text(encoding="utf-8"),
            encoding="utf-8"
        )
        print(f"backup created: {backup_file}")

    with TOURNAMENTS_FILE.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"done: updated {len(out)} tournaments -> {TOURNAMENTS_FILE}")


if __name__ == "__main__":
    enrich_tournaments()
