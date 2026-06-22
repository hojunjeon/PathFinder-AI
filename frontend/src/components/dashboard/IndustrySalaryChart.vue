<template>
  <div class="chart-card card">
    <div class="chart-header">
      <h3>산업별 평균 연봉 vs 평균 지원자 수</h3>
      <button id="download-chart-a" class="btn-outline small" @click="download">📥 PNG</button>
    </div>
    <p class="insight">💡 콘텐츠·미디어는 낮은 연봉에도 높은 경쟁률, 항공·우주는 반대 경향</p>
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

function getColors() {
  return {
    text: themeStore.isDark ? '#f1f5f9' : '#212529',
    grid: themeStore.isDark ? '#334155' : '#e9ecef',
  }
}

function createChart() {
  if (chart) chart.destroy()
  if (!props.chartData?.labels?.length) return
  const { text, grid } = getColors()
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
      datasets: [
        {
          label: '평균 연봉 (만원)',
          data: props.chartData.salaries,
          backgroundColor: 'rgba(59,130,246,0.75)',
          yAxisID: 'y',
        },
        {
          label: '평균 지원자 수 (명)',
          data: props.chartData.applicants,
          backgroundColor: 'rgba(239,68,68,0.75)',
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { labels: { color: text } } },
      scales: {
        x: { ticks: { color: text, maxRotation: 45 }, grid: { color: grid } },
        y: {
          type: 'linear', position: 'left',
          title: { display: true, text: '연봉(만원)', color: text },
          ticks: { color: text }, grid: { color: grid },
        },
        y1: {
          type: 'linear', position: 'right',
          title: { display: true, text: '지원자수(명)', color: text },
          ticks: { color: text }, grid: { display: false },
        },
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
  const originalY1TitleDisplay = chart.options.scales.y1?.title?.display || false
  const text = themeStore.isDark ? '#f1f5f9' : '#212529'

  chart.options.plugins.title = {
    ...chart.options.plugins.title,
    display: true,
    text: '산업별 평균 연봉 vs 평균 지원자 수',
    color: text,
    font: { size: 16, weight: 'bold', family: 'sans-serif' },
    padding: { top: 10, bottom: 20 }
  }
  chart.options.scales.x.title = {
    ...chart.options.scales.x.title,
    display: true,
    text: '산업',
    color: text,
    font: { weight: 'bold' }
  }
  chart.options.scales.y.title = {
    ...chart.options.scales.y.title,
    display: true,
    text: '연봉(만원)',
    color: text,
    font: { weight: 'bold' }
  }
  if (chart.options.scales.y1) {
    chart.options.scales.y1.title = {
      ...chart.options.scales.y1.title,
      display: true,
      text: '지원자수(명)',
      color: text,
      font: { weight: 'bold' }
    }
  }

  chart.update('none')

  const url = chart.toBase64Image('image/png', 1.0)
  const a = document.createElement('a')
  a.href = url
  a.download = 'industry-salary-chart.png'
  a.click()

  if (chart.options.plugins.title) chart.options.plugins.title.display = originalTitleDisplay
  if (chart.options.scales.x.title) chart.options.scales.x.title.display = originalXTitleDisplay
  if (chart.options.scales.y.title) chart.options.scales.y.title.display = originalYTitleDisplay
  if (chart.options.scales.y1?.title) chart.options.scales.y1.title.display = originalY1TitleDisplay

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
