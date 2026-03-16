<template>
  <div class="page">
    <h1 class="pageTitle">{{ ui.title }}</h1>

    <div class="meta">
      <div>{{ ui.time }}: <span class="mono">{{ meta?.generated_at || "—" }}</span></div>
      <div>
        <!-- Window: last {{ Data.meta.days_back }} days ·
        Min players: {{ Data.meta.min_players }} ·
        Usage ≥ {{ (Data.meta.usage_threshold * 100).toFixed(0) }}% ·
        Events: {{ Data.meta.tournaments_count }} -->
        {{ ui.window }}
      </div>
    </div>

    <div class="tableWrap">
      <div class="responsive-table">
        <table class="tbl">
          <thead>
            <tr>
              <th>#</th>
              <th>{{ ui.deck }}</th>
              <th>{{ ui.tier }}</th>
              <th class="num">{{ ui.score }}</th>
              <th class="num">{{ ui.usage }}</th>
              <th class="num">{{ ui.samples }}</th>
              <th class="num">{{ ui.top32 }}</th>
              <th class="num">{{ ui.points }}</th>
              <th class="num">{{ ui.top32pct }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in rows" :key="r.deck">
              <td class="muted">{{ i + 1 }}</td>
              <td class="deck">{{ r.deck }}</td>
              <td><span class="pill" :data-tier="r.tier">{{ r.tier }}</span></td>
              <td class="num mono">{{ r.score.toFixed(4) }}</td>
              <td class="num mono">{{ (r.usage * 100).toFixed(2) }}%</td>
              <td class="num mono">{{ r.total_samples }}</td>
              <td class="num mono">{{ r.data1_top32_appearances }}</td>
              <td class="num mono">{{ r.data2_weighted_points }}</td>
              <td class="num mono">{{ r.data3_top32_share_pct.toFixed(2) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- 移动端卡片式布局 -->
      <div class="mobile-cards" v-if="rows.length > 0">
        <div v-for="(r, i) in rows" :key="r.deck" class="mobile-card">
          <div class="card-header">
            <span class="rank-badge">{{ i + 1 }}</span>
            <div class="deck-info">
              <div class="deck-name">{{ r.deck }}</div>
              <span class="pill" :data-tier="r.tier">{{ r.tier }}</span>
            </div>
          </div>
          <div class="card-stats">
            <div class="stat-item">
              <span class="stat-label">{{ ui.score }}</span>
              <span class="stat-value mono">{{ r.score.toFixed(4) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">{{ ui.usage }}</span>
              <span class="stat-value mono">{{ (r.usage * 100).toFixed(2) }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">{{ ui.samples }}</span>
              <span class="stat-value mono">{{ r.total_samples }}</span>
            </div>
          </div>
          <div class="card-stats">
            <div class="stat-item">
              <span class="stat-label">{{ ui.top32 }}</span>
              <span class="stat-value mono">{{ r.data1_top32_appearances }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">{{ ui.points }}</span>
              <span class="stat-value mono">{{ r.data2_weighted_points }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">{{ ui.top32pct }}</span>
              <span class="stat-value mono">{{ r.data3_top32_share_pct.toFixed(2) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from "vue-router";

// 统一：从 public/data/*.json 通过 fetch 读取
const BASE_URL = (import.meta as any).env?.BASE_URL ?? "/";

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url, { cache: "force-cache" });
  if (!res.ok) throw new Error(`Fetch failed ${res.status} for ${url}`);
  return (await res.json()) as T;
}

type TierRow = {
  deck: string;
  tier: string;
  score: number;
  usage: number;
  total_samples: number;
  data1_top32_appearances: number;
  data2_weighted_points: number;
  data3_top32_share_pct: number;
};

type Meta = {
  generated_at: string;
  days_back: number;
  min_players: number;
  usage_threshold: number;
  tournaments_count: number;
};

const tierRows = ref<TierRow[]>([]);
const meta = ref<Meta | null>(null);

onMounted(async () => {
  try {
    tierRows.value = await fetchJson<TierRow[]>(`${BASE_URL}data/tier.json`);
  } catch {
    tierRows.value = [];
  }

  try {
    meta.value = await fetchJson<Meta>(`${BASE_URL}data/meta.json`);
  } catch {
    meta.value = null;
  }
});

const rows = computed(() => tierRows.value);

const route = useRoute();
const lang = computed<"zh" | "en">(() => {
  const seg = String(route.path).split("/")[1];
  return seg === "en" ? "en" : "zh";
});

const isZh = computed(() => lang.value === "zh");

const ui = computed(() => {
  const m = meta.value;
  const days = m?.days_back ?? 0;
  const minPlayers = m?.min_players ?? 0;
  const usage = ((m?.usage_threshold ?? 0) * 100).toFixed(0);
  const events = m?.tournaments_count ?? 0;

  if (isZh.value) {
    return {
      title: "梯队排行",
      time: "发布于",
      window: `统计范围：最近 ${days} 天 · 最小参赛人数 ${minPlayers} · 使用率 ≥ ${usage}% · 赛事数量 ${events}`,
      deck: "牌组",
      tier: "梯队",
      score: "评分",
      usage: "使用率",
      samples: "样本数",
      top32: "Top32",
      points: "积分",
      top32pct: "Top32%",
    };
  }
  return {
    title: "Tier List",
    time: "Generated at",
    window: `Window: last ${days} days · Min players: ${minPlayers} · Usage ≥ ${usage}% · Events: ${events}`,
    deck: "Deck",
    tier: "Tier",
    score: "Score",
    usage: "Usage",
    samples: "Samples",
    top32: "Top32",
    points: "Points",
    top32pct: "Top32%",
  };
});
</script>

<style scoped>
.page {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 10px;
  box-sizing: border-box;
}
.pageTitle { margin: 0 0 12px; color: rgba(255,255,255,0.92); font-size: 18px; font-weight: 800; }
.meta { margin-bottom: 12px; color: rgba(226,232,240,.75); font-size: 12px; line-height: 1.5; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

.tableWrap {
  width: 100%;
  box-sizing: border-box;
  margin: 0 auto;
}

.responsive-table {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  background: rgba(15,23,42,0.35);
  width: 100%;
  box-sizing: border-box;
  margin: 0 auto;
}

.tbl { 
  width: 100%; 
  border-collapse: collapse; 
  table-layout: fixed;
}

/* 调整列宽 */
td.deck {
  width: 25%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

th:nth-child(1), td:nth-child(1) {
  width: 5%;
  text-align: center;
}

th:nth-child(3), td:nth-child(3) {
  width: 8%;
  text-align: center;
}

th:nth-child(4), td:nth-child(4) {
  width: 10%;
  text-align: right;
}

th:nth-child(5), td:nth-child(5) {
  width: 10%;
  text-align: right;
}

th:nth-child(6), td:nth-child(6) {
  width: 10%;
  text-align: right;
}

th:nth-child(7), td:nth-child(7) {
  width: 10%;
  text-align: right;
}

th:nth-child(8), td:nth-child(8) {
  width: 10%;
  text-align: right;
}

th:nth-child(9), td:nth-child(9) {
  width: 12%;
  text-align: right;
}

/* 移动端卡片式布局 */
.mobile-cards {
  display: none;
  width: 100%;
}

.mobile-card {
  background: rgba(15, 23, 42, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-sizing: border-box;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.rank-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.7);
  color: white;
  font-weight: bold;
  font-size: 14px;
  margin-right: 12px;
}

.deck-info {
  flex: 1;
}

.deck-name {
  font-size: 14px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
}

.card-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.card-stats:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.stat-label {
  font-size: 12px;
  color: rgba(226, 232, 240, 0.7);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 14px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.9);
}

/* 响应式断点 */
@media (max-width: 760px) {
  .page {
    width: 100%;
    padding: 0 10px;
    box-sizing: border-box;
  }
  
  .responsive-table {
    display: none;
  }
  
  .mobile-cards {
    display: block;
  }
  
  .pageTitle {
    font-size: 16px;
  }
  
  .meta {
    font-size: 11px;
  }
}
th, td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.06); text-align: left; }
th { font-size: 12px; color: rgba(226,232,240,.75); font-weight: 700; }
td { font-size: 13px; color: rgba(255,255,255,0.9); }
.num { text-align: right; }
.muted { color: rgba(226,232,240,.55); }
.deck { max-width: 280px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.pill { display: inline-block; padding: 3px 8px; border-radius: 999px; font-weight: 800; font-size: 12px; border: 1px solid rgba(255,255,255,0.10); }
.pill[data-tier="S"] { background: rgba(255,215,0,0.15); }
.pill[data-tier="A"] { background: rgba(0,175,239,0.15); }
.pill[data-tier="B"] { background: rgba(34,197,94,0.15); }
.pill[data-tier="C"] { background: rgba(249,115,22,0.15); }
.pill[data-tier="D"] { background: rgba(148,163,184,0.15); }
.pill[data-tier="E"] { background: rgba(148,163,184,0.08); }
</style>