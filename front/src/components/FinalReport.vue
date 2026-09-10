<template>
  <div class="final-report">
    <div class="section-title">
      <span class="dot" style="background: var(--success)"></span>
      <h3>🎯 最终方案 · n99_end</h3>
      <span class="tag success">可执行 · 已完成</span>
    </div>

    <div class="report-meta">
      <span class="meta-item"><strong>目的地:</strong>{{ form.destination }}</span>
      <span class="meta-item"><strong>出发地:</strong>{{ form.departure || '—' }}</span>
      <span class="meta-item"><strong>天数:</strong>{{ form.days }} 天</span>
      <span class="meta-item"><strong>人数:</strong>{{ form.people }} 人</span>
      <span class="meta-item"><strong>总预算:</strong>{{ form.budget }} 元</span>
      <span class="meta-item"><strong>风格:</strong>{{ form.style }}</span>
      <span class="meta-item"><strong>需求:</strong>{{ form.special_request }}</span>
    </div>

    <div class="md-body main-md" v-html="renderMarkdown(markdown)"></div>

    <div class="grid-2">
      <div class="block">
        <h4 class="block-title">🏖️ 推荐景点卡片</h4>
        <div class="spot-grid">
          <div v-for="(s, i) in spots.slice(0, 6)" :key="'rs'+i" class="spot-mini">
            <div class="sm-img" :class="{ ph: !hasImg(s.image_url) }">
              <img v-if="hasImg(s.image_url)" :src="s.image_url" :alt="s.name" loading="lazy" />
              <span v-else>🖼️</span>
            </div>
            <div class="sm-body">
              <div class="sm-name">{{ s.name }}</div>
              <div class="sm-rating">★ {{ s.rating }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="block">
        <h4 class="block-title">🏨 推荐酒店卡片</h4>
        <div class="spot-grid">
          <div v-for="(h, i) in hotels.slice(0, 4)" :key="'rh'+i" class="spot-mini">
            <div class="sm-img" :class="{ ph: !hasImg(h.image_url) }">
              <img v-if="hasImg(h.image_url)" :src="h.image_url" :alt="h.name" loading="lazy" />
              <span v-else>🖼️</span>
            </div>
            <div class="sm-body">
              <div class="sm-name">{{ h.name }}</div>
              <div class="sm-rating">★ {{ h.rating }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="block">
      <h4 class="block-title">📅 每日行程 + 天气 + 预算</h4>
      <div class="itinerary-list">
        <div v-for="d in itinerary" :key="d.day" class="day-card">
          <div class="dc-head">
            <span class="dc-day">{{ d.day }}</span>
            <span class="dc-date">{{ d.date }}</span>
            <span class="dc-weather" :class="weatherClass(d.weather)">{{ weatherIcon(d.weather) }} {{ d.weather }}</span>
            <span class="dc-temp">🌡️ {{ d.temperature }}</span>
            <span class="dc-budget">💰 {{ d.budget }} 元</span>
          </div>
          <div class="dc-grid">
            <div v-for="slot in ['morning', 'noon', 'afternoon', 'evening']" :key="slot" class="dc-slot" :class="{ empty: !d[slot]?.place || d[slot].place === '—' }">
              <div class="dc-slot-label">{{ slotLabel(slot) }}</div>
              <div class="dc-place">{{ d[slot]?.place || '—' }}</div>
              <div class="dc-note" v-if="d[slot]?.note">{{ d[slot].note }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid-2">
      <div class="block">
        <h4 class="block-title">💰 预算汇总</h4>
        <table class="b-table">
          <thead><tr><th>项目</th><th>金额(元)</th><th>占比</th></tr></thead>
          <tbody>
            <tr v-for="(v, k) in budget.allocation" :key="k">
              <td>{{ k }}</td>
              <td>{{ v }}</td>
              <td>
                <div class="pb-wrap"><div class="pb-bar" :style="{ width: (v / budget.total_budget * 100) + '%' }"></div></div>
              </td>
            </tr>
          </tbody>
          <tfoot><tr><td>合计</td><td>{{ budget.total_budget }}</td><td>100%</td></tr></tfoot>
        </table>
      </div>
      <div class="block">
        <h4 class="block-title">⚠️ 约束检查 & 待核实</h4>
        <ul class="warn-list">
          <li v-for="(w, i) in warnings" :key="'w'+i">{{ w }}</li>
        </ul>
        <div class="check-summary">
          <div class="cs-item"><strong>日均预算:</strong>{{ budget.per_day_total }} 元</div>
          <div class="cs-item"><strong>人均日:</strong>{{ budget.per_person_per_day }} 元</div>
          <div class="cs-item"><strong>天数:</strong>{{ budget.days }} 天</div>
          <div class="cs-item"><strong>预算状态:</strong><span class="tag success">已估算</span></div>
        </div>
      </div>
    </div>

    <div class="export-row">
      <button class="btn primary" @click="exportMd">📄 导出 Markdown</button>
      <button class="btn" @click="exportTxt">📝 导出纯文本</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  form: { type: Object, required: true },
  itinerary: { type: Array, required: true },
  weather: { type: Array, required: true },
  budget: { type: Object, required: true },
  spots: { type: Array, default: () => [] },
  hotels: { type: Array, default: () => [] },
  markdown: { type: String, default: '' },
  warnings: { type: Array, default: () => [] }
})

function hasImg(url) {
  return url && typeof url === 'string' && url.startsWith('http')
}

function slotLabel(s) {
  return { morning: '上午', noon: '中午', afternoon: '下午', evening: '晚上' }[s]
}

function weatherIcon(w) {
  if (!w) return '🌤️'
  if (w.includes('雨')) return '🌧️'
  if (w.includes('晴')) return '☀️'
  if (w.includes('云')) return '⛅'
  return '🌤️'
}

function weatherClass(w) {
  if (!w) return ''
  if (w.includes('雨')) return 'rain'
  if (w.includes('晴')) return 'sun'
  return 'cloud'
}

function renderMarkdown(md) {
  let html = md
  html = html.replace(/^## (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>')
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (m, alt, url) => hasImg(url) ? `<img class="md-img" src="${url}" alt="${alt}" />` : `<span class="md-ph">🖼️ 图片待核实</span>`)
  html = html.replace(/\|(.+)\|\n\|[-|:\s]+\|\n/g, (m, head) => {
    const cols = head.split('|').map(c => c.trim()).filter(Boolean)
    return '<table class="md-table"><thead><tr>' + cols.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>'
  })
  html = html.replace(/^\|(.+)\|$/gm, (m, row) => {
    const cells = row.split('|').map(c => c.trim()).filter(Boolean)
    return '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>'
  })
  html = html.replace(/<\/tr>\s*<\/thead>/g, '</tr></thead><tbody>')
  html = html.replace(/<\/tr>\s*<tbody>\s*<\/tbody>/g, '</tr></tbody></table>')
  html = html.replace(/\n\n/g, '</p><p>')
  return '<p>' + html + '</p>'
}

function download(filename, content, type = 'text/plain') {
  const blob = new Blob([content], { type: `${type};charset=utf-8` })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function exportMd() {
  download(`${props.form.destination}旅行方案.md`, props.markdown, 'text/markdown')
}
function exportTxt() {
  download(`${props.form.destination}旅行方案.txt`, props.markdown)
}
</script>

<style scoped>
.report-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  background: var(--surface-soft);
  padding: 12px 16px;
  border-radius: 10px;
  margin-bottom: 18px;
  font-size: 13px;
}
.meta-item strong { color: var(--muted); margin-right: 4px; font-weight: 600; }

.main-md {
  font-size: 14px;
  line-height: 1.75;
  color: var(--text);
  margin-bottom: 18px;
}
.main-md h3 {
  margin: 18px 0 8px;
  font-size: 16px;
  color: var(--primary);
  border-bottom: 1px solid var(--border);
  padding-bottom: 6px;
}
.main-md h4 { margin: 14px 0 6px; font-size: 14px; color: var(--text); }
.main-md li { margin: 3px 0; }
.main-md strong { color: var(--text); }
.main-md .md-img { max-width: 100%; border-radius: 8px; margin: 8px 0; }
.main-md .md-ph { display: inline-block; padding: 2px 8px; background: var(--surface-2); border-radius: 4px; font-size: 12px; color: var(--muted); }
.main-md table.md-table { width: 100%; border-collapse: collapse; font-size: 13px; margin: 8px 0; }
.main-md table.md-table th, .main-md table.md-table td { padding: 6px 10px; border: 1px solid var(--border); text-align: left; }
.main-md table.md-table th { background: var(--surface-2); }

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 14px;
}
@media (max-width: 760px) { .grid-2 { grid-template-columns: 1fr; } }
.block { margin-top: 4px; }
.block-title { margin: 0 0 10px; font-size: 14px; color: var(--text); }

.spot-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.spot-mini {
  display: flex;
  gap: 10px;
  padding: 8px;
  background: var(--surface-soft);
  border-radius: 8px;
  border: 1px solid var(--border);
}
.sm-img {
  width: 64px;
  height: 64px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--surface-2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.sm-img img { width: 100%; height: 100%; object-fit: cover; }
.sm-img.ph { color: var(--muted); }
.sm-body { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; gap: 2px; }
.sm-name { font-size: 13px; font-weight: 600; color: var(--text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sm-rating { font-size: 12px; color: #ffd54f; }

.itinerary-list { display: flex; flex-direction: column; gap: 12px; }
.day-card {
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  overflow: hidden;
}
.dc-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: linear-gradient(90deg, var(--primary-soft), transparent);
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
}
.dc-day {
  background: var(--primary);
  color: #fff;
  font-weight: 700;
  font-size: 13px;
  padding: 3px 10px;
  border-radius: 6px;
}
.dc-date { font-size: 13px; color: var(--text-soft); font-weight: 600; }
.dc-weather { font-size: 12px; padding: 2px 8px; border-radius: 10px; }
.dc-weather.sun { background: #fef3c7; color: #d97706; }
.dc-weather.rain { background: #dbeafe; color: #2563eb; }
.dc-weather.cloud { background: #f3f4f6; color: #6b7280; }
.dc-temp { font-size: 12px; color: var(--muted); }
.dc-budget { font-size: 12px; color: var(--success); font-weight: 600; margin-left: auto; }
.dc-grid { display: grid; grid-template-columns: repeat(4, 1fr); }
@media (max-width: 720px) { .dc-grid { grid-template-columns: 1fr 1fr; } }
.dc-slot {
  padding: 14px;
  border-right: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.dc-slot:last-child { border-right: none; }
.dc-slot.empty { background: var(--surface-soft); }
.dc-slot-label { font-size: 11px; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.dc-place { font-size: 14px; font-weight: 600; color: var(--text); }
.dc-note { font-size: 12px; color: var(--text-soft); line-height: 1.5; }

.b-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.b-table th, .b-table td { padding: 8px 10px; border-bottom: 1px solid var(--border); text-align: left; }
.b-table th { background: var(--surface-2); font-weight: 600; }
.b-table tfoot td { font-weight: 700; background: var(--surface-soft); }
.pb-wrap { height: 8px; background: var(--surface-2); border-radius: 4px; overflow: hidden; }
.pb-bar { height: 100%; background: linear-gradient(90deg, var(--primary), var(--purple)); border-radius: 4px; }

.warn-list { margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 6px; font-size: 13px; color: var(--text-soft); }
.check-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 12px;
  padding: 12px;
  background: var(--surface-soft);
  border-radius: 8px;
  font-size: 12px;
}
.cs-item strong { color: var(--muted); margin-right: 4px; }

.export-row { display: flex; gap: 10px; margin-top: 20px; }
</style>
