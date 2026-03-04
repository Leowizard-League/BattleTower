<!-- web/src/views/TournamentReport.vue -->
<template>
  <div class="page">
    <div class="topBar">
      <RouterLink class="back" :to="`/${lang}/tournaments`">
        ← {{ isZh ? "返回賽事列表" : "Back to tournaments" }}
      </RouterLink>

      <a class="ext" :href="standingsUrl" target="_blank" rel="noreferrer">
        {{ isZh ? "Standings ↗" : "Standings ↗" }}
      </a>
    </div>

    <div v-if="!details" class="card">
      <div class="title">
        {{ isZh ? "找不到賽事資料" : "Tournament not found" }}
      </div>
      <div class="muted mono">
        id = {{ id }}
      </div>
      <div class="muted" style="margin-top: 8px;">
        {{ isZh ? "請確認是否存在：" : "Make sure files exist:" }}
        <div class="mono muted">web/src/data/raw/{{ id }}/details.json</div>
        <div class="mono muted">web/src/data/raw/{{ id }}/standings.json</div>
      </div>
    </div>

    <template v-else>
      <div class="card">
        <div class="title">{{ detailsTitle }}</div>

        <div class="metaGrid">
          <div class="kv">
            <div class="k">{{ isZh ? "日期(UTC)" : "Date (UTC)" }}</div>
            <div class="v mono">{{ dateStr }}</div>
          </div>

          <div class="kv">
            <div class="k">{{ isZh ? "人數" : "Players" }}</div>
            <div class="v mono">{{ players ?? "—" }}</div>
          </div>

          <div class="kv">
            <div class="k">{{ isZh ? "賽制" : "Format" }}</div>
            <div class="v">{{ formatLabelForUi(format) }}</div>
          </div>

          <div class="kv">
            <div class="k">{{ isZh ? "瑞士輪" : "Swiss" }}</div>
            <div class="v mono">{{ swiss ?? "—" }}</div>
          </div>
        </div>

        <div v-if="details?.phases?.length" class="muted" style="margin-top: 10px;">
          <div class="k">{{ isZh ? "Phases" : "Phases" }}</div>
          <div class="mono" style="margin-top: 6px; white-space: pre-wrap;">
            {{ JSON.stringify(details.phases, null, 2) }}
          </div>
        </div>
      </div>

      <div class="sectionTitle">
        {{ isZh ? "Top 32" : "Top 32" }}
        <span class="muted mono">({{ top32.length }})</span>
      </div>

      <div class="standings">
        <div v-for="r in top32" :key="rowKey(r)" class="row">
          <div class="place mono muted">{{ getPlace(r) ?? "—" }}</div>

          <div class="player">
            <div class="playerName">{{ playerNameFromRow(r) }}</div>
            <div class="deckName muted">{{ deckNameFromRow(r) }}</div>
          </div>

          <div class="deckIcons">
            <template v-for="slot in 2" :key="slot">
              <img
                v-if="deckIconUrls(r)[slot - 1]"
                :class="['deckIcon', slot === 2 ? 'deckIcon--second' : '']"
                :src="deckIconUrls(r)[slot - 1]!"
                alt=""
                loading="lazy"
                decoding="async"
                draggable="false"
              />
              <span
                v-else
                :class="['deckIconFallback', slot === 2 ? 'deckIconFallback--second' : '']"
                aria-hidden="true"
              />
            </template>
          </div>

          <div class="decklist">
            <details v-if="getDeckCards(r)?.length" class="details">
              <summary class="summary">
                {{ isZh ? "展開牌組" : "Show deck" }}
                <span class="muted mono">({{ deckCardTotal(getDeckCards(r)!) }})</span>
              </summary>

              <div class="cards mono">
                <div v-for="c in getDeckCards(r)!" :key="c.name" class="cardLine">
                  <span class="qty">{{ c.count }}×</span>
                  <span class="nm">{{ c.name }}</span>
                </div>
              </div>
            </details>

            <div v-else class="muted">
              {{ isZh ? "（standings.json 內沒有 decklist）" : "(No decklist in standings.json)" }}
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

// -------- route params --------
const route = useRoute();

const lang = computed<"zh" | "en">(() => {
  const p = String(route.params.lang ?? "");
  if (p === "en") return "en";
  if (p === "zh") return "zh";
  // fallback
  const seg = String(route.path).split("/")[1];
  return seg === "en" ? "en" : "zh";
});
const isZh = computed(() => lang.value === "zh");

const id = computed(() => String(route.params.id ?? ""));

const standingsUrl = computed(() => `https://play.limitlesstcg.com/tournament/${id.value}/standings`);

// -------- load raw json (same strategy as your Tournaments.vue) --------
const detailsModules = import.meta.glob("../data/raw/*/details.json", { eager: true }) as Record<string, any>;
const standingsModules = import.meta.glob("../data/raw/*/standings.json", { eager: true }) as Record<string, any>;

const details = computed<any | undefined>(() => {
  const key = `../data/raw/${id.value}/details.json`;
  const mod = detailsModules[key];
  return mod?.default ?? mod;
});

const standings = computed<any[]>(() => {
  const key = `../data/raw/${id.value}/standings.json`;
  const mod = standingsModules[key];
  const val = mod?.default ?? mod;
  return Array.isArray(val) ? val : [];
});

// -------- tournament meta helpers --------
type FormatLabel = "Standard" | "NoEX" | "Special";

function formatFromDetails(d: any): FormatLabel | undefined {
  const raw = d?.format;
  if (raw == null) return "Standard";

  const s = String(raw).trim().toUpperCase();
  if (s === "" || s === "STANDARD") return "Standard";
  if (s === "NOEX") return "NoEX";
  if (s === "CUSTOM") return "Special";
  return undefined;
}

function formatLabelForUi(f?: FormatLabel | string) {
  if (!f) return "—";
  if (f === "NoEX") return "NoEX";
  if (isZh.value) {
    if (f === "Standard") return "標準";
    if (f === "Special") return "特殊";
  } else {
    if (f === "Standard") return "Standard";
    if (f === "Special") return "Special";
  }
  return String(f);
}

function swissLabelFromDetails(d: any): "BO1" | "BO3" | "Other" | undefined {
  const phases = Array.isArray(d?.phases) ? d.phases : [];
  const p1 = phases.find((p: any) => p?.phase === 1) ?? phases[0];
  if (!p1) return undefined;

  const p1Type = String(p1?.type ?? "").toUpperCase();
  const p1Mode = String(p1?.mode ?? "").toUpperCase();

  if (p1Type !== "SWISS") return "Other";
  if (p1Mode === "BO1") return "BO1";
  if (p1Mode === "BO3") return "BO3";
  return "Other";
}

function toUtcDateMs(dateLike: any): number | undefined {
  if (!dateLike) return undefined;
  if (typeof dateLike === "number") return dateLike;
  const s = String(dateLike);
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

const detailsTitle = computed(() => details.value?.name ?? details.value?.title ?? id.value);

const dateMs = computed(() => {
  const d = details.value;
  return (
    toUtcDateMs(d?.date) ??
    toUtcDateMs(d?.startDate) ??
    toUtcDateMs(d?.start_date) ??
    toUtcDateMs(d?.time) ??
    undefined
  );
});
const dateStr = computed(() => formatUtcYmd(dateMs.value));

const players = computed<number | undefined>(() => {
  const d = details.value;
  const n = d?.players ?? d?.playerCount ?? d?.player_count ?? d?.attendance;
  const v = typeof n === "number" ? n : Number(n);
  return Number.isFinite(v) ? v : undefined;
});

const format = computed<FormatLabel | undefined>(() => formatFromDetails(details.value));
const swiss = computed(() => swissLabelFromDetails(details.value));

// -------- standings helpers --------
function getPlace(r: any): number | undefined {
  const p = r?.placing ?? r?.place ?? r?.rank;
  const n = typeof p === "number" ? p : Number(p);
  return Number.isFinite(n) ? n : undefined;
}

function rowKey(r: any) {
  return String(r?.id ?? r?.player?.id ?? `${getPlace(r) ?? "x"}:${playerNameFromRow(r)}`);
}

function playerNameFromRow(r: any) {
  return (
    r?.player?.name ??
    r?.name ??
    r?.username ??
    r?.displayName ??
    r?.playerName ??
    "—"
  );
}

function deckNameFromRow(r: any) {
  return (
    r?.deck?.name ??
    r?.deck?.archetype ??
    r?.archetype ??
    "—"
  );
}

function pickTopN(arr: any[], n: number) {
  const getP = (r: any) => getPlace(r) ?? 999999;
  return [...arr].sort((a, b) => getP(a) - getP(b)).slice(0, n);
}

const top32 = computed(() => pickTopN(standings.value, 32));

// -------- deck icons (reuse your logic) --------
const deckIconModules = import.meta.glob("../assets/deck-icons/*.{png,webp,svg}", {
  eager: true,
  import: "default",
}) as Record<string, string>;

function normalizeKeyForMatch(k: string) {
  return k.toLowerCase().replace(/[^a-z0-9]/g, "");
}
function getBasenameNoExt(p: string) {
  const file = p.split("/").pop() ?? p;
  return file.replace(/\.(png|webp|svg)$/i, "");
}

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
  const nk = normalizeKeyForMatch(String(key));
  return deckIconIndex[nk];
}

function getDeckIconKeys(r: any): (string | undefined)[] {
  const icons = r?.deck?.icons;
  if (Array.isArray(icons) && icons.length) {
    return [
      icons[0] != null ? String(icons[0]) : undefined,
      icons[1] != null ? String(icons[1]) : undefined,
    ];
  }
  const a = r?.deckIconKeys;
  if (Array.isArray(a) && a.length) {
    return [
      a[0] != null ? String(a[0]) : undefined,
      a[1] != null ? String(a[1]) : undefined,
    ];
  }
  return [undefined, undefined];
}

function deckIconUrls(r: any) {
  const keys = getDeckIconKeys(r);
  return [resolveDeckIconUrl(keys[0]), resolveDeckIconUrl(keys[1])] as (string | undefined)[];
}

// -------- decklist extraction (best-effort) --------
type DeckCard = { name: string; count: number };

function parseTextDecklist(s: string): DeckCard[] {
  return s
    .split(/\r?\n/)
    .map((x) => x.trim())
    .filter(Boolean)
    .map((line) => {
      // e.g. "2 Pikachu"
      const m = line.match(/^(\d+)\s+(.+)$/);
      if (!m) return null;
      return { count: Number(m[1]!), name: m[2]!.trim() };
    })
    .filter(Boolean) as DeckCard[];
}

function getDeckCards(r: any): DeckCard[] | undefined {
  const raw =
    r?.deck?.cards ??
    r?.deck?.list ??
    r?.decklist ??
    r?.deckList ??
    r?.cards ??
    undefined;

  if (!raw) return undefined;

  if (typeof raw === "string") {
    const xs = parseTextDecklist(raw);
    return xs.length ? xs : undefined;
  }

  if (Array.isArray(raw)) {
    const xs = raw
      .map((c: any) => {
        const name = c?.name ?? c?.card?.name ?? c?.cardName ?? c?.id;
        if (!name) return null;
        const cnt = Number(c?.count ?? c?.qty ?? c?.quantity ?? 1);
        return { name: String(name), count: Number.isFinite(cnt) ? cnt : 1 };
      })
      .filter(Boolean) as DeckCard[];
    return xs.length ? xs : undefined;
  }

  return undefined;
}

function deckCardTotal(cards: DeckCard[]) {
  return cards.reduce((sum, c) => sum + (Number.isFinite(c.count) ? c.count : 0), 0);
}
</script>

<style scoped>
.page { padding: 12px 14px; }
.muted { color: rgba(226,232,240,0.70); }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

.topBar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.back, .ext {
  color: rgba(147,197,253,0.95);
  text-decoration: none;
  font-weight: 900;
}
.back:hover, .ext:hover { text-decoration: underline; }

.card {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  background: rgba(15,23,42,0.35);
  padding: 12px;
}

.title {
  font-size: 18px;
  font-weight: 900;
  color: rgba(255,255,255,0.92);
}

.metaGrid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}
@media (max-width: 980px) {
  .metaGrid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
.k { font-size: 12px; font-weight: 900; color: rgba(226,232,240,0.80); }
.v { margin-top: 4px; color: rgba(255,255,255,0.92); }

.sectionTitle {
  margin-top: 12px;
  margin-bottom: 8px;
  font-weight: 900;
  color: rgba(255,255,255,0.92);
}

.standings {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  background: rgba(15,23,42,0.35);
  overflow: hidden;
}

.row {
  display: grid;
  grid-template-columns: 64px 1.2fr 90px 1fr;
  gap: 10px;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  align-items: start;
}
.row:last-child { border-bottom: 0; }

.place { text-align: right; padding-top: 2px; }
.playerName { font-weight: 900; color: rgba(255,255,255,0.92); }
.deckName { margin-top: 4px; }

.deckIcons { display: inline-flex; align-items: center; gap: 0; line-height: 0; padding-top: 2px; }
.deckIcon, .deckIconFallback {
  width: 34px;
  height: 34px;
  display: block;
  object-fit: contain;
}
.deckIcon { filter: drop-shadow(0 1px 2px rgba(0,0,0,0.55)); z-index: 2; }
.deckIcon--second { margin-left: -3px; }
.deckIconFallback { background: rgba(255,255,255,0.06); }
.deckIconFallback--second { margin-left: -3px; }

.details { width: 100%; }
.summary { cursor: pointer; font-weight: 900; color: rgba(226,232,240,0.92); }
.cards { margin-top: 8px; display: grid; gap: 4px; }
.cardLine { display: flex; gap: 8px; }
.qty { width: 44px; text-align: right; color: rgba(226,232,240,0.80); }
.nm { color: rgba(255,255,255,0.92); }

@media (max-width: 980px) {
  .row { grid-template-columns: 56px 1fr 90px; }
  .decklist { grid-column: 1 / -1; }
}
</style>