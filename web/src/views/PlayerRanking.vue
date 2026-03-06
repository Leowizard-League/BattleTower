<template>
  <div class="page">
    <h1 class="pageTitle">{{ ui.title }}</h1>

    <div class="meta">
      <div>{{ ui.rule }}</div>
    </div>

    <div class="tableWrap">
      <table class="tbl">
        <thead>
          <tr>
            <th>#</th>
            <th>{{ ui.player }}</th>
            <th class="num">{{ ui.points }}</th>
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
import { Data } from '../lib/data'
import { useRoute } from "vue-router";
import { computed, reactive, ref, watch } from "vue";

const route = useRoute();

const lang = computed<"zh" | "en">(() => {
  const seg = String(route.path).split("/")[1];
  return seg === "en" ? "en" : "zh";
});

const isZh = computed(() => lang.value === "zh");

const ui = computed(() => {
  if (isZh.value) {
    return {
      title: "玩家排行榜",
      rule: "积分规则 = 你在每场比赛中的排名权重（第1名 10分，第2名 8分，第3-4名 6分，第5-8名 4分，第9-16名 2分，第17-32名 1分）",
      player: "玩家",
      points: "积分",
    };
  }
  return {
    title: "Player Ranking",
    rule: "Points rule = your placing weights (1st 10, 2nd 8, 3-4 6, 5-8 4, 9-16 2, 17-32 1)",
    player: "Player",
    points: "Points",
  };
});

const rows = computed(() => Data.players)
</script>

<style scoped>
.page{ width: 1100px; }
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