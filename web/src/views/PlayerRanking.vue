<template>
  <div>
    <h1 class="pageTitle">Player Ranking</h1>

    <div class="meta">
      <div>Points rule = your placing weights (1st 10, 2nd 8, 3-4 6, 5-8 4, 9-16 2, 17-32 1)</div>
    </div>

    <div class="tableWrap">
      <table class="tbl">
        <thead>
          <tr>
            <th>#</th>
            <th>Player</th>
            <th class="num">Points</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in rows" :key="r.player">
            <td class="muted">{{ i + 1 }}</td>
            <td>{{ r.player }}</td>
            <td class="num mono">{{ r.points }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Data } from '../lib/data'

const rows = computed(() => Data.players)
</script>

<style scoped>
.pageTitle { margin: 0 0 12px; color: rgba(255,255,255,0.92); font-size: 18px; font-weight: 800; }
.meta { margin-bottom: 12px; color: rgba(226,232,240,.75); font-size: 12px; line-height: 1.5; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

.tableWrap { overflow: auto; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; background: rgba(15,23,42,0.35); }
.tbl { width: 100%; border-collapse: collapse; min-width: 680px; }
th, td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.06); text-align: left; }
th { font-size: 12px; color: rgba(226,232,240,.75); font-weight: 700; }
td { font-size: 13px; color: rgba(255,255,255,0.9); }
.num { text-align: right; }
.muted { color: rgba(226,232,240,.55); }
</style>