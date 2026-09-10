<template>
  <div class="kb-page">
    <header class="page-header">
      <span class="tag primary">阶段 1</span>
      <h1>昆明旅游知识问答(RAG)</h1>
      <p class="muted">
        基于 KB1 景区 / KB2 美食 / KB3 避坑 三个知识库的混合检索,所有回答
        <strong>必须引用来源</strong>,资料不足时明确拒答。
      </p>
    </header>

    <div class="kb-layout">
      <!-- 左侧:提问 + 回答 -->
      <section class="kb-main">
        <div class="card ask-card">
          <div class="section-title"><span class="dot"></span><h3>向知识库提问</h3></div>
          <div class="ask-row">
            <input
              v-model="query"
              type="text"
              placeholder="例:昆明下雨天适合去哪?/ 石林和滇池哪个更顺路?/ 两个人 3000 怎么玩?"
              @keyup.enter="runSearch"
            />
            <button class="btn primary" :disabled="loading" @click="runSearch">
              {{ loading ? '检索中...' : '检索回答' }}
            </button>
          </div>
          <div class="quick-questions">
            <span class="muted">常见问题:</span>
            <button
              v-for="q in quickQuestions"
              :key="q"
              class="chip"
              @click="setQuery(q)"
            >{{ q }}</button>
          </div>
        </div>

        <div v-if="answer" class="card answer-card">
          <div class="section-title">
            <span class="dot" style="background: var(--success)"></span>
            <h3>RAG 回答</h3>
            <span v-if="answer.refused" class="tag warning">资料不足 · 拒答</span>
          </div>
          <p v-if="answer.refused" class="refuse">
            知识库未覆盖该问题,系统拒绝回答,避免幻觉。请补充资料或换一种问法。
          </p>
          <template v-else>
            <p class="answer-text">{{ answer.text }}</p>
            <div class="citations">
              <span class="muted">引用来源卡片:</span>
              <span v-for="c in answer.citations" :key="c.id" class="citation-chip">
                <strong>{{ c.id }}</strong> · {{ c.label }}
              </span>
            </div>
          </template>
        </div>

        <div v-if="resultCards.length" class="card result-cards">
          <div class="section-title">
            <span class="dot" style="background: var(--purple)"></span>
            <h3>命中的知识卡片({{ resultCards.length }})</h3>
          </div>
          <div class="cards-grid">
            <KnowledgeCard v-for="c in resultCards" :key="c.id" :card="c" :kind="searchKind" />
          </div>
        </div>
      </section>

      <!-- 右侧:过滤 + 知识库概览 -->
      <aside class="kb-side">
        <div class="card filter-card">
          <div class="section-title"><span class="dot" style="background: var(--warning)"></span><h3>元数据过滤</h3></div>
          <div class="filter-group">
            <label>知识库</label>
            <div class="filter-opts">
              <button
                v-for="k in kinds"
                :key="k.value"
                class="chip"
                :class="{ active: filter.kind === k.value }"
                @click="filter.kind = k.value"
              >{{ k.label }}</button>
            </div>
          </div>
          <template v-if="filter.kind === 'attraction'">
            <div class="filter-group">
              <label>适合天气</label>
              <div class="filter-opts">
                <button
                  v-for="w in weatherOpts"
                  :key="w"
                  class="chip"
                  :class="{ active: filter.weather === w }"
                  @click="filter.weather = filter.weather === w ? '' : w"
                >{{ w }}</button>
              </div>
            </div>
            <div class="filter-group">
              <label>体力强度</label>
              <div class="filter-opts">
                <button
                  v-for="i in intensityOpts"
                  :key="i"
                  class="chip"
                  :class="{ active: filter.intensity === i }"
                  @click="filter.intensity = filter.intensity === i ? '' : i"
                >{{ i }}</button>
              </div>
            </div>
            <div class="filter-group">
              <label>类型</label>
              <div class="filter-opts">
                <button
                  v-for="t in typeOpts"
                  :key="t"
                  class="chip"
                  :class="{ active: filter.type === t }"
                  @click="filter.type = filter.type === t ? '' : t"
                >{{ t }}</button>
              </div>
            </div>
          </template>
        </div>

        <div class="card stats-card">
          <div class="section-title"><span class="dot"></span><h3>知识库概览</h3></div>
          <ul class="stats">
            <li><span class="num">{{ attractions.length }}</span><span class="label">景区卡 KB1</span></li>
            <li><span class="num">{{ foods.length }}</span><span class="label">美食卡 KB2</span></li>
            <li><span class="num">{{ pitfalls.length }}</span><span class="label">避坑卡 KB3</span></li>
          </ul>
          <p class="muted small">数据为本地 mock,对应 needed.md 中"20~30 景点卡、15~20 美食卡、10~20 避坑卡"的最小可行范围。</p>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { attractions } from '@/data/attractions.js'
import { foods } from '@/data/foods.js'
import { pitfalls } from '@/data/pitfalls.js'
import KnowledgeCard from '@/components/KnowledgeCard.vue'

const query = ref('')
const loading = ref(false)
const answer = ref(null)
const resultCards = ref([])

const filter = reactive({
  kind: 'attraction',
  weather: '',
  intensity: '',
  type: ''
})

const kinds = [
  { value: 'attraction', label: '景区 KB1' },
  { value: 'food', label: '美食 KB2' },
  { value: 'pitfall', label: '避坑 KB3' }
]
const weatherOpts = ['晴天更佳', '均可', '雨天首选']
const intensityOpts = ['低', '中', '高']
const typeOpts = ['自然景观', '城市公园', '人文古迹', '室内文博', '自然地质', '民俗文化', '城市地标', '城市市集', '商业休闲']

const searchKind = computed(() => filter.kind)

const quickQuestions = [
  '昆明下雨天适合去哪?',
  '石林和滇池哪个更顺路?',
  '第一次来昆明有哪些避坑点?',
  '适合拍照又轻松的景点',
  '预算 3000 怎么玩?',
  '情侣适合去哪?'
]

function setQuery(q) {
  query.value = q
  runSearch()
}

function runSearch() {
  if (!query.value.trim()) return
  loading.value = true
  answer.value = null
  resultCards.value = []
  // 模拟检索延迟
  setTimeout(() => {
    const q = query.value.toLowerCase()
    const kind = filter.kind

    if (kind === 'attraction') {
      const cards = attractions.filter((c) => {
        let ok = true
        if (filter.weather) ok = ok && c.weather === filter.weather
        if (filter.intensity) ok = ok && c.intensity === filter.intensity
        if (filter.type) ok = ok && c.type === filter.type
        if (q) {
          ok =
            ok &&
            (c.name.includes(query.value) ||
              c.type.includes(query.value) ||
              c.audience.includes(query.value) ||
              c.weather.includes(query.value) ||
              c.intensity.includes(query.value) ||
              matchesKeyword(q, c))
        }
        return ok
      })
      finishSearch(cards, 'attraction')
    } else if (kind === 'food') {
      const cards = foods.filter((c) => {
        if (!q) return true
        return (
          c.name.includes(query.value) ||
          c.tags.some((t) => t.includes(query.value)) ||
          c.scene.includes(query.value) ||
          c.location.includes(query.value)
        )
      })
      finishSearch(cards, 'food')
    } else {
      const cards = pitfalls.filter((c) => {
        if (!q) return true
        return (
          c.topic.includes(query.value) ||
          c.question.includes(query.value) ||
          c.answer.includes(query.value)
        )
      })
      finishSearch(cards, 'pitfall')
    }
    loading.value = false
  }, 500)
}

function matchesKeyword(q, c) {
  const keywords = ['下雨', '雨天', '室内', '拍照', '情侣', '轻松', '低体力', '预算']
  for (const k of keywords) {
    if (q.includes(k)) {
      if (k === '下雨' || k === '雨天' || k === '室内') {
        return c.weather === '雨天首选' || c.weather === '均可'
      }
      if (k === '拍照' || k === '情侣') return c.audience.includes('情侣') || c.audience.includes('摄影')
      if (k === '轻松' || k === '低体力') return c.intensity === '低'
      if (k === '预算') return true
    }
  }
  return false
}

function finishSearch(cards, kind) {
  resultCards.value = cards
  if (cards.length === 0) {
    answer.value = { refused: true, text: '', citations: [] }
    return
  }
  // 生成带引用的回答
  let text = ''
  const citations = cards.slice(0, 4).map((c) => ({
    id: c.id,
    label: c.name || c.topic
  }))
  if (kind === 'attraction') {
    text =
      `根据 KB1 景区知识库检索到 ${cards.length} 条相关结果。` +
      cards
        .slice(0, 3)
        .map((c) => `${c.name}(${c.type},推荐时长 ${c.duration},体力 ${c.intensity},适合天气:${c.weather})`)
        .join('; ') +
      `。建议结合天气与体力强度选择。`
  } else if (kind === 'food') {
    text =
      `根据 KB2 美食知识库检索到 ${cards.length} 条相关结果。` +
      cards
        .slice(0, 3)
        .map((c) => `${c.name}(人均 ${c.price},场景:${c.scene})`)
        .join('; ') +
      `。`
  } else {
    text =
      `根据 KB3 避坑知识库检索到 ${cards.length} 条相关结果。` +
      cards
        .slice(0, 3)
        .map((c) => `【${c.topic}】${c.answer.slice(0, 40)}...`)
        .join('  ')
  }
  answer.value = { refused: false, text, citations }
}
</script>

<style scoped>
.kb-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.page-header h1 { margin-top: 6px; }
.page-header p { max-width: 720px; }

.kb-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
  align-items: start;
}
@media (max-width: 960px) { .kb-layout { grid-template-columns: 1fr; } }

.kb-main {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ask-row {
  display: flex;
  gap: 10px;
}
.ask-row input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  font-size: 14px;
  outline: none;
  background: var(--surface);
  color: var(--text);
  transition: border-color var(--transition), box-shadow var(--transition);
}
.ask-row input:focus {
  border-color: var(--primary);
  box-shadow: var(--ring);
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}

.answer-text {
  font-size: 14.5px;
  line-height: 1.85;
  background: var(--surface-2);
  padding: 16px 18px;
  border-radius: var(--radius);
  border-left: 3px solid var(--primary);
}
.refuse {
  color: var(--warning);
  background: var(--warning-soft);
  padding: 14px 16px;
  border-radius: var(--radius);
  font-size: 14px;
}
.citations {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.citation-chip {
  font-size: 12.5px;
  padding: 4px 10px;
  background: var(--primary-soft);
  color: var(--primary);
  border-radius: 6px;
}
.citation-chip strong {
  font-family: var(--mono);
}

.cards-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
@media (max-width: 640px) { .cards-grid { grid-template-columns: 1fr; } }

.kb-side {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 66px;
}
.filter-group { margin-bottom: 14px; }
.filter-group label {
  display: block;
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 6px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.filter-opts {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.stats {
  list-style: none;
  padding: 0;
  margin: 0;
}
.stats li {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px dashed var(--border);
}
.stats li:last-child { border-bottom: none; }
.stats .num {
  font-weight: 700;
  color: var(--primary);
  font-size: 18px;
}
.small { font-size: 12px; margin-top: 10px; }
</style>
