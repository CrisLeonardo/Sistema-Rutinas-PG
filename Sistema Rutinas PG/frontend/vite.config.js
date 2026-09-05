import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: 'auto',
      // No cachea llamadas a la API: solo el cascarón de la aplicación (JS,
      // CSS, fuentes e iconos), para que abrir la app instalada sea
      // inmediato aun con mala señal, sin arriesgar datos de ejercicio o
      // nutrición desactualizados.
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,svg,png,woff2}'],
        navigateFallbackDenylist: [/^\/api\//],
      },
      manifest: {
        id: '/',
        name: 'Sistema de Rutinas y Planes Nutricionales',
        short_name: 'Rutinas',
        description:
          'Planes de nutrición y rutinas de entrenamiento personalizadas.',
        lang: 'es',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        background_color: '#070a08',
        theme_color: '#0a0a0d',
        icons: [
          { src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
          {
            src: '/maskable-icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable',
          },
        ],
      },
    }),
  ],
  server: {
    port: 5173,
  },
})
