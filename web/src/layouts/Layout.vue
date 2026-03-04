<template>
  <div class="app">

    <main class="container">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const lang = computed(() => (String(route.path).split('/')[1] === 'en' ? 'en' : 'zh'))


</script>

<style scoped>
.app { min-height: 100vh; }
.topbar {
  position: sticky; top: 0; z-index: 50;
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  background: rgba(2, 6, 23, 0.75);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.topbar__left { display:flex; align-items: baseline; gap: 10px; min-width: 260px; }
.brand { color: #fff; font-weight: 700; text-decoration: none; letter-spacing: .5px; }
.sub { color: rgba(226,232,240,.75); font-size: 12px; }

.topbar__nav { display:flex; flex-wrap: wrap; gap: 14px; justify-content: center; }
.navlink { color: rgba(226,232,240,.75); font-size: 13px; text-decoration: none; }
.navlink:hover { color: #fff; }
.navlink.is-active { color: #fff; font-weight: 700; }

.topbar__right { display:flex; gap: 8px; align-items: center; }
.lang {
  padding: 4px 8px; border-radius: 8px;
  color: rgba(226,232,240,.75);
  text-decoration: none; font-size: 12px;
}
.lang.is-active { background: rgba(255,255,255,0.10); color: #fff; }

.container { max-width: 1100px; margin: 0 auto; padding: 20px 16px; }
</style>