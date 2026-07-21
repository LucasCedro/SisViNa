import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'
import { initViewport } from './composables/useViewport'
import './assets/main.css'
import './assets/dialog.css'
import './assets/modal-shell.css'
import './assets/module-panels.css'

initViewport()

const app = createApp(App)

app.use(router)
app.use(pinia)

app.mount('#app')
