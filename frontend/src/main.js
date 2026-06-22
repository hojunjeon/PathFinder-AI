import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { Chart, BarController, BarElement, LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend, Filler } from 'chart.js'
import App from './App.vue'
import router from './router'
import './style.css'

Chart.register(BarController, BarElement, LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend, Filler)

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
