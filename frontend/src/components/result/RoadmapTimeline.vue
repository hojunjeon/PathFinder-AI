<template>
  <div class="timeline">
    <div v-for="item in timelineData" :key="item.week" class="timeline-item">
      <div class="timeline-marker">{{ item.week }}주</div>
      <div class="timeline-content card">
        <h3>{{ item.title }}</h3>
        <ul>
          <li v-for="task in item.tasks" :key="task">{{ task }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ timelineData: { type: Array, default: () => [] } })
</script>

<style scoped>
.timeline { position: relative; padding-left: 60px; }
.timeline::before {
  content: ''; position: absolute; left: 24px; top: 0; bottom: 0;
  width: 2px; background: var(--primary);
}
.timeline-item { position: relative; margin-bottom: 1.5rem; }
.timeline-marker {
  position: absolute; left: -48px; width: 36px; height: 36px;
  background: var(--primary); color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 700;
}
.timeline-content h3 { margin-bottom: 0.5rem; font-size: 1rem; }
.timeline-content ul { padding-left: 1.2rem; }
.timeline-content li { font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.2rem; }
</style>
