<template>
  <div class="human-review">
    <div class="section-title">
      <span class="dot" style="background: var(--warning)"></span>
      <h3>节点 6 · Human Review 人工审核</h3>
      <span class="tag warning">Human-in-the-loop</span>
    </div>
    <p class="muted">
      AI 负责调研与初稿,人负责关键决策。请查看上方候选行程初稿,选择"通过"直接输出,或填写修改意见后由系统重新规划。
    </p>

    <div v-if="verifier" class="verifier-box">
      <div class="verifier-head">
        <span>节点 5 · Verifier 校验结果</span>
        <span class="tag" :class="verifier.passed ? 'success' : 'warning'">
          {{ verifier.passed ? '全部通过' : '需调整' }}
        </span>
      </div>
      <ul class="verifier-list">
        <li v-for="c in verifier.checks" :key="c.item">
          <span class="v-status" :class="c.status">{{ statusText(c.status) }}</span>
          <strong>{{ c.item }}</strong>
          <span class="muted">{{ c.detail }}</span>
        </li>
      </ul>
      <div v-if="verifier.issues.length" class="verifier-issues">
        <strong>待修复问题:</strong>
        <ul>
          <li v-for="i in verifier.issues" :key="i">{{ i }}</li>
        </ul>
      </div>
    </div>

    <div class="review-actions">
      <textarea
        v-model="feedback"
        rows="3"
        placeholder="输入修改意见,如:第三天不要安排太累;预算降到 2500;Day2 西山改为观景台远眺不进山"
      ></textarea>
      <div class="review-buttons">
        <button class="btn primary" @click="onApprove">通过 · 直接输出最终方案</button>
        <button class="btn" @click="onModify">提交修改 · 系统重规划</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  verifier: { type: Object, default: null },
  defaultFeedback: { type: String, default: '' }
})

const emit = defineEmits(['approve', 'modify'])

const feedback = ref(props.defaultFeedback)

function onApprove() {
  emit('approve')
}
function onModify() {
  emit('modify', feedback.value)
}
function statusText(s) {
  return s === 'pass' ? '✓' : s === 'warn' ? '!' : '✕'
}
</script>

<style scoped>
.muted {
  color: var(--muted);
  font-size: 13px;
}
.verifier-box {
  background: var(--surface-soft);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
  margin: 14px 0;
}
.verifier-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  margin-bottom: 10px;
}
.verifier-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.verifier-list li {
  display: grid;
  grid-template-columns: 24px 1fr;
  gap: 8px;
  font-size: 13px;
}
.v-status {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
}
.v-status.pass {
  background: var(--success);
}
.v-status.warn {
  background: var(--warning);
}
.v-status.fail {
  background: var(--danger);
}
.verifier-list li strong {
  font-weight: 600;
  margin-right: 6px;
}
.verifier-issues {
  margin-top: 12px;
  padding: 10px 12px;
  background: var(--warning-soft);
  border-radius: 6px;
  font-size: 13px;
}
.verifier-issues ul {
  margin: 6px 0 0;
  padding-left: 18px;
}
.review-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 14px;
}
textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
  outline: none;
}
textarea:focus {
  border-color: var(--primary);
}
.review-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
