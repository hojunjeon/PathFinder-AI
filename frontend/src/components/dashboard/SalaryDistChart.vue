<template>
  <div class="chart-card card">
    <div class="chart-header">
      <h3>연봉 구간별 공고 분포</h3>
      <button id="download-chart-d" class="btn-outline small" @click="download">📥 PNG</button>
    </div>
    <p class="insight">💡 1억 이상 공고가 전체의 약 46% — 고연봉 포지션이 다수 포함된 데이터셋</p>
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
    type: 'bar',
    data: {
      labels: props.chartData.labels,
      datasets: [{
        label: '공고 수',
        data: props.chartData.data,
        backgroundColor: [
          'rgba(16,185,129,0.8)', 'rgba(5,150,105,0.8)', 'rgba(4,120,87,0.8)',
          'rgba(6,95,70,0.8)', 'rgba(59,130,246,0.8)', 'rgba(37,99,235,0.8)', 'rgba(29,78,216,0.8)',
        ],
        borderWidth: 0,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
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
    text: '연봉 구간별 공고 분포',
    color: text,
    font: { size: 16, weight: 'bold', family: 'sans-serif' },
    padding: { top: 10, bottom: 20 }
  }
  chart.options.scales.x.title = {
    ...chart.options.scales.x.title,
    display: true,
    text: '연봉 구간',
    color: text,
    font: { weight: 'bold' }
  }
  chart.options.scales.y.title = {
    ...chart.options.scales.y.title,
    display: true,
    text: '공고 수 (개)',
    color: text,
    font: { weight: 'bold' }
  }

  chart.update('none')

  const url = chart.toBase64Image('image/png', 1.0)
  const a = document.createElement('a')
  a.href = url
  a.download = 'salary-dist-chart.png'
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
