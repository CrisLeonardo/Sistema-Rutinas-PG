import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { join } from 'node:path'
import { createServer } from 'vite'
import react from '@vitejs/plugin-react'

const carpeta = join(process.cwd(), 'dist')
const plantilla = await readFile(join(carpeta, 'privado.html'), 'utf8')
  .catch(() => readFile(join(carpeta, 'index.html'), 'utf8'))
const escapar = valor => valor.replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
const servidor = await createServer({
  configFile: false, mode: 'production', plugins: [react()], optimizeDeps: { noDiscovery: true, entries: [] },
  cacheDir: join(process.cwd(), 'node_modules', '.vite-prerender'),
  ssr: { noExternal: ['react-router-dom', 'react-router'], resolve: { conditions: ['module', 'import', 'production'] } },
  server: { middlewareMode: true }, appType: 'custom',
})
try {
  const { PAGINAS_PUBLICAS, renderizar } = await servidor.ssrLoadModule('/src/publico/renderizar.jsx')
  for (const [ruta, datos] of Object.entries(PAGINAS_PUBLICAS)) {
    const destino = ruta === '/' ? carpeta : join(carpeta, ruta.slice(1))
    await mkdir(destino, { recursive: true })
    const html = plantilla
      .replace(/<title>[^<]*<\/title>/, `<title>${escapar(datos.titulo)}</title>`)
      .replace(/<meta\s+name="description"\s+content="[^"]*"\s*\/>/, `<meta name="description" content="${escapar(datos.descripcion)}" />`)
      .replace('content="noindex, nofollow"', 'content="index, follow"')
      .replace('<div id="raiz"></div>', `<div id="raiz">${renderizar(ruta)}</div>`)
    await writeFile(join(destino, 'index.html'), html)
  }
  // Las rutas privadas arrancan con un armazón vacío y noindex, sin datos personales.
  await writeFile(join(carpeta, 'privado.html'), plantilla)
  for (const ruta of ['acceso', 'registro', 'recuperar-acceso', 'restablecer-acceso', 'bienvenida', 'panel', 'comer', 'entrenar', 'avance', 'mas', 'admin']) {
    await mkdir(join(carpeta, ruta), { recursive: true })
    await writeFile(join(carpeta, ruta, 'index.html'), plantilla)
  }
  await writeFile(join(carpeta, 'robots.txt'), 'User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /prototipo/\n')
  console.log(`HTML público generado: ${Object.keys(PAGINAS_PUBLICAS).length} páginas; armazón privado con noindex.`)
} finally {
  await servidor.close()
}
