import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import KnowledgeQA from '@/views/KnowledgeQA.vue'
import TravelPlanner from '@/views/TravelPlanner.vue'

const routes = [
  { path: '/', name: 'home', component: Home, meta: { title: '首页' } },
  { path: '/kb', name: 'knowledge', component: KnowledgeQA, meta: { title: '昆明知识库问答' } },
  { path: '/planner', name: 'planner', component: TravelPlanner, meta: { title: '通用旅行助手 · 酒店景点图片版' } }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.afterEach((to) => {
  const base = '昆明智能旅行决策 Agent'
  document.title = to.meta.title ? `${to.meta.title} · ${base}` : base
})

export default router
