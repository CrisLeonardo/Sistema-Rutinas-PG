import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

// Verifica el artefacto entregable, sin iniciar una API ni una sesión real.
const rutas = ['/', '/como-funciona', '/ejercicios', '/alimentacion', '/comunidad', '/preguntas-frecuentes', '/sobre-el-proyecto', '/privacidad', '/terminos', '/ayuda']
const titulos = new Set()
for (const ruta of rutas) {
  const html = await readFile(ruta === '/' ? 'dist/index.html' : `dist${ruta}/index.html`, 'utf8')
  assert.equal((html.match(/<h1\b/g) || []).length, 1, `${ruta}: falta contenido público antes de ejecutar JS`)
  assert.match(html, /name="robots" content="index, follow"/, ruta)
  const titulo = html.match(/<title>(.*?)<\/title>/)?.[1]
  assert.ok(titulo && !titulos.has(titulo), `${ruta}: título ausente o repetido`)
  titulos.add(titulo)
  assert.ok(!html.includes('Fase 1 / Prototipo'), `${ruta}: se publicó el taller de diseño`)
}
for (const ruta of ['privado.html', 'acceso/index.html', 'registro/index.html', 'panel/index.html', 'recuperar-acceso/index.html', 'restablecer-acceso/index.html']) {
  const html = await readFile(`dist/${ruta}`, 'utf8')
  assert.match(html, /name="robots" content="noindex, nofollow"/, ruta)
  assert.ok(html.includes('<div id="raiz"></div>'), `${ruta}: el armazón privado no debe incluir datos`)
}
const ayuda = await readFile('dist/ayuda/index.html', 'utf8')
assert.match(ayuda, /mailto:/, 'El contacto público debe estar disponible antes de ejecutar JS')
const manifiesto = JSON.parse(await readFile('dist/manifest.webmanifest', 'utf8'))
assert.equal(manifiesto.start_url, '/acceso', 'La aplicación instalada debe abrir el acceso')
assert.equal(manifiesto.id, '/', 'La identidad de la aplicación instalada debe mantenerse')
console.log('Verificado: 10 páginas con contenido, títulos únicos e indexación; 6 armazones privados sin datos; contacto público en HTML.')
