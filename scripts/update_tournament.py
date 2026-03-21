import json
import os  # 新增：用于创建目录（可选增强）
from pathlib import Path
from datetime import datetime

# ===================== 核心修正：基准路径指向项目根目录 =====================
# 脚本路径：BattleTower/scripts/xxx.py
# Path(__file__).resolve() → 脚本文件的绝对路径
# .parent → scripts 目录
# .parent.parent → BattleTower 根目录（正确基准路径）
BASE_DIR = Path(__file__).resolve().parent.parent  

# 以下路径基于根目录拼接，完全匹配你的目录结构
TOURNAMENTS_FILE = BASE_DIR / "web/public/data/tournaments.json"  
RAW_DIR = BASE_DIR / "web/public/data/raw"  
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


# 加载游戏版本数据
GAME_VERSIONS = load_json(GAME_VERSION_FILE, default=[])
if not isinstance(GAME_VERSIONS, list):
    raise ValueError(f"{GAME_VERSION_FILE} 内容不是数组格式")

for v in GAME_VERSIONS:
    v["releaseMs"] = iso_to_ms(v.get("releaseUtcIso"))

GAME_VERSIONS.sort(key=lambda v: v["releaseMs"] or 0)
VERSION_BY_CODE = {v["code"]: v for v in GAME_VERSIONS if "code" in v}


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
    # 调试打印：确认路径是否正确（运行时可看输出）
    print("✅ 项目根目录:", BASE_DIR)
    print("✅ 赛事文件路径:", TOURNAMENTS_FILE)
    print("✅ 原始数据目录:", RAW_DIR)

    # 可选增强：自动创建不存在的目录（避免GitHub Action中因目录缺失报错）
    os.makedirs(TOURNAMENTS_FILE.parent, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)

    # 读取赛事主文件
    tournaments = load_json(TOURNAMENTS_FILE, default=[])
    if not isinstance(tournaments, list):
        raise ValueError("tournaments.json 不是数组格式")

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

        if set_code and set_code in VERSION_BY_CODE:
            new_row["setNameZh"] = VERSION_BY_CODE[set_code].get("nameZh")
            new_row["setNameEn"] = VERSION_BY_CODE[set_code].get("nameEn")
        else:
            new_row["setNameZh"] = None
            new_row["setNameEn"] = None

        out.append(new_row)

    # 备份原文件
    backup_file = BASE_DIR / "tournaments.backup.json"
    if TOURNAMENTS_FILE.exists():
        backup_file.write_text(
            TOURNAMENTS_FILE.read_text(encoding="utf-8"),
            encoding="utf-8"
        )
        print(f"📝 已备份原文件: {backup_file}")

    # 写入更新后的数据
    with TOURNAMENTS_FILE.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"✅ 完成更新：共处理 {len(out)} 条赛事数据 → {TOURNAMENTS_FILE}")


if __name__ == "__main__":
    enrich_tournaments()
