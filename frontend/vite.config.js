import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import process from 'node:process'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const target = env.VITE_BACKEND_URL || 'http://127.0.0.1:8011';

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/processes': {
          target: target,
          changeOrigin: true,
        },
        '/health': {
          target: target,
          changeOrigin: true,
        },
        '/stats': {
          target: target,
          changeOrigin: true,
        },
        '/history': {
          target: target,
          changeOrigin: true,
        },
        '/settings': {
          target: target,
          changeOrigin: true,
        },
        '/sql': {
          target: target,
          changeOrigin: true,
        },
        '/openapi.json': {
          target: target,
          changeOrigin: true,
        },
      },
    },
  }
})
