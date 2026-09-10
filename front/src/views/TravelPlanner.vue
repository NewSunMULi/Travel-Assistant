<template>
  <div class="planner-page">
    <header class="page-header">
      <span class="tag purple">🧭 工作流 Agent · v6.1</span>
      <h1>通用旅行助手 · Dify + 高德 API</h1>
      <p class="muted">
        后端 FastAPI <code class="inline-code">:8000</code> + Dify 工作流 SSE 流式调用。
      </p>
      <div class="backend-badge" :class="{ ok: backendAlive, fail: !backendAlive }">
        <span class="dot"></span>
        <span>{{ backendAlive ? '后端已连接' : '后端未连接' }}</span>
      </div>
    </header>

    <section class="card">
      <div class="section-title">
        <span class="dot"></span>
        <h3>s_start · 用户输入 ({{ Object.keys(defaultForm).length }} 个字段)</h3>
      </div>
      <div class="form-grid">
        <div class="form-item form-item-full">
          <label>request 用户请求 *</label>
          <input v-model="form.request" type="text" placeholder="请根据以下信息为我规划旅行行程" />
        </div>
        <div class="form-item">
          <label>destination 目的地 *</label>
          <input v-model="form.destination" type="text" placeholder="昆明" />
        </div>
        <div class="form-item">
          <label>departure 出发地</label>
          <input v-model="form.departure" type="text" placeholder="可选" />
        </div>
        <div class="form-item">
          <label>days 天数 *</label>
          <input v-model.number="form.days" type="number" min="1" max="15" />
        </div>
        <div class="form-item">
          <label>people 人数 *</label>
          <input v-model.number="form.people" type="number" min="1" max="20" />
        </div>
        <div class="form-item">
          <label>budget 预算(元) *</label>
          <input v-model.number="form.budget" type="number" min="500" step="100" />
        </div>
        <div class="form-item">
          <label>style 旅行风格</label>
          <input v-model="form.style" type="text" placeholder="休闲 / 拍照 / 美食 / 亲子" />
        </div>
        <div class="form-item form-item-full">
          <label>special_request 特殊需求 *</label>
          <input v-model="form.special_request" type="text" placeholder="帮我安排完整行程 / 只要简要建议 / 第三天下午返程" />
        </div>
      </div>
      <div class="quick-tags">
        <span class="muted small">快速填充 Demo:</span>
        <button v-for="d in demos" :key="d.label" class="chip" @click="applyDemo(d)">{{ d.label }}</button>
      </div>
      <div class="form-actions">
        <button class="btn primary" :disabled="running || !backendAlive" @click="runAgent">
          <span v-if="running">⏳ Agent 执行中...</span>
          <span v-else>🚀 启动 Agent 规划(完整)</span>
        </button>
        <button class="btn" :disabled="running || !backendAlive" @click="runSimple">💡 简要建议</button>
        <button class="btn ghost" @click="reset">重置</button>
        <button v-if="!backendAlive" class="btn ghost" @click="checkBackend">🔄 检测后端</button>
      </div>
    </section>

    <section v-if="running" class="card generating-card" aria-live="polite">
      <div class="section-title">
        <span class="loading-spinner" aria-hidden="true"></span>
        <h3>正在生成旅行建议，请稍候...</h3>
      </div>
      <p class="muted small">结果完成后会在这里直接显示最终答案。</p>
    </section>

    <section v-if="finalMarkdown && !running" class="card">
      <div class="section-title">
        <span class="dot" style="background: var(--primary)"></span>
        <h3>🎯 最终报告</h3>
        <div class="final-actions">
          <button class="btn ghost small" @click="downloadMd">📄 导出 Markdown</button>
          <button class="btn ghost small" @click="copyMd">📋 复制</button>
        </div>
      </div>
      <div class="md-body final" v-html="renderMd(finalMarkdown)"></div>
    </section>

    <section v-if="errorMsg" class="card error">
      <div class="section-title">
        <span class="dot" style="background: var(--danger)"></span>
        <h3>❌ 运行出错</h3>
      </div>
      <pre class="error-pre">{{ errorMsg }}</pre>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { runWorkflowStream, checkBackendAlive } from '@/api/index.js'

const defaultForm = {
  request: '请根据以下信息为我规划旅行行程',
  destination: '昆明',
  departure: '成都',
  days: 3,
  people: 2,
  budget: 3000,
  style: '休闲',
  special_request: '帮我安排完整行程'
}

const form = reactive({ ...defaultForm })
const running = ref(false)
const backendAlive = ref(false)
const errorMsg = ref('')

const finalMarkdown = ref('')
const textBuf = ref('')

const demos = [
  { label: '昆明 3天2人3000', form: { request: '帮我安排完整行程', destination: '昆明', departure: '成都', days: 3, people: 2, budget: 3000, style: '休闲', special_request: '帮我安排完整行程' } },
  { label: '大理 2天2人2000', form: { request: '帮我安排完整行程', destination: '大理', departure: '昆明', days: 2, people: 2, budget: 2000, style: '拍照', special_request: '简要建议' } },
  { label: '成都 4天3人5000', form: { request: '帮我安排完整行程', destination: '成都', departure: '深圳', days: 4, people: 3, budget: 5000, style: '美食', special_request: '帮我安排完整行程' } },
  { label: '北京 3天2人4000', form: { request: '帮我安排完整行程', destination: '北京', departure: '上海', days: 3, people: 2, budget: 4000, style: '亲子', special_request: '帮我安排完整行程' } }
]

function applyDemo(d) {
  Object.assign(form, d.form)
}

async function checkBackend() {
  backendAlive.value = await checkBackendAlive()
}

onMounted(checkBackend)

function reset(resetForm = true) {
  if (resetForm) Object.assign(form, defaultForm)
  running.value = false
  finalMarkdown.value = ''
  textBuf.value = ''
  errorMsg.value = ''
}

async function runAgent() {
  reset(false)
  running.value = true
  await runReal()
}

async function runSimple() {
  reset(false)
  running.value = true
  form.request = '请根据以下信息给出简要旅行建议'
  form.special_request = '只要简要建议'
  await runReal()
}

async function runReal() {
  await runWorkflowStream(form, {
    onTextChunk: (txt) => {
      textBuf.value += txt
    },
    onWorkflowFinish: ({ outputs, error }) => {
      if (error) {
        errorMsg.value = JSON.stringify(error, null, 2)
        finalMarkdown.value = ''
      } else {
        const text = outputs?.text || outputs?.output || ''
        finalMarkdown.value = text || textBuf.value
      }
      running.value = false
    },
    onError: (e) => {
      errorMsg.value = String(e)
      running.value = false
    }
  })
}

function renderMd(md) {
  if (!md) return ''
  let html = String(md)
  const imageTokens = []

  // Markdown 图片必须先占位，否则后续的粗体、换行替换可能破坏 alt/title 属性。
  // 同时接受普通 URL 和 `<URL with spaces>` 两种 Markdown 写法。
  html = html.replace(
    /!\[([^\]]*)\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+["']([^"']*)["'])?\s*\)/g,
    (match, alt, angleUrl, plainUrl, title) => {
      const url = angleUrl || plainUrl
      if (!isSafeImageUrl(url)) return escapeHtml(match)

      const titleAttr = title ? ` title="${escapeHtml(title)}"` : ''
      const image = `<img src="${escapeHtml(url)}" alt="${escapeHtml(alt)}"${titleAttr} loading="lazy" decoding="async" referrerpolicy="no-referrer">`
      const token = `\u0000IMAGE_${imageTokens.length}\u0000`
      imageTokens.push(image)
      return token
    }
  )
  html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
  html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>')
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>')
  html = html.replace(/^\|(.+)\|$/gm, (m) => {
    const cells = m.split('|').slice(1, -1).map(c => c.trim())
    const tag = /^-+/.test(cells[0] || '') ? '' : (cells.length > 2 ? '<tr>' : '')
    if (!tag) return ''
    return '<tr>' + cells.map((c, i) => i === 0 ? `<th>${c}</th>` : `<td>${c}</td>`).join('') + '</tr>'
  })
  html = html.replace(/\n\n/g, '</p><p>')
  html = html.replace(/\u0000IMAGE_(\d+)\u0000/g, (_, index) => imageTokens[Number(index)] || '')
  return '<div class="md-body-inner"><p>' + html + '</p></div>'
}

function isSafeImageUrl(value) {
  const url = String(value || '').trim()
  if (!url) return false

  // 支持后端的相对文件地址、常规网络图片，以及 Markdown 中常见的 base64 图片。
  if (/^(?:\/|\.\/|\.\.\/)/.test(url)) return true
  if (/^data:image\/(?:png|jpe?g|gif|webp|svg\+xml);base64,[a-z0-9+/=\s]+$/i.test(url)) return true

  try {
    return ['http:', 'https:', 'blob:'].includes(new URL(url, window.location.origin).protocol)
  } catch {
    return false
  }
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function downloadMd() {
  const blob = new Blob([finalMarkdown.value], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `travel_plan_${Date.now()}.md`
  a.click()
  URL.revokeObjectURL(url)
}

function copyMd() {
  navigator.clipboard?.writeText(finalMarkdown.value)
}
</script>

<style scoped>
.planner-page { display: flex; flex-direction: column; gap: 16px; }
.page-header h1 { margin-top: 6px; }
.page-header p { max-width: 760px; }
.backend-badge {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 12px; padding: 4px 10px; border-radius: 12px;
  margin-top: 8px; font-weight: 600;
  background: var(--surface-2); border: 1px solid var(--border);
}
.backend-badge.ok .dot { background: #22c55e; }
.backend-badge.fail .dot { background: var(--danger); }
.form-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 14px; margin: 14px 0;
}
@media (max-width: 720px) { .form-grid { grid-template-columns: 1fr 1fr; } }
.form-item { display: flex; flex-direction: column; gap: 6px; }
.form-item-full { grid-column: 1 / -1; }
.form-item label {
  font-size: 12px; color: var(--muted); font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.04em;
}
.form-actions { display: flex; gap: 10px; margin-top: 4px; flex-wrap: wrap; }
.quick-tags {
  display: flex; align-items: center; gap: 8px;
  flex-wrap: wrap; margin-bottom: 12px;
}
.chip {
  font-size: 12px; padding: 4px 10px; border-radius: 14px;
  background: var(--surface-2); border: 1px solid var(--border);
  color: var(--text-soft); cursor: pointer; transition: all 0.15s ease;
}
.chip:hover { background: var(--primary-soft); color: var(--primary); border-color: var(--primary); }

.inline-code {
  background: var(--surface-2); padding: 1px 6px; border-radius: 4px;
  font-family: var(--mono, monospace); font-size: 12px;
}

.generating-card .section-title { margin-bottom: 4px; }
.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--primary-soft);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.final-actions { display: flex; gap: 6px; }
.btn.small { font-size: 12px; padding: 4px 10px; }

.md-body { font-size: 14px; line-height: 1.7; color: var(--text); }
.md-body.small { font-size: 13px; line-height: 1.6; }
.md-body.final { font-size: 14px; }
.md-body-inner :deep(h2) { margin: 18px 0 8px; font-size: 18px; color: var(--primary); }
.md-body-inner :deep(h3) { margin: 16px 0 8px; font-size: 16px; color: var(--primary); }
.md-body-inner :deep(h4) { margin: 12px 0 6px; font-size: 14px; color: var(--text); }
.md-body-inner :deep(li) { margin: 3px 0; list-style: disc; }
.md-body-inner :deep(strong) { color: var(--text); }
.md-body-inner :deep(pre) {
  background: var(--surface-2); padding: 10px; border-radius: 8px;
  overflow-x: auto; font-family: var(--mono); font-size: 12px;
}
.md-body-inner :deep(code) {
  background: var(--surface-2); padding: 1px 6px; border-radius: 4px;
  font-family: var(--mono); font-size: 12px;
}
.md-body-inner :deep(table) {
  border-collapse: collapse; margin: 10px 0; font-size: 13px; width: 100%;
}
.md-body-inner :deep(th), .md-body-inner :deep(td) {
  border: 1px solid var(--border); padding: 6px 10px; text-align: left;
}
.md-body-inner :deep(th) { background: var(--surface-2); }
.md-body-inner :deep(img) {
  display: block;
  width: auto;
  max-width: 80%;
  height: auto;
  max-height: 560px;
  margin: 12px auto;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  object-fit: contain;
  background: var(--surface-2);
}

.card.error { border-color: var(--danger); }
.error-pre {
  background: var(--surface-2); padding: 12px; border-radius: 8px;
  color: var(--danger); font-family: var(--mono); font-size: 12px;
  overflow-x: auto; max-height: 300px; white-space: pre-wrap;
}
</style>
