<template>
  <div>
    <h1 class="pageTitle">Tier List</h1>

    <div class="meta">
      <div>Generated at: <span class="mono">{{ Data.meta.generated_at }}</span></div>
      <div>
        Window: last {{ Data.meta.days_back }} days ·
        Min players: {{ Data.meta.min_players }} ·
        Usage ≥ {{ (Data.meta.usage_threshold * 100).toFixed(0) }}% ·
        Events: {{ Data.meta.tournaments_count }}
      </div>
    </div>

    <div class="tableWrap">
      <table class="tbl">
        <thead>
          <tr>
            <th>#</th>
            <th>Deck</th>
            <th>Tier</th>
            <th class="num">Score</th>
            <th class="num">Usage</th>
            <th class="num">Samples</th>
            <th class="num">Top32</th>
            <th class="num">Points</th>
            <th class="num">Top32%</th>
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
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Data } from '../lib/data'

const rows = computed(() => Data.tier)
</script>

<style scoped>
.pageTitle { margin: 0 0 12px; color: rgba(255,255,255,0.92); font-size: 18px; font-weight: 800; }
.meta { margin-bottom: 12px; color: rgba(226,232,240,.75); font-size: 12px; line-height: 1.5; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

.tableWrap { overflow: auto; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; background: rgba(15,23,42,0.35); }
.tbl { width: 100%; border-collapse: collapse; min-width: 980px; }
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