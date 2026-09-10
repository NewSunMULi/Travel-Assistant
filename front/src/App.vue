<template>
  <div class="app-layout">
    <header class="topbar">
      <div class="topbar-title">🧭 Dify 旅游规划助手</div>
      <button class="icon-btn" @click="toggleTheme" :title="isDark ? '切换浅色' : '切换深色'">
        <svg v-if="isDark" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
        </svg>
        <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      </button>
    </header>

    <main class="app-main">
      <TravelPlanner />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import TravelPlanner from '@/views/TravelPlanner.vue'

const isDark = ref(true)

function applyTheme() {
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  localStorage.setItem('travelcopilot-theme', isDark.value ? 'dark' : 'light')
}

function toggleTheme() {
  isDark.value = !isDark.value
  applyTheme()
}

onMounted(() => {
  const saved = localStorage.getItem('travelcopilot-theme')
  if (saved) {
    isDark.value = saved === 'dark'
  } else {
    isDark.value = true
  }
  applyTheme()
})

watch(isDark, applyTheme)
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: var(--bg);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 40;
  height: 52px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(10px);
}
.topbar-title {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--text-soft);
  transition: all var(--transition);
}
.icon-btn:hover {
  background: var(--surface-2);
  color: var(--text);
}

.app-main {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 28px 60px;
}

@media (max-width: 760px) {
  .app-main {
    padding: 20px 16px 60px;
  }
}
</style>
