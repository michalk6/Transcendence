import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // Przegladarka widzi tylko localhost:5173. Vite przekazuje /api/* do Django,
    // dzieki czemu nie ma zapytan cross-origin i nie potrzebujemy CORS po stronie backendu.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
