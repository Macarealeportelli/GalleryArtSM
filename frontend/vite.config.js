import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const backend = 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, // accesible desde otros dispositivos de la red local
    port: 5173,
    proxy: {
      '/api': backend,
      '/uploads': backend
    }
  }
})
