<template>
  <div class="agent-flow">
    <div class="section-title"><span class="dot"></span><h3>Agent 工作流 · 通用旅行助手</h3></div>
    <div class="flow-track">
      <div
        v-for="(step, idx) in steps"
        :key="step.key"
        class="flow-step"
        :class="{ active: current === idx, done: current > idx, error: getStatus(step.name) === 'error' }"
      >
        <div class="flow-icon">
          <span v-if="current > idx" class="check">✓</span>
          <span v-else class="icon-emoji">{{ step.icon }}</span>
        </div>
        <div class="flow-text">
          <strong>{{ step.name }}</strong>
          <small>{{ step.node }} · {{ step.desc }}</small>
        </div>
        <div v-if="idx < steps.length - 1" class="flow-line" :class="{ done: current > idx }"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  steps: { type: Array, required: true },
  current: { type: Number, default: 0 },
  nodeStatus: { type: Object, default: () => ({}) }
})

function getStatus(name) {
  return props.nodeStatus?.[name]
}
</script>

<style scoped>
.flow-track {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0;
}
.flow-step {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0 0 auto;
  padding-right: 4px;
}
.flow-icon {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--surface-2);
  color: var(--muted);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  border: 2px solid var(--border);
  flex-shrink: 0;
}
.flow-step.active .flow-icon {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px var(--primary-soft);
  animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 4px var(--primary-soft); }
  50% { box-shadow: 0 0 0 8px transparent; }
}
.flow-step.done .flow-icon {
  background: var(--success);
  color: #fff;
  border-color: var(--success);
}
.flow-step.error .flow-icon {
  background: var(--danger);
  color: #fff;
  border-color: var(--danger);
}
.check { font-size: 14px; }
.icon-emoji { line-height: 1; }
.flow-text {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
  max-width: 180px;
}
.flow-text strong {
  font-size: 13px;
  color: var(--text);
}
.flow-text small {
  font-size: 11px;
  color: var(--muted);
  line-height: 1.4;
}
.flow-line {
  width: 20px;
  height: 2px;
  background: var(--border);
  margin: 0 2px;
  margin-top: 16px;
  flex-shrink: 0;
}
.flow-line.done { background: var(--success); }
@media (max-width: 760px) {
  .flow-step { width: 100%; margin-bottom: 10px; }
  .flow-line { display: none; }
}
</style>
