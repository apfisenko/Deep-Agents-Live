import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';

// Оба пути проксируются на devstand-сервер drill-модуля (:8123).
// NB: dev-сервер Vite слушает ::1 — браузером ходить на localhost, не 127.0.0.1.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5273,
    strictPort: true,
    proxy: {
      '/drill': {target: 'http://127.0.0.1:8123', changeOrigin: true},
      '/devstand': {target: 'http://127.0.0.1:8123', changeOrigin: true},
    },
  },
  optimizeDeps: {
    include: ['@a2ui/react', 'react', 'react-dom'],
  },
});
