import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'
import './assets/main.css'
import './assets/dialog.css'
import './assets/module-panels.css'

const app = createApp(App)

app.use(router)
app.use(pinia)

app.mount('#app')
