import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { refrescarUsuario } from './auth'
import './styles.css'

refrescarUsuario()
createApp(App).use(router).mount('#app')
