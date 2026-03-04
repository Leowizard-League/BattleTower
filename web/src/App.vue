<template>
  <div class="app">
    <header class="topbar">
      <div class="topbar__left">
        <RouterLink :to="`/${lang}`" class="brand">
          <div class="dot" aria-hidden="true"></div>
          <div>
            <div class="logo">BATTLE TOWER META</div>
            <div class="sub">Daily-updated stats</div>
          </div>
        </RouterLink>
      </div>

      <nav class="topbar__nav">
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="navlink"
          active-class="is-active"
        >
          {{ label(item.key) }}
        </RouterLink>
      </nav>

      <div class="topbar__right">
        <RouterLink :to="switchLangTo('zh')" class="lang" active-class="is-active">中文</RouterLink>
        <RouterLink :to="switchLangTo('en')" class="lang" active-class="is-active">EN</RouterLink>
      </div>
    </header>

    <main class="container">
      <RouterView />
    </main>

    <footer class="footer">
      <span>Data: Limitless Tournament Platform API</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const lang = computed<'zh' | 'en'>(() => (String(route.path).split('/')[1] === 'en' ? 'en' : 'zh'))

const nav = computed(() => {
  const base = `/${lang.value}`
  return [
    { key: 'tierList', to: `${base}/tier-list` },
    { key: 'tournaments', to: `${base}/tournaments` },
    { key: 'topDecks', to: `${base}/top-decks` },
    { key: 'topCards', to: `${base}/top-cards` },
    { key: 'playerRanking', to: `${base}/player-ranking` },
    { key: 'countryRanking', to: `${base}/country-ranking` },
  ] as const
})

function switchLangTo(next: 'zh' | 'en') {
  const parts = String(route.path).split('/')
  parts[1] = next
  const nextPath = parts.join('/') || `/${next}`
  return nextPath === '/' ? `/${next}` : nextPath
}

const dict = {
  zh: {
    tierList: '牌組排名',
    tournaments: '線上比賽',
    topDecks: '最強牌組',
    topCards: '泛用卡片',
    playerRanking: '玩家排名',
    countryRanking: '國家排名',
  },
  en: {
    tierList: 'Tier List',
    tournaments: 'Tournaments',
    topDecks: 'Top Decks',
    topCards: 'Cards Usage',
    playerRanking: 'Player Ranking',
    countryRanking: 'Country Ranking',
  },
} as const

function label(key: keyof typeof dict.zh) {
  return dict[lang.value][key]
}
</script>

<style scoped>
/* 原本 App.vue 的版型保留，並融合 Layout.vue 的 topbar/nav 樣式 */
.app { min-height: 100vh; display: flex; flex-direction: column; }
.container { width: 100%; max-width: 1100px; margin: 0 auto; padding: 20px; flex: 1; }

.topbar {
  position: sticky;
  top: 0;
  z-index: 1000; 
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 24px;
  background: rgba(2, 6, 23, 0.75);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.topbar__left { min-width: 220px; }
.topbar__nav  { flex: 1; min-width: 0; }
.brand { display:flex; gap:12px; align-items:center; text-decoration: none; color: inherit; }

.dot{ width:12px; height:12px; border-radius: 999px; background: var(--accent); box-shadow: 0 0 18px rgba(0,175,239,.55); }
.logo{ font-family: var(--font-en); letter-spacing:.04em; color: #fff; font-weight: 700; }
.sub{ color: rgba(226,232,240,.75); font-size: 12px; margin-top: 2px; }

.topbar__nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 18px;
}

.navlink {
  color: rgba(226,232,240,.75);
  font-size: 18px;
  text-decoration: none;
  white-space: nowrap;
}
.navlink:hover { color: #fff; }
.navlink.is-active { color: #fff; font-weight: 700; }

.topbar__right { display:flex; gap: 8px; align-items: center; }
.lang {
  padding: 4px 8px; border-radius: 8px;
  color: rgba(226,232,240,.75);
  text-decoration: none; font-size: 12px;
}
.lang.is-active { background: rgba(255,255,255,0.10); color: #fff; }


.footer{ color: rgba(226,232,240,.65); font-size: 12px; padding: 18px 20px; border-top: 1px solid rgba(255,255,255,0.08); }

/* 中螢幕：字再小一點 + gap 再小一點 */
@media (max-width: 1100px) {
  .topbar { padding: 10px 16px; }
  .topbar__left { min-width: 180px; }
  .topbar__nav { gap: 12px; }
  .navlink { font-size: 16px; }
}

/* 小螢幕：topbar 改成上下兩排（最穩） */
@media (max-width: 760px) {
  .topbar {
    flex-wrap: wrap;
    align-items: flex-start;
  }
  .topbar__left { width: 100%; min-width: 0; }
  .topbar__nav  { width: 100%; justify-content: flex-start; }
  .topbar__right { margin-left: auto; }
}

</style>