<template>
  <div class="itinerary-card">
    <div class="day-head">
      <span class="day-badge">Day {{ day.day }}</span>
      <span class="day-date">{{ day.date }}</span>
      <span class="tag" :class="weatherTagClass">{{ day.weather }}</span>
      <span v-if="isFinal" class="tag success">最终版</span>
    </div>
    <div class="day-grid">
      <div v-for="slot in slots" :key="slot.key" class="slot" :class="{ empty: !day[slot.key].place || day[slot.key].place === '—' }">
        <div class="slot-time">{{ slot.label }}</div>
        <div class="slot-place">
          {{ day[slot.key].place || '—' }}
        </div>
        <div v-if="day[slot.key].note && day[slot.key].place !== '—'" class="slot-note">
          {{ day[slot.key].note }}
        </div>
        <span v-if="day[slot.key].citation" class="slot-cite">{{ day[slot.key].citation }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  day: { type: Object, required: true },
  isFinal: { type: Boolean, default: false }
})

const slots = [
  { key: 'morning', label: '上午' },
  { key: 'noon', label: '中午' },
  { key: 'afternoon', label: '下午' },
  { key: 'evening', label: '晚上' }
]

const weatherTagClass = computed(() => {
  if (props.day.weather.includes('雨')) return 'warning'
  if (props.day.weather.includes('晴')) return 'primary'
  return ''
})
</script>

<style scoped>
.itinerary-card {
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  overflow: hidden;
}
.day-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: linear-gradient(90deg, var(--primary-soft), transparent);
  border-bottom: 1px solid var(--border);
}
.day-badge {
  background: var(--primary);
  color: #fff;
  font-weight: 700;
  font-size: 13px;
  padding: 3px 10px;
  border-radius: 6px;
}
.day-date {
  font-size: 14px;
  color: var(--text-soft);
  font-weight: 600;
}
.day-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
}
@media (max-width: 720px) {
  .day-grid {
    grid-template-columns: 1fr 1fr;
  }
}
.slot {
  padding: 14px;
  border-right: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.slot.empty {
  background: var(--surface-soft);
}
.slot-time {
  font-size: 11px;
  color: var(--muted);
  font-weight: 600;
}
.slot-place {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}
.slot-note {
  font-size: 12px;
  color: var(--text-soft);
  line-height: 1.5;
}
.slot-cite {
  margin-top: auto;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--primary);
  background: var(--primary-soft);
  padding: 1px 6px;
  border-radius: 4px;
  align-self: flex-start;
}
</style>
