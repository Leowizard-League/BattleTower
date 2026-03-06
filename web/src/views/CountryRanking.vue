<template>
  <div class="page">
    <div class="header">
      <div>
        <div class="title">{{ ui.title }}</div>
        <div class="sub">
          {{ ui.standingsTitle }}
        </div>
      </div>
    </div>
    <div class="tableWrap">
      <table class="tbl">
        <thead>
          <tr>
            <th class="num" rowspan="2">
              {{ ui.rank }}
            </th>
            <th class="num" rowspan="2">
              {{ ui.country }}
            </th>
            <th class="num" rowspan="2">
              {{ ui.totalcountryplayers }}
            </th>
            <th class="num" rowspan="2">
              {{ ui.totalplayers }}
            </th>
            <!-- <th class="num">
              {{ ui.totalappearances }}
            </th> -->
            <th colspan="4" style="text-align: center;">{{ ui.bestplayer }}</th>
          </tr>
          <tr>
            <!-- <td colspan="4"></td> -->
            <th class="num">
              {{ ui.first }}
            </th>
            <th class="num">
              {{ ui.second }}
            </th>
            <th class="num">
              {{ ui.third }}
            </th>
            <th class="num">
              {{ ui.actions }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="num muted">1</td>
            <td class="num muted">japan</td>
            <td class="num muted">1000</td>
            <td class="num muted">5000</td>
            <!-- <td class="num muted">20000</td> -->
            <td class="num muted">10</td>
            <td class="num muted">5</td>
            <td class="num muted">2</td>
            <td class="num muted">{{ ui.view }}</td>
          </tr>
          <tr>
            <td class="num muted">2</td>
            <td class="num muted">usa</td>
            <td class="num muted">800</td>
            <td class="num muted">4000</td>
            <!-- <td class="num muted">15000</td> -->
            <td class="num muted">8</td>
            <td class="num muted">3</td>
            <td class="num muted">1</td>
            <td class="num muted">{{ ui.view }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
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
      title: "《宝可梦 TCG 口袋版》国家 / 地区玩家排行榜",
      standingsTitle: "赛事",
      rank: "排名",
      country: "国家/地区",
      totalcountryplayers: "国家/地区玩家总分数",
      totalplayers: "合计玩家总数",
      bestplayer: "最佳玩家",
      first: "第一",
      second: "第二",
      third: "第三",
      actions:"操作",
      view: "查看",
    };
  }
  return {
    title: "Pokémon TCG Pocket Country Player Rankings",
    standingsTitle: "Season",
    rank: "Rank",
    country: "Country/Region",
    totalcountryplayers: "Total Points in Country/Region",
    totalplayers: "Total Players",
    bestplayer: "Best Player in Country/Region",
    first: "1st",
    second: "2nd",
    third: "3rd",
    actions: "Actions",
    view: "View",
  };
});
</script>

<style scoped>
.page {
  width: 1100px;
}

.header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-end;
  margin-bottom: 12px;
}

.title {
  font-size: 20px;
  font-weight: 900;
  color: rgba(255, 255, 255, 0.92);
}

.sub {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(226, 232, 240, 0.75);
}

.tableWrap {
  overflow: auto;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.35);
}

.tbl {
  width: 100%;
  border-collapse: collapse;
  min-width: 940px;
}

th,
td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  text-align: left;
  vertical-align: middle;
}

th {
  color: rgba(226, 232, 240, 0.78);
  font-size: 12px;
  font-weight: 900;
}

td {
  color: rgba(255, 255, 255, 0.90);
  font-size: 13px;
}

.muted {
  color: rgba(226, 232, 240, 0.70);
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.num {
  text-align: right;
}

.date {
  width: 118px;
}

.top4 {
  width: 260px;
}

.link {
  width: 64px;
  text-align: center;
}

a {
  color: rgba(147, 197, 253, 0.95);
  text-decoration: none;
  font-weight: 800;
}

a:hover {
  text-decoration: underline;
}

.nameCell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nameMain {
  font-weight: 900;
}

.nameMeta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
</style>