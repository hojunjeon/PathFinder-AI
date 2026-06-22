<template>
  <div class="chart-card card">
    <div class="chart-header">
      <h3>경력 연수별 평균 지원자 수 추이</h3>
      <button id="download-chart-c" class="btn-outline small" @click="download">📥 PNG</button>
    </div>
    <p class="insight">💡 경력 0→3년: 지원자 급감 구간. 3년 이상부터는 완만하게 감소</p>
    <canvas ref="canvasRef" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Chart } from 'chart.js'
import { useThemeStore } from '../../stores/theme'

const props = defineProps({ chartData: Object })
const canvasRef = ref(null)
const themeStore = useThemeStore()
let chart = null

function createChart() {
  if (chart) chart.destroy()
  if (!props.chartData?.labels?.length) return
  const text = themeStore.isDark ? '#f1f5f9' : '#212529'
  const grid = themeStore.isDark ? '#334155' : '#e9ecef'
  const backgroundPlugin = {
    id: 'customCanvasBackgroundColor',
    beforeDraw: (chart) => {
      const { ctx } = chart;
      ctx.save();
      ctx.globalCompositeOperation = 'destination-over';
      ctx.fillStyle = themeStore.isDark ? '#1e293b' : '#ffffff';
      ctx.fillRect(0, 0, chart.width, chart.height);
      ctx.restore();
    }
  }
  chart = new Chart(canvasRef.value, {
    type: 'line',
    data: {
      labels: props.chartData.labels,
      datasets: [{
        label: '평균 지원자 수',
        data: props.chartData.data,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59,130,246,0.12)',
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 7,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: text } } },
      scales: {
        x: { ticks: { color: text }, grid: { color: grid } },
        y: { ticks: { color: text }, grid: { color: grid } },
      },
    },
    plugins: [backgroundPlugin],
  })
}

onMounted(createChart)
watch(() => [props.chartData, themeStore.isDark], createChart, { deep: true })
onUnmounted(() => chart?.destroy())

function download() {
  if (!chart) return
  
  const originalTitleDisplay = chart.options.plugins.title?.display || false
  const originalXTitleDisplay = chart.options.scales.x.title?.display || false
  const originalYTitleDisplay = chart.options.scales.y.title?.display || false
  const text = themeStore.isDark ? '#f1f5f9' : '#212529'

  chart.options.plugins.title = {
    ...chart.options.plugins.title,
    display: true,
    text: '경력 연수별 평균 지원자 수 추이',
    color: text,
    font: { size: 16, weight: 'bold', family: 'sans-serif' },
    padding: { top: 10, bottom: 20 }
  }
  chart.options.scales.x.title = {
    ...chart.options.scales.x.title,
    display: true,
    text: '경력 연수',
    color: text,
    font: { weight: 'bold' }
  }
  chart.options.scales.y.title = {
    ...chart.options.scales.y.title,
    display: true,
    text: '평균 지원자 수 (명)',
    color: text,
    font: { weight: 'bold' }
  }

  chart.update('none')

  const url = chart.toBase64Image('image/png', 1.0)
  const a = document.createElement('a')
  a.href = url
  a.download = 'experience-trend-chart.png'
  a.click()

  if (chart.options.plugins.title) chart.options.plugins.title.display = originalTitleDisplay
  if (chart.options.scales.x.title) chart.options.scales.x.title.display = originalXTitleDisplay
  if (chart.options.scales.y.title) chart.options.scales.y.title.display = originalYTitleDisplay

  chart.update('none')
}
</script>

<style scoped>
.chart-card { margin-bottom: 1rem; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.chart-header h3 { font-size: 0.95rem; }
.insight { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.8rem; }
.small { font-size: 0.78rem; padding: 0.2rem 0.6rem; }
</style>
