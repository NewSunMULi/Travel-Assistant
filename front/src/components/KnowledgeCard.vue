<template>
  <div class="kcard" :class="kind">
    <div class="kcard-head">
      <span class="kcard-id">{{ card.id }}</span>
      <h4 v-if="kind === 'attraction'" class="kcard-title">{{ card.name }}</h4>
      <h4 v-else-if="kind === 'food'" class="kcard-title">{{ card.name }}</h4>
      <h4 v-else class="kcard-title">{{ card.topic }}</h4>
    </div>

    <!-- 景区卡 -->
    <template v-if="kind === 'attraction'">
      <div class="kcard-tags">
        <span class="tag primary">{{ card.type }}</span>
        <span class="tag">体力 {{ card.intensity }}</span>
        <span class="tag" :class="weatherClass">{{ card.weather }}</span>
      </div>
      <dl class="kcard-list">
        <div><dt>推荐时长</dt><dd>{{ card.duration }}</dd></div>
        <div><dt>适合人群</dt><dd>{{ card.audience }}</dd></div>
        <div><dt>门票</dt><dd>{{ card.ticket }}</dd></div>
        <div><dt>开放时间</dt><dd>{{ card.open }}</dd></div>
        <div><dt>交通</dt><dd>{{ card.traffic }}</dd></div>
        <div><dt>位置</dt><dd>{{ card.location }}</dd></div>
      </dl>
      <div class="kcard-pitfall">
        <strong>避坑提示:</strong>{{ card.pitfall }}
      </div>
    </template>

    <!-- 美食卡 -->
    <template v-else-if="kind === 'food'">
      <div class="kcard-tags">
        <span v-for="t in card.tags" :key="t" class="tag purple">{{ t }}</span>
      </div>
      <dl class="kcard-list">
        <div><dt>价格区间</dt><dd>{{ card.price }}</dd></div>
        <div><dt>位置</dt><dd>{{ card.location }}</dd></div>
        <div><dt>适合场景</dt><dd>{{ card.scene }}</dd></div>
      </dl>
      <div class="kcard-reason">
        <strong>推荐理由:</strong>{{ card.reason }}
      </div>
    </template>

    <!-- 避坑卡 -->
    <template v-else>
      <div class="kcard-q">Q: {{ card.question }}</div>
      <div class="kcard-a">A: {{ card.answer }}</div>
    </template>

    <div class="kcard-foot">
      <span class="muted small">来源:{{ card.source }}</span>
      <span class="muted small">更新:{{ card.updatedAt }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  card: { type: Object, required: true },
  kind: { type: String, default: 'attraction' }
})

const weatherClass = computed(() => {
  const w = props.card.weather || ''
  if (w.includes('雨天')) return 'success'
  if (w.includes('晴天')) return 'warning'
  return ''
})
</script>

<style scoped>
.kcard {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: box-shadow var(--transition), transform var(--transition), border-color var(--transition);
}
.kcard:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: var(--border-strong);
}
.kcard-head {
  display: flex;
  align-items: center;
  gap: 8px;
}
.kcard-id {
  font-family: var(--mono);
  font-size: 11px;
  padding: 2px 7px;
  background: var(--surface-2);
  border-radius: 5px;
  color: var(--muted);
}
.kcard-title {
  margin: 0;
  font-size: 15.5px;
  font-weight: 600;
}
.kcard-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.kcard-list {
  margin: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 12px;
}
.kcard-list > div {
  display: flex;
  flex-direction: column;
}
.kcard-list dt {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.kcard-list dd {
  margin: 0;
  font-size: 13px;
  color: var(--text);
}
.kcard-pitfall,
.kcard-reason {
  font-size: 13px;
  background: var(--warning-soft);
  color: var(--warning);
  padding: 8px 12px;
  border-radius: 8px;
  line-height: 1.5;
}
.kcard-reason {
  background: var(--primary-soft);
  color: var(--primary);
}
.kcard-q {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
}
.kcard-a {
  font-size: 13px;
  color: var(--text-soft);
  line-height: 1.7;
}
.kcard-foot {
  display: flex;
  justify-content: space-between;
  border-top: 1px dashed var(--border);
  padding-top: 8px;
  margin-top: auto;
}
.small { font-size: 11px; }
</style>
