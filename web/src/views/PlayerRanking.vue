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
          <!-- <tr v-for="(r, i) in rows" :key="r.player">
            <td class="muted">{{ i + 1 }}</td>
            <td>{{ r.player }}</td>
            <td class="num mono">{{ r.points }}</td>
          </tr> -->
          <!-- 显示当前页的数据 -->
          <tr v-for="(r, i) in currentPageRows" :key="r.player">
            <td class="muted">{{ (currentPage - 1) * pageSize + i + 1 }}</td>
            <td>{{ r.player }}</td>
            <td class="num mono">{{ r.points }}</td>
          </tr>
          <!-- 空数据提示 -->
          <tr v-if="!currentPageRows.length">
            <td colspan="3" style="text-align: center; padding: 20px;">
              {{ isZh ? '暂无数据' : 'No data' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页控件 -->
    <div class="pagination" v-if="totalPages > 1">
      <button 
        class="page-btn" 
        :disabled="currentPage === 1"
        @click="currentPage -= 1"
      >
        {{ isZh ? '上一页' : 'Previous' }}
      </button>
      
      <span class="page-info">
        {{ isZh ? `第 ${currentPage} 页 / 共 ${totalPages} 页` : `Page ${currentPage} / ${totalPages}` }}
      </span>
      
      <button 
        class="page-btn" 
        :disabled="currentPage === totalPages"
        @click="currentPage += 1"
      >
        {{ isZh ? '下一页' : 'Next' }}
      </button>

      <!-- 可选：快速跳页控件 -->
      <div class="page-jump" v-if="totalPages > 5">
        <input 
          type="number" 
          v-model.number="jumpPage" 
          :min="1" 
          :max="totalPages"
          class="page-input"
        >
        <button 
          class="page-btn jump-btn"
          @click="jumpToPage"
        >
          {{ isZh ? '跳转' : 'Go' }}
        </button>
      </div>
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

// 分页配置
const pageSize = ref(15); // 每页显示10条
const currentPage = ref(1); // 当前页码
const jumpPage = ref(1); // 跳转页码

// 所有玩家数据
const allPlayers = computed(() => Data.players || []);

// 总页数
const totalPages = computed(() => {
  return Math.ceil(allPlayers.value.length / pageSize.value);
});

// 当前页显示的数据
const currentPageRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return allPlayers.value.slice(start, end);
});

// 跳转页面方法
const jumpToPage = () => {
  if (jumpPage.value < 1) {
    jumpPage.value = 1;
  } else if (jumpPage.value > totalPages.value) {
    jumpPage.value = totalPages.value;
  }
  currentPage.value = jumpPage.value;
};

// 监听总页数变化，防止页码超出范围
watch(totalPages, () => {
  if (currentPage.value > totalPages.value) {
    currentPage.value = totalPages.value || 1;
  }
});
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

/* 分页样式 */
.pagination {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  color: rgba(255,255,255,0.9);
  font-size: 13px;
}

.page-btn {
  padding: 6px 12px;
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 6px;
  background: rgba(15,23,42,0.5);
  color: rgba(255,255,255,0.9);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn:not(:disabled):hover {
  background: rgba(15,23,42,0.8);
  border-color: rgba(255,255,255,0.25);
}

.page-info {
  color: rgba(226,232,240,.75);
  font-size: 12px;
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.page-input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 6px;
  background: rgba(15,23,42,0.5);
  color: rgba(255,255,255,0.9);
  font-size: 12px;
  outline: none;
}

.page-input:focus {
  border-color: rgba(255,255,255,0.25);
}

.jump-btn {
  padding: 6px 10px;
}
</style>