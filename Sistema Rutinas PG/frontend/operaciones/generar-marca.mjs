// Genera PNG desde el SVG aprobado; no dibuja otra versión del símbolo.
// node operaciones/generar-marca.mjs [--modulos RUTA_A_NODE_MODULES]
import { createRequire } from 'node:module'
import { writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { iconoSendaSVG, trazosCaminoSVG, VERSION_MARCA } from '../src/marca/identidad.mjs'

const require = createRequire(import.meta.url)
const indice = process.argv.indexOf('--modulos')
const rutas = indice < 0 ? [] : [process.argv[indice + 1]]
const sharp = require(require.resolve('sharp', { paths: [...rutas, process.cwd()] }))
const publico = fileURLToPath(new URL('../public/', import.meta.url))
await writeFile(`${publico}/favicon.svg`, `${iconoSendaSVG()}\n`)
await writeFile(`${publico}/favicon-camino.svg`, `${iconoSendaSVG()}\n`)
await writeFile(`${publico}/marca-senda.svg`, `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Senda, símbolo Camino">${trazosCaminoSVG()}</svg>\n`)
for (const [nombre, tamaño, maskable] of [
  ['favicon-96x96.png', 96, false], ['apple-touch-icon.png', 180, true],
  ['pwa-192x192.png', 192, false], ['pwa-512x512.png', 512, false],
  ['maskable-icon-512x512.png', 512, true],
]) {
  const png = await sharp(Buffer.from(iconoSendaSVG({ maskable }))).resize(tamaño, tamaño).png().toBuffer()
  await writeFile(`${publico}/${nombre}`, png)
  await writeFile(`${publico}/${nombre.replace('.png', '-camino.png')}`, png)
}
console.log(`Marca ${VERSION_MARCA}: SVG, favicon y cinco PNG generados.`)
