<template>
  <div class="card" :class="{ 'has-image': hasImage }">
    <div class="img-wrap" :class="{ placeholder: !hasImage }">
      <img v-if="hasImage" :src="item.image_url" :alt="item.name" loading="lazy" />
      <div v-else class="ph">
        <span class="ph-icon">🖼️</span>
        <span>图片待核实</span>
      </div>
      <div class="rating" v-if="item.rating && item.rating !== '评分待核实'">
        <span class="star">★</span>
        {{ item.rating }}
      </div>
    </div>
    <div class="body">
      <div class="name" :title="item.name">{{ item.name }}</div>
      <div class="addr" :title="item.address">{{ item.address }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  item: { type: Object, required: true }
})
const hasImage = computed(() =>
  props.item.image_url &&
  typeof props.item.image_url === 'string' &&
  props.item.image_url.startsWith('http')
)
</script>

<style scoped>
.card {
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface);
  overflow: hidden;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  display: flex;
  flex-direction: column;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}
.img-wrap {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  background: var(--surface-soft);
  overflow: hidden;
}
.img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.img-wrap.placeholder .ph {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--muted);
  font-size: 12px;
  background: repeating-linear-gradient(
    45deg,
    var(--surface-soft),
    var(--surface-soft) 10px,
    var(--surface-2) 10px,
    var(--surface-2) 20px
  );
}
.ph-icon { font-size: 28px; }
.rating {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.65);
  color: #ffd54f;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}
.rating .star { margin-right: 2px; }
.body {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.addr {
  font-size: 12px;
  color: var(--muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
