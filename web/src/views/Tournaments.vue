<template>
  <div class="page">
    <div class="header">
      <div>
        <div class="title">{{ ui.title }}</div>
        <div class="sub">
          {{ ui.subtitle(filtered.length) }}
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="f">
        <label>{{ isZh ? "玩家數" : "Players " }}</label>
        <input
          v-model.number="filters.minPlayers"
          type="number"
          inputmode="numeric"
          min="0"
          :placeholder="isZh ? '例如 32' : 'e.g： 32'"
        />
        <div class="hint">{{ isZh ? "多於或等於（>=）" : "More than or equal to (>=)" }}</div>
      </div>

      <div class="f">
        <label>{{ isZh ? "日期" : "Time" }}</label>
        <select v-model="filters.time">
          <option value="past7">{{ isZh ? "過去一週" : "Past 7 days" }}</option>
          <option value="past4w">{{ isZh ? "過去一月" : "Past 4 weeks" }}</option>
          <optgroup :label="isZh ? '月份' : 'Month'">
            <option v-for="m in monthOptions" :key="m.value" :value="m.value">
              {{ m.label }}
            </option>
          </optgroup>
        </select>
        <div class="hint">{{ isZh ? "以 UTC 日期計算" : "Based on UTC date" }}</div>
      </div>

      <div class="f">
        <label>{{ isZh ? "版本" : "Set" }}</label>
        <select v-model="filters.set">
          <option value="">{{ isZh ? "全部" : "All" }}</option>
<option v-for="s in setOptions" :key="s" :value="s">
  {{ versionLabel(s) }}
</option>
        </select>
        <div class="hint">{{ isZh ? " " : " " }}</div>
      </div>

      <div class="f">
        <label>{{ isZh ? "瑞士輪" : "SWISS" }}</label>
        <select v-model="filters.swiss">
          <option value="">{{ isZh ? "全部" : "All" }}</option>
          <option value="BO1">BO1</option>
          <option value="BO3">BO3</option>
          <option value="Other">Other</option>
        </select>
        <div class="hint">{{ isZh ? " " : " " }}</div>
      </div>

      <div class="f">
        <label>{{ isZh ? "賽制" : "Format" }}</label>
        <select v-model="filters.format">
          <option value="">{{ isZh ? "全部" : "All" }}</option>
          <option value="Standard">{{ isZh ? "標準" : "Standard" }}</option>
          <option value="NoEX">{{ isZh ? "沒有EX" : "NoEX" }}</option>
          <option value="Special">{{ isZh ? "特殊" : "Special" }}</option>
        </select>
        <div class="hint">{{ isZh ? " " : " " }}</div>
      </div>
    </div>

    <!-- Pager -->
<div class="pager">
  <div class="pager__left">
    <div class="pager__label">{{ isZh ? "每頁顯示" : "Per page" }}</div>

    <div class="pager__sizes" role="group" :aria-label="isZh ? '每頁筆數' : 'Rows per page'">
      <button

        v-for="n in PAGE_SIZES"
        :key="n"
        type="button"
        :class="['pagerBtn', pageSize === n ? 'is-active' : '']"
        :aria-pressed="pageSize === n"
        @click="setPageSize(n)"
      >
        {{ n }}

      </button>
    </div>

    <div class="pager__summary mono muted">
      <template v-if="total > 0">
        {{ isZh ? `顯示第 ${rangeStart}–${rangeEnd} 筆 / 共 ${total} 筆` : `Showing ${rangeStart}–${rangeEnd} of ${total}` }}
      </template>
      <template v-else>
        {{ isZh ? "共 0 筆" : "0 results" }}
      </template>
    </div>
  </div>

  <div class="pager__right">
    <button class="pagerNav" type="button" @click="prevPage" :disabled="page <= 1">
      {{ isZh ? "上一頁" : "Prev" }}
    </button>

    <div class="pager__page mono">
      {{ isZh ? `第 ${page} / ${pageCount} 頁` : `Page ${page} / ${pageCount}` }}
    </div>

    <button class="pagerNav" type="button" @click="nextPage" :disabled="page >= pageCount">
      {{ isZh ? "下一頁" : "Next" }}
    </button>
  </div>
</div>

    <!-- Table -->
    <div class="tableWrap">
      <table class="tbl">
        <thead>
          <tr>
            <th class="date">
              {{ isZh ? "日期" : "Date" }}
            </th>

            <th>
              {{ isZh ? "賽事" : "Name" }}
            </th>

            <th class="num">
              {{ isZh ? "人數" : "Players" }}
            </th>

            <th class="top4">
              {{ isZh ? "前四名牌組" : "Top 4 Decks" }}<br />
              <span class="muted">
                {{ isZh ? " " : " " }}
              </span>
            </th>

            <th class="link">
              {{ isZh ? "排位" : "Standings" }}
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="t in paged" :key="t.id">
            <td class="mono muted">
              {{ t.dateStr }}
            </td>

            <td>
              <div class="nameCell">
                <div class="nameMain">{{ t.name }}</div>
                <div class="nameMeta muted">
                  <button
                    v-if="t.set"
                    type="button"
                    :class="['pill', 'pill--btn', filters.set === t.set ? 'pill--active' : '']"
                    :aria-pressed="filters.set === t.set"
                    @click="toggleSet(t.set)"
                    :title="isZh ? '點擊篩選：Set' : 'Click to filter: Set'"
                  >
                    {{ versionLabel(t.set) }}
                  </button>

                  <button
                    v-if="t.format"
                    type="button"
                    :class="['pill', 'pill--btn', filters.format === t.format ? 'pill--active' : '']"
                    :aria-pressed="filters.format === t.format"
                    @click="toggleFormat(t.format)"
                    :title="isZh ? '點擊篩選：Format' : 'Click to filter: Format'"
                  >
                    {{ formatLabelForUi(t.format) }}
                  </button>

                  <button
                    v-if="t.swiss"
                    type="button"
                    :class="['pill', 'pill--btn', filters.swiss === t.swiss ? 'pill--active' : '']"
                    :aria-pressed="filters.swiss === t.swiss"
                    @click="toggleSwiss(t.swiss)"
                    :title="isZh ? '點擊篩選：Swiss' : 'Click to filter: Swiss'"
                  >
                    {{ t.swiss }}
                  </button>
                </div>
              </div>
            </td>

            <td class="num mono">{{ t.players ?? "—" }}</td>

            <td>
              <div v-if="t.topDecks.length" class="topDecksGrid" :aria-label="ui.top4AriaLabel">
                <div
                  v-for="(d, i) in t.topDecks"
                  :key="i"
                  class="deckPair"
                  :title="deckPairTitle(d, i + 1)"
                >
<div class="deckIconsWrap">
  <div class="deckIconsRow">
    <template v-for="slot in 2" :key="slot">
      <img
        v-if="d.iconUrls[slot - 1]"
        :class="['deckIcon', slot === 2 ? 'deckIcon--second' : '']"
        :src="d.iconUrls[slot - 1]!"
        :alt="deckAlt(i + 1, slot)"
        loading="lazy"
        decoding="async"
        draggable="false"
      />

      <span
        v-else-if="d.iconKeys[slot - 1]"
        :class="['deckIconFallback', slot === 2 ? 'deckIconFallback--second' : '']"
        aria-hidden="true"
        :title="missingIconTitle(d.iconKeys[slot - 1], i + 1, slot)"
      ></span>

      <template v-else></template>
    </template>
  </div>

  <img
    class="deckDisk"
    :src="resolveDeckDiskUrl(getDeckDiskKind(i + 1))"
    alt=""
    aria-hidden="true"
    draggable="false"
  />
</div>


                </div>
              </div>
              <span v-else class="muted">—</span>
            </td>

            <td class="link">
              <a
                class="linkDot"
                :href="t.standingsUrl"
                target="_blank"
                rel="noreferrer"
                :title="ui.standingsTitle"
                :aria-label="ui.standingsTitle"
              >
                ↗
              </a>
            </td>
          </tr>

          <tr v-if="filtered.length === 0">
            <td class="muted" colspan="5" style="padding: 16px;">
              {{ ui.emptyText }}
              <span class="mono">web/src/data/raw/*</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="foot muted mono">
      {{ ui.footText }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { computed, reactive, ref, watch } from "vue";


function toggleSet(set?: string) {
  if (!set) return;
  filters.set = filters.set === set ? "" : set;
}

function toggleSwiss(s?: SwissLabel) {
  if (!s) return;
  filters.swiss = filters.swiss === s ? "" : s;
}

function toggleFormat(f?: "Standard" | "NoEX" | "Special" | string) {
  // 你的 filters.format 只接受這三種；其它值就忽略
  if (f !== "Standard" && f !== "NoEX" && f !== "Special") return;
  filters.format = filters.format === f ? "" : f;
}

type FormatLabel = "Standard" | "NoEX" | "Special";

/**
 * 規則：
 * - null / undefined / "STANDARD" => Standard
 * - "NOEX" => NoEX
 * - "CUSTOM" => Special
 * - 其他看不懂的 => undefined（不顯示、不參與 filter）
 */
function formatFromDetails(details: any): FormatLabel | undefined {
  const raw = details?.format;

  if (raw == null) return "Standard";

  const s = String(raw).trim().toUpperCase();

  if (s === "" || s === "STANDARD") return "Standard";
  if (s === "NOEX") return "NoEX";
  if (s === "CUSTOM") return "Special";

  return undefined;
}

function formatLabelForUi(f?: FormatLabel | string) {
  if (!f) return "—";
  if (f === "NoEX") return "NoEX"; // 你說 NOEX 不分中英文

  if (isZh.value) {
    if (f === "Standard") return "標準";
    if (f === "Special") return "特殊";
  } else {
    if (f === "Standard") return "Standard";
    if (f === "Special") return "Special";
  }
  return String(f);
}

function swissLabelFromDetails(details: any): SwissLabel {
  const phases = Array.isArray(details?.phases) ? details.phases : [];

  // Phase 1：優先找 phase===1；找不到就退回用第一個
  const p1 = phases.find((p: any) => p?.phase === 1) ?? phases[0];

  const p1Type = String(p1?.type ?? "").toUpperCase();
  const p1Mode = String(p1?.mode ?? "").toUpperCase();

  // 你的規則：Other 只看 Phase 1
  if (p1Type !== "SWISS") return "Other";
  if (p1Mode === "BO1") return "BO1";
  if (p1Mode === "BO3") return "BO3";
  return "Other";
}


// 讀取 src/assets/deck-disks 內所有 png
const diskFiles = import.meta.glob('../assets/deck-disks/*.png', {
  eager: true,
  import: 'default',
}) as Record<string, string>;

const DISK_NAME: Record<string, string> = {
  gold: 'disk-gold.png',
  silver: 'disk-silver.png',
  bronze: 'disk-bronze.png',
  neutral: 'disk-neutral.png',
};

function resolveDeckDiskUrl(kind: 'gold' | 'silver' | 'bronze' | 'neutral' = 'neutral') {
  const file = DISK_NAME[kind] ?? DISK_NAME.neutral;
  const hit = Object.entries(diskFiles).find(([path]) => path.endsWith(`/${file}`));
  return hit?.[1];
}

// 先用「位置」做預設：每列第一個金，其它銀（符合你截圖的感覺）
// 之後你若有 place / rank 欄位，再改這裡就好
function getDeckDiskKind(rank: number): 'gold' | 'silver' | 'neutral' {
  if (rank === 1) return 'gold';
  if (rank === 2) return 'silver';
  return 'neutral';
}

/**
 * 讀取 raw 資料夾內的 details / standings
 * 注意：路徑以本檔案位置（src/views）為基準
 */
const detailsModules = import.meta.glob("../data/raw/*/details.json", {
  eager: true,
}) as Record<string, any>;

const standingsModules = import.meta.glob("../data/raw/*/standings.json", {
  eager: true,
}) as Record<string, any>;

/**
 * 讀取本地 deck icon（你自己放的 png/webp/svg）
 * 你可以建立：web/src/assets/deck-icons/<key>.png
 */
const deckIconModules = import.meta.glob("../assets/deck-icons/*.{png,webp,svg}", {
  eager: true,
  import: "default",
}) as Record<string, string>;

type SwissLabel = "BO1" | "BO3" | "Other";

type TopDeck = {
  // 兩個 icon key：主力/副手（或你希望的兩個代表）
  iconKeys: (string | undefined)[];
  iconUrls: (string | undefined)[];
};

type TournamentRow = {
  id: string;
  dateISO?: string; // YYYY-MM-DD
  dateMs?: number;  // for sorting/filtering
  dateStr: string;  // display
  name: string;
  players?: number;

  set?: string;     // e.g. A1, B2a ...
  format?: "Standard" | "NoEX" | "Special" | string;
  swiss?: SwissLabel;

  topDecks: TopDeck[]; // top 4，每個 2 icons

  standingsUrl: string;
};

const route = useRoute();

const lang = computed<"zh" | "en">(() => {
  const seg = String(route.path).split("/")[1];
  return seg === "en" ? "en" : "zh";
});

const isZh = computed(() => lang.value === "zh");

const ui = computed(() => {
  if (isZh.value) {
    return {
      title: "賽事",
      subtitle: (n: number) => `共 ${n} 場（資料源：web/src/data/raw/*）`,
      standingsTitle: "查看 standings",
      emptyText: "沒有符合條件的賽事。請調整 filters，或確認 raw 資料是否存在於 ",
      footText:
        " ",
      top4AriaLabel: "前四名牌組（每副2圖）",
    };
  }
  return {
    title: "Tournaments",
    subtitle: (n: number) => `Total ${n} tournaments (source: web/src/data/raw/*)`,
    standingsTitle: "Open standings",
    emptyText:
      "No tournaments match your filters. Adjust filters or make sure raw data exists in ",
    footText:
      "tips: If icons don’t show up, make sure standings provides 2 keys per deck (deckIconKeys / deckIconKeyMain&Sub, or a deckIconKey that can be split) matching filenames in assets/deck-icons.",
    top4AriaLabel: "Top 4 decks (2 icons each)",
  };
});

function deckAlt(rank: number, slot: number) {
  if (isZh.value) return `第${rank}名牌組 第${slot}圖`;
  return `Top ${rank} deck icon ${slot}`;
}

type GameVersionCode =
  | "A1" | "A1a" | "A2" | "A2a" | "A2b"
  | "A3" | "A3a" | "A3b" | "A4" | "A4a" | "A4b"
  | "B1" | "B1a" | "B2" | "B2a";

type GameVersion = {
  code: GameVersionCode;
  nameZh: string;
  nameEn: string;
  releaseUtcIso: string; // ISO string in UTC
  releaseMs: number;     // Date.parse(releaseUtcIso)
};

const GAME_VERSIONS = [
  { code: "A1",  nameZh: "最強的基因",   nameEn: "Genetic Apex",           releaseUtcIso: "2024-10-30T01:00:00Z", releaseMs: Date.parse("2024-10-30T01:00:00Z") },
  { code: "A1a", nameZh: "幻遊島",       nameEn: "Mythical Island",        releaseUtcIso: "2024-12-17T06:00:00Z", releaseMs: Date.parse("2024-12-17T06:00:00Z") },
  { code: "A2",  nameZh: "時空激鬥",     nameEn: "Space-Time Smackdown",   releaseUtcIso: "2025-01-30T06:00:00Z", releaseMs: Date.parse("2025-01-30T06:00:00Z") },
  { code: "A2a", nameZh: "超克之光",     nameEn: "Triumphant Light",       releaseUtcIso: "2025-02-28T06:00:00Z", releaseMs: Date.parse("2025-02-28T06:00:00Z") },
  { code: "A2b", nameZh: "嗨放異彩",     nameEn: "Shining Revelry",        releaseUtcIso: "2025-03-27T06:00:00Z", releaseMs: Date.parse("2025-03-27T06:00:00Z") },
  { code: "A3",  nameZh: "雙天之守護者", nameEn: "Celestial Guardians",    releaseUtcIso: "2025-04-30T06:00:00Z", releaseMs: Date.parse("2025-04-30T06:00:00Z") },
  { code: "A3a", nameZh: "異次元危機",   nameEn: "Extradimensional Crisis",releaseUtcIso: "2025-05-29T06:00:00Z", releaseMs: Date.parse("2025-05-29T06:00:00Z") },
  { code: "A3b", nameZh: "伊布花園",     nameEn: "Eevee Grove",            releaseUtcIso: "2025-06-26T06:00:00Z", releaseMs: Date.parse("2025-06-26T06:00:00Z") },
  { code: "A4",  nameZh: "天與海的指引", nameEn: "Wisdom of Sea and Sky",  releaseUtcIso: "2025-07-30T06:00:00Z", releaseMs: Date.parse("2025-07-30T06:00:00Z") },
  { code: "A4a", nameZh: "未知水域",     nameEn: "Secluded Springs",       releaseUtcIso: "2025-08-28T06:00:00Z", releaseMs: Date.parse("2025-08-28T06:00:00Z") },
  { code: "A4b", nameZh: "高級擴充包ex", nameEn: "Deluxe Pack: ex",        releaseUtcIso: "2025-09-30T06:00:00Z", releaseMs: Date.parse("2025-09-30T06:00:00Z") },
  { code: "B1",  nameZh: "超級崛起",     nameEn: "Mega Rising",            releaseUtcIso: "2025-10-30T06:00:00Z", releaseMs: Date.parse("2025-10-30T06:00:00Z") },
  { code: "B1a", nameZh: "紅蓮烈焰",     nameEn: "Crimson Blaze",          releaseUtcIso: "2025-12-17T06:00:00Z", releaseMs: Date.parse("2025-12-17T06:00:00Z") },
  { code: "B2",  nameZh: "幻夢遊行",     nameEn: "Fantastical Parade",     releaseUtcIso: "2026-01-29T01:00:00Z", releaseMs: Date.parse("2026-01-29T01:00:00Z") },
  { code: "B2a", nameZh: "帕底亞驚奇",   nameEn: "Paldean Wonders",        releaseUtcIso: "2026-02-26T01:00:00Z", releaseMs: Date.parse("2026-02-26T01:00:00Z") },
].sort((a, b) => a.releaseMs - b.releaseMs) as GameVersion[];

const VERSION_BY_CODE: Record<string, GameVersion> = Object.fromEntries(
  GAME_VERSIONS.map((v) => [v.code, v])
);

function inferVersionByStartMs(startMs?: number): GameVersion | undefined {
  if (!startMs) return undefined;
  let cur: GameVersion | undefined;
  for (const v of GAME_VERSIONS) {
    if (startMs >= v.releaseMs) cur = v;
    else break;
  }
  return cur;
}

function versionLabel(code?: string) {
  if (!code) return "—";
  const v = VERSION_BY_CODE[code];
  if (!v) return code;
  return isZh.value ? `${v.code} - ${v.nameZh}` : `${v.code} - ${v.nameEn}`;
}

// 給 filter 下拉用（新到舊）


const setOptions = computed(() => GAME_VERSIONS.map(v => v.code).reverse());

const filters = reactive({
  minPlayers: undefined as number | undefined,
  time: "past7" as string, // past7 | past4w | month:YYYY-MM
  set: "" as string,
  swiss: "" as "" | SwissLabel,
  format: "" as "" | "Standard" | "NoEX" | "Special",
});

function extractIdFromPath(p: string) {
  // .../raw/<id>/details.json
  const m = p.match(/\/raw\/([^/]+)\/details\.json$/);
  return m?.[1] ?? "";
}

function toUtcDateMs(dateLike: any): number | undefined {
  if (!dateLike) return undefined;
  if (typeof dateLike === "number") return dateLike;
  const s = String(dateLike);

  // YYYY-MM-DD → UTC 00:00
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return Date.parse(s + "T00:00:00Z");

  const ms = Date.parse(s);
  return Number.isFinite(ms) ? ms : undefined;
}

function formatUtcYmd(ms?: number) {
  if (!ms) return "—";
  const d = new Date(ms);
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function normalizeSwiss(details: any): SwissLabel | undefined {
  const bestOf =
    details?.bestOf ??
    details?.swiss?.bestOf ??
    details?.swissBestOf ??
    details?.bo ??
    details?.matchBestOf;

  if (bestOf === 1 || String(bestOf).toLowerCase() === "bo1") return "BO1";
  if (bestOf === 3 || String(bestOf).toLowerCase() === "bo3") return "BO3";

  const text = String(details?.swiss ?? details?.rounds ?? details?.rules ?? "").toLowerCase();
  if (text.includes("bo1")) return "BO1";
  if (text.includes("bo3")) return "BO3";

  return bestOf != null ? "Other" : undefined;
}

// -------- icon resolving (more robust) --------
function normalizeKeyForMatch(k: string) {
  // 小寫 + 去掉非英數（讓 garchomp-ex / Garchomp EX / garchomp_ex 都能對上）
  return k.toLowerCase().replace(/[^a-z0-9]/g, "");
}

function getBasenameNoExt(p: string) {
  const file = p.split("/").pop() ?? p;
  return file.replace(/\.(png|webp|svg)$/i, "");
}

// 建立一個「normalized basename」→ url 的索引
const deckIconIndex: Record<string, string> = (() => {
  const idx: Record<string, string> = {};
  for (const [path, url] of Object.entries(deckIconModules)) {
    const base = getBasenameNoExt(path);
    const nk = normalizeKeyForMatch(base);
    if (nk && !idx[nk]) idx[nk] = url;
  }
  return idx;
})();

function resolveDeckIconUrl(key?: string) {
  if (!key) return undefined;

  // 先試原本精準路徑（大小寫都試）
  const candidates = [
    `../assets/deck-icons/${key}.png`,
    `../assets/deck-icons/${key}.webp`,
    `../assets/deck-icons/${key}.svg`,
    `../assets/deck-icons/${String(key).toLowerCase()}.png`,
    `../assets/deck-icons/${String(key).toLowerCase()}.webp`,
    `../assets/deck-icons/${String(key).toLowerCase()}.svg`,
  ];
  for (const p of candidates) {
    if (deckIconModules[p]) return deckIconModules[p];
  }

  // 再用「normalized basename」對檔名
  const nk = normalizeKeyForMatch(String(key));
  return deckIconIndex[nk];
}

function parseTwoFromDeckId(deckId?: string): (string | undefined)[] {
  if (!deckId) return [undefined, undefined];

  // e.g. "suicune-ex-a4a-greninja-ex-b1"
  const tokens = String(deckId).toLowerCase().split("-").filter(Boolean);

  // set token examples: a1, a2a, a4b, b1, b2a ...
  const isSetToken = (t: string) => /^[ab]\d+[a-z]?$/.test(t);

  const mons: string[] = [];
  let cur: string[] = [];

  for (const t of tokens) {
    if (isSetToken(t)) {
      if (cur.length) mons.push(cur.join("-"));
      cur = [];
      continue;
    }
    cur.push(t);
  }
  if (cur.length) mons.push(cur.join("-"));

  // mons should look like ["suicune-ex", "greninja-ex"]
  return [mons[0], mons[1]];
}

function parseTwoFromDeckName(deckName?: string): (string | undefined)[] {
  if (!deckName) return [undefined, undefined];

  // e.g. "Suicune ex Greninja ex"
  const s = String(deckName).trim();

  // 找出每個 "ex" 的結束位置（最多取前兩個）
  const re = /\bex\b/gi;
  const hits: number[] = [];
  let m: RegExpExecArray | null;
  while ((m = re.exec(s)) && hits.length < 2) hits.push(m.index + m[0].length);

  if (hits.length < 2) return [s || undefined, undefined];

  const firstEnd = hits[0];
  const secondEnd = hits[1];

  // 第一段：從頭到第一個 ex（含 ex）
  const part1 = s.slice(0, firstEnd).trim();

  // 第二段：從第一個 ex 後面到第二個 ex（含 ex）
  const part2 = s.slice(firstEnd, secondEnd).trim();

  return [part1 || undefined, part2 || undefined];
}

/**
 * 取得每副牌組「兩個」icon keys（主力/副手）
 * 你可以讓 standings 每列直接提供 deckIconKeys: [main, sub] 最穩。
 */
function getDeckIconKeys(r: any): (string | undefined)[] {
  // ✅ 0) 你說的重點：deck.icons 已經是「兩隻」
  const icons = r?.deck?.icons;
  if (Array.isArray(icons) && icons.length) {
    const a = icons[0] != null ? String(icons[0]) : undefined;
    const b = icons[1] != null ? String(icons[1]) : undefined;
    return [a, b];
  }

  // 1) array fields
  const a1 = r?.deck?.iconKeys;
  if (Array.isArray(a1) && a1.length) return [a1[0], a1[1]].map((x) => (x != null ? String(x) : undefined));

  const a2 = r?.deckIconKeys;
  if (Array.isArray(a2) && a2.length) return [a2[0], a2[1]].map((x) => (x != null ? String(x) : undefined));

  // 2) explicit pair fields
  const main =
    r?.deck?.primaryIconKey ??
    r?.deck?.mainIconKey ??
    r?.deckIconKeyMain ??
    r?.primaryIconKey ??
    r?.mainIconKey ??
    r?.deck?.mainPokemon ??
    r?.deck?.main ??
    undefined;

  const sub =
    r?.deck?.secondaryIconKey ??
    r?.deck?.subIconKey ??
    r?.deckIconKeySub ??
    r?.secondaryIconKey ??
    r?.subIconKey ??
    r?.deck?.subPokemon ??
    r?.deck?.sub ??
    undefined;

  if (main != null || sub != null) {
    return [main != null ? String(main) : undefined, sub != null ? String(sub) : undefined];
  }

  // 3) parse from deck.id like "suicune-ex-a4a-greninja-ex-b1"
  const fromId = parseTwoFromDeckId(r?.deck?.id);
  if (fromId[0] || fromId[1]) return fromId;

  // 4) parse from deck.name like "Suicune ex Greninja ex"
  const fromName = parseTwoFromDeckName(r?.deck?.name ?? r?.deck?.archetype ?? r?.archetype);
  if (fromName[0] || fromName[1]) return fromName;

  // fallback
  return [undefined, undefined];
}

function pickTopN(standings: any[], n: number): any[] {
  if (!Array.isArray(standings) || standings.length === 0) return [];

  const getPlace = (r: any) => r?.placing ?? r?.place ?? r?.rank ?? 999999;

  return [...standings]
    .sort((a, b) => getPlace(a) - getPlace(b))
    .slice(0, n);
}

// ---- medals ----
function medalClass(rank: number) {
  if (rank === 1) return "medal--gold";
  if (rank === 2) return "medal--silver";
  return "medal--platinum"; // 3rd & 4th
}
function medalTitle(rank: number) {
  if (isZh.value) {
    if (rank === 1) return "冠軍（金）";
    if (rank === 2) return "亞軍（銀）";
    return "季軍/殿軍（鉑）";
  }
  if (rank === 1) return "Champion (Gold)";
  if (rank === 2) return "Runner-up (Silver)";
  return "Top 4 (Platinum)";
}

function missingIconTitle(key: string | undefined, rank: number, slot: number) {
  const k = key ? `key=${key}` : "key=undefined";
  return isZh.value
    ? `缺少 icon（第${rank}名 第${slot}圖，${k}）`
    : `Missing icon (rank ${rank} slot ${slot}, ${k})`;
}

function deckPairTitle(d: TopDeck, rank: number) {
  const k1 = d.iconKeys[0] ?? "—";
  const k2 = d.iconKeys[1] ?? "—";
  return isZh.value
    ? `第${rank}名：${k1} / ${k2}`
    : `Rank ${rank}: ${k1} / ${k2}`;
}

const tournaments = computed<TournamentRow[]>(() => {
  const rows: TournamentRow[] = [];

  for (const [path, mod] of Object.entries(detailsModules)) {
    const id = extractIdFromPath(path);
    if (!id) continue;

    const details = mod?.default ?? mod;

    const standingsPath = path.replace(/details\.json$/, "standings.json");
    const standingsMod = standingsModules[standingsPath];
    const standings = (standingsMod?.default ?? standingsMod) as any[];

    const top4Rows = pickTopN(standings, 4);
    const topDecks: TopDeck[] = top4Rows.map((r) => {
      const keys = getDeckIconKeys(r);
      const urls = keys.map((k) => resolveDeckIconUrl(k)) as (string | undefined)[];
      return {
        iconKeys: [keys[0], keys[1]],
        iconUrls: [urls[0], urls[1]],
      };
    });

    const dateMs =
      toUtcDateMs(details?.date) ??
      toUtcDateMs(details?.startDate) ??
      toUtcDateMs(details?.start_date) ??
      toUtcDateMs(details?.time) ??
      undefined;

    const dateISO = dateMs ? formatUtcYmd(dateMs) : undefined;

    const players =
      details?.players ??
      details?.playerCount ??
      details?.player_count ??
      details?.attendance ??
      undefined;

    const format = formatFromDetails(details);



    
const g = String(details?.game ?? "").toUpperCase();
  if (g && g !== "POCKET") continue;
    
    const set = inferVersionByStartMs(dateMs)?.code;

    const swiss = swissLabelFromDetails(details);

    rows.push({
      id,
      dateISO,
      dateMs,
      dateStr: dateISO ?? "—",
      name: details?.name ?? details?.title ?? id,
      players: typeof players === "number" ? players : Number(players) || undefined,

      set: set ? String(set) : undefined,
      format: format ? String(format) : undefined,
      swiss,

      topDecks,

      standingsUrl: `https://play.limitlesstcg.com/tournament/${id}/standings`,
    });
  }

  rows.sort((a, b) => (b.dateMs ?? 0) - (a.dateMs ?? 0));
  return rows;
});

const monthOptions = computed(() => {
  const seen = new Set<string>();
  const opts: { value: string; label: string }[] = [];

  for (const t of tournaments.value) {
    if (!t.dateMs) continue;
    const d = new Date(t.dateMs);
    const y = d.getUTCFullYear();
    const m = d.getUTCMonth() + 1;
    const key = `${y}-${String(m).padStart(2, "0")}`;
    if (seen.has(key)) continue;
    seen.add(key);

    opts.push({
      value: `month:${key}`,
      label: isZh.value ? `${m}月${y}` : `${key}`,
    });
  }

  opts.sort((a, b) => (a.value < b.value ? 1 : -1));
  return opts;
});

function inTimeRange(t: TournamentRow) {
  if (!t.dateMs) return false;

  const now = Date.now();
  const day = 24 * 60 * 60 * 1000;

  if (filters.time === "past7") return t.dateMs >= now - 7 * day;
  if (filters.time === "past4w") return t.dateMs >= now - 28 * day;

  if (filters.time.startsWith("month:")) {
    const ym = filters.time.slice("month:".length);
    const [yS, mS] = ym.split("-");
    const y = Number(yS);
    const m = Number(mS);
    if (!y || !m) return true;

    const start = Date.UTC(y, m - 1, 1, 0, 0, 0);
    const end = Date.UTC(y, m, 1, 0, 0, 0);
    return t.dateMs >= start && t.dateMs < end;
  }

  return true;
}

const filtered = computed(() => {
  return tournaments.value.filter((t) => {
    if (filters.minPlayers != null && Number.isFinite(filters.minPlayers)) {
      if ((t.players ?? 0) < (filters.minPlayers as number)) return false;
    }

    if (!inTimeRange(t)) return false;

    if (filters.set && t.set !== filters.set) return false;

    if (filters.swiss) {
      if ((t.swiss ?? "Other") !== filters.swiss) return false;
    }


    if (filters.format) {
      if (!t.format) return false;
      if (t.format !== filters.format) return false;
    }

    return true;
  });
});

// ---------- pagination ----------
const PAGE_SIZES = [10, 20, 50] as const;
type PageSize = typeof PAGE_SIZES[number];

const pageSize = ref<PageSize>(20);

const page = ref(1);

const total = computed(() => filtered.value.length);

const pageCount = computed(() => {
  const n = Math.ceil(total.value / pageSize.value);
  return Math.max(1, n);
});

const pageStartIndex = computed(() => (page.value - 1) * pageSize.value);

const paged = computed(() => {
  const start = pageStartIndex.value;
  return filtered.value.slice(start, start + pageSize.value);
});

const rangeStart = computed(() => (total.value === 0 ? 0 : pageStartIndex.value + 1));
const rangeEnd = computed(() => Math.min(total.value, pageStartIndex.value + pageSize.value));

function setPageSize(n: PageSize) {
  pageSize.value = n;
}

function prevPage() {
  page.value = Math.max(1, page.value - 1);
}
function nextPage() {
  page.value = Math.min(pageCount.value, page.value + 1);
}

// filters 或 pageSize 改變時，回到第 1 頁
watch(
  () => ({ ...filters, pageSize: pageSize.value }),
  () => {
    page.value = 1;
  },
  { deep: true }
);

// 如果套了 filter 後總頁數變少，確保 page 不超出
watch([total, pageSize], () => {
  if (page.value > pageCount.value) page.value = pageCount.value;
});

</script>

<style scoped>
.page { padding: 12px 14px; }
.header { display: flex; justify-content: space-between; gap: 12px; align-items: flex-end; margin-bottom: 12px; }
.title { font-size: 20px; font-weight: 900; color: rgba(255,255,255,0.92); }
.sub { margin-top: 4px; font-size: 12px; color: rgba(226,232,240,0.75); }

.deckIcon--second {
  margin-left: -3px; /* 更貼：-4；稍開：-2 */
}

.filters {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin: 10px 0 12px;
}
@media (max-width: 980px) {
  .filters { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
.f {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  background: rgba(15,23,42,0.35);
  padding: 10px;
}
.f label { display: block; font-size: 12px; font-weight: 800; color: rgba(255,255,255,0.85); margin-bottom: 6px; }
.f input, .f select {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(2,6,23,0.35);
  color: rgba(255,255,255,0.92);
  padding: 8px 10px;
  outline: none;
}
.hint { margin-top: 6px; font-size: 11px; color: rgba(226,232,240,0.65); }

.tableWrap {
  overflow: auto;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  background: rgba(15,23,42,0.35);
}
.tbl { width: 100%; border-collapse: collapse; min-width: 940px; }
th, td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  text-align: left;
  vertical-align: middle;
}
th { color: rgba(226,232,240,0.78); font-size: 12px; font-weight: 900; }
td { color: rgba(255,255,255,0.90); font-size: 13px; }
.muted { color: rgba(226,232,240,0.70); }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
.num { text-align: right; }
.date { width: 118px; }
.top4 { width: 260px; }
.link { width: 64px; text-align: center; }
a { color: rgba(147,197,253,0.95); text-decoration: none; font-weight: 800; }
a:hover { text-decoration: underline; }

.nameCell { display: flex; flex-direction: column; gap: 4px; }
.nameMain { font-weight: 900; }
.nameMeta { display: flex; gap: 6px; flex-wrap: wrap; }
.pill {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(2,6,23,0.25);
}

.pill--btn {
  cursor: pointer;
  appearance: none;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(2,6,23,0.25);
  color: rgba(226,232,240,0.90);
}

.pill--btn:hover {
  border-color: rgba(255,255,255,0.22);
  background: rgba(2,6,23,0.35);
}

.pill--active {
  border-color: rgba(147,197,253,0.55);
  background: rgba(30,41,59,0.35);
  color: rgba(255,255,255,0.95);
}

/* button 預設會有 focus ring，你可以保留或自訂 */
.pill--btn:focus-visible {
  outline: 2px solid rgba(147,197,253,0.55);
  outline-offset: 2px;
}

/* Top 4 decks: 4 columns, each cell has 2 icons + medal */
.topDecksGrid {
  display: grid;
  grid-template-columns: repeat(4, max-content);
  column-gap: 14px;
  row-gap: 8px;
  align-items: start;
}
.deckPair {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.deckIconsRow {
  display: inline-flex;
  gap: 6px;
  align-items: center;
}

.deckIconsRow {
  display: inline-flex;
  align-items: center;
  gap: 0;
  line-height: 0;
}

.deckIcon {
  width: 34px;
  height: 34px;
  object-fit: contain;

  background: transparent;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  outline: none;

  display: block;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.55));
  z-index: 2;
}

.deckIconFallback {
  width: 34px;
  height: 34px;
  display: block;

  border: 0;
  border-radius: 0;
  background: rgba(255,255,255,0.06);
}

.deckDisk {
  width: 64px;
  height: 44px;
  margin-top: -43px;
  opacity: 0.95;
  display: block;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.6));
  z-index:1;
}

/* medal discs */
.medal {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.18);
  box-shadow:
    0 0 0 1px rgba(0,0,0,0.25) inset,
    0 1px 6px rgba(0,0,0,0.35);
}
.medal--gold {
  background: radial-gradient(circle at 30% 30%, #fff3c4 0%, #f6c84b 35%, #b7791f 100%);
}
.medal--silver {
  background: radial-gradient(circle at 30% 30%, #ffffff 0%, #cbd5e1 40%, #64748b 100%);
}
.medal--platinum {
  background: radial-gradient(circle at 30% 30%, #ffffff 0%, #e5e4e2 40%, #8b8b8b 100%);
}

/* standings link dot */
.linkDot {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(2,6,23,0.25);
  color: rgba(147,197,253,0.95);
  font-weight: 900;
  text-decoration: none;
  user-select: none;
}
.linkDot:hover {
  text-decoration: none;
  border-color: rgba(147,197,253,0.55);
  background: rgba(30,41,59,0.35);
}

.foot { margin-top: 10px; font-size: 12px; }

.pager{
  margin: 10px 0 12px;
  padding: 10px 12px;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  background: rgba(15,23,42,0.35);

  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.pager__left{
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.pager__label{
  font-size: 12px;
  font-weight: 900;
  color: rgba(226,232,240,0.85);
}

.pager__sizes{
  display: inline-flex;
  gap: 8px;
}

.pagerBtn{
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(2,6,23,0.25);
  color: rgba(226,232,240,0.85);
  cursor: pointer;
  font-weight: 800;
  font-size: 12px;
}

.pagerBtn:hover{
  border-color: rgba(255,255,255,0.22);
  background: rgba(2,6,23,0.35);
}

.pagerBtn.is-active{
  border-color: rgba(147,197,253,0.55);
  background: rgba(30,41,59,0.35);
  color: rgba(255,255,255,0.95);
}

.nameLink {
  color: rgba(255, 255, 255, 0.92);
}
.nameLink:hover {
  text-decoration: underline;
}

.pager__summary{
  font-size: 12px;
}

.pager__right{
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.pagerNav{
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(2,6,23,0.25);
  color: rgba(226,232,240,0.9);
  cursor: pointer;
  font-weight: 900;
  font-size: 12px;
}

.pagerNav:disabled{
  opacity: 0.5;
  cursor: not-allowed;
}

.pager__page{
  color: rgba(226,232,240,0.9);
  font-size: 12px;
}

</style>