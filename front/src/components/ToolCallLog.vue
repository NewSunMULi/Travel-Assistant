<template>
  <div class="tool-log">
    <div class="section-title">
      <span class="dot" style="background: var(--purple)"></span>
      <h3>🔧 节点执行日志</h3>
      <span class="tag purple">{{ calls.length }} 个节点</span>
    </div>
    <div class="calls">
      <details v-for="c in calls" :key="c.id" class="call" :open="c.status !== 'success' && c.status !== 'running'">
        <summary>
          <span class="call-status" :class="c.status">●</span>
          <span v-if="c.status === 'running'" class="call-spinner">⟳</span>
          <span class="call-name">{{ c.name }}</span>
          <span class="call-node">{{ c.node }}</span>
          <span class="call-type" :class="c.type">{{ typeLabel(c.type) }}</span>
        </summary>
        <div v-if="c.outputs" class="call-body">
          <div class="call-block">
            <span class="muted small">输出</span>
            <pre>{{ formatJson(c.outputs) }}</pre>
          </div>
        </div>
      </details>
    </div>
  </div>
</template>

<script setup>
defineProps({
  calls: { type: Array, required: true }
})

function formatJson(obj) {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

function typeLabel(t) {
  const m = {
    code: 'Code',
    'http-request': 'HTTP API',
    llm: 'LLM',
    'question-classifier': '分类器',
    'knowledge-retrieval': '知识库',
    'if-else': '条件分支',
    'variable-aggregator': '合并'
  }
  return m[t] || t
}
</script>

<style scoped>
.calls {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.call {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0;
}
.call summary {
  list-style: none;
  cursor: pointer;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.call summary::-webkit-details-marker {
  display: none;
}
.call-status {
  color: var(--muted);
  font-size: 10px;
}
.call-status.success {
  color: var(--success);
}
.call-status.fail {
  color: var(--danger);
}
.call-status.running {
  color: var(--primary);
}
.call-spinner {
  font-size: 13px;
  color: var(--primary);
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.call-name {
  font-weight: 600;
  font-size: 14px;
}
.call-node {
  font-family: var(--mono);
  font-size: 11px;
  padding: 1px 6px;
  background: var(--surface-2);
  color: var(--text-soft);
  border-radius: 4px;
}
.call-type {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 4px;
  font-weight: 600;
}
.call-type.code { background: #0d1117; color: #79c0ff; }
.call-type.http-request { background: #fff7ed; color: #c2410c; }
.call-type.llm { background: var(--purple-soft); color: var(--purple); }
.call-type.question-classifier { background: var(--primary-soft); color: var(--primary); }
.call-type.knowledge-retrieval { background: var(--warning-soft); color: var(--warning); }
.call-time {
  margin-left: auto;
  font-size: 12px;
  color: var(--muted);
  font-family: var(--mono);
}
.call-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 14px 14px;
}
.call-api {
  background: var(--surface-soft);
  padding: 8px 12px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}
.call-api code {
  font-family: var(--mono);
  color: var(--primary);
}
.call-block pre {
  margin: 4px 0 0;
  background: #0d1117;
  color: #e6edf3;
  padding: 10px;
  border-radius: 6px;
  font-size: 11.5px;
  overflow-x: auto;
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
}
.small {
  font-size: 11px;
}
</style>
