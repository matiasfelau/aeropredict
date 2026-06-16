import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// El backend (FastAPI) permite CORS desde http://localhost:3000, por eso el
// servidor de desarrollo se fija en ese puerto. La URL del backend se
// configura con VITE_API_URL (ver .env.example).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
  },
  preview: {
    port: 3000,
  },
})
