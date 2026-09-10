import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

const BACKEND = process.env.VITE_BACKEND || 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    open: true,
    proxy: {
      '/dify': {
        target: BACKEND,
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes) => {
            if (proxyRes.headers['content-type'] && proxyRes.headers['content-type'].includes('text/event-stream')) {
              proxyRes.headers['cache-control'] = 'no-cache'
            }
          })
        }
      },
      '/api': {
        target: BACKEND,
        changeOrigin: true
      }
    }
  }
})
