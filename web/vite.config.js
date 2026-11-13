import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// base: GitHub Pages serves the site at /Leaktrace/; dev and local preview use /.
export default defineConfig({
  base: process.env.PAGES_BASE || '/',
  plugins: [react()],
  server: { proxy: { '/api': 'http://localhost:8000' } },
})
