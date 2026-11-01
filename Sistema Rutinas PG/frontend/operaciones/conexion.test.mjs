import test, { before, after } from 'node:test'
import assert from 'node:assert/strict'
import { createServer } from 'vite'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { crearMonitorConexion, resolverUrlApi, sesionRechazada } from '../src/servicios/conexion.mjs'
import { cargarRecursos } from '../src/servicios/recursos.mjs'

const salud = () => Response.json({ estado: 'disponible' })

test('producción usa su dominio si falta la variable; desarrollo conserva el puerto documentado', () => {
  assert.equal(resolverUrlApi(undefined, true), '/api/v1')
  assert.equal(resolverUrlApi('', true), '/api/v1')
  assert.equal(resolverUrlApi(undefined, false), 'http://127.0.0.1:8010/api/v1')
  assert.equal(resolverUrlApi(' https://api.example/api/v1/ ', true), 'https://api.example/api/v1')
})

test('la portada y el acceso comparten una sola comprobación, sin credenciales', async () => {
  let liberar, llamadas = 0
  const monitor = crearMonitorConexion({ url: '/api/v1', solicitar: (url, opciones) => {
    llamadas++
    assert.equal(url, '/api/v1/estado')
    assert.equal(opciones.cache, 'no-store')
    assert.equal(opciones.headers.Authorization, undefined)
    assert.equal(opciones.body, undefined)
    return new Promise(resolve => { liberar = () => resolve(salud()) })
  } })
  const primera = monitor.comprobar(), segunda = monitor.comprobar()
  assert.equal(primera, segunda)
  assert.equal(monitor.leer().fase, 'conectando')
  monitor.fallo('Otra consulta encontró un fallo temporal')
  assert.equal(monitor.comprobar(), primera)
  assert.equal(monitor.leer().fase, 'conectando')
  liberar()
  assert.equal(await primera, true)
  assert.equal(await monitor.comprobar(), true)
  assert.equal(llamadas, 1)
  assert.equal(monitor.leer().fase, 'disponible')
})

test('un arranque con 503 se recupera repitiendo solo salud', async () => {
  let llamadas = 0
  const monitor = crearMonitorConexion({ url: '/api/v1', pausa: 1, plazo: 100,
    solicitar: async () => ++llamadas === 1 ? new Response('', { status: 503 }) : salud() })
  assert.equal(await monitor.comprobar(), true)
  assert.equal(llamadas, 2)
})

test('un 200 HTML del proxy nunca se considera una API disponible', async () => {
  let llamadas = 0
  const monitor = crearMonitorConexion({ url: '/api/v1', solicitar: async () => {
    llamadas++
    return new Response('<html>Senda</html>', { headers: { 'Content-Type': 'text/html' } })
  } })
  assert.equal(await monitor.comprobar(), false)
  assert.equal(monitor.leer().fase, 'sin-conexion')
  assert.equal(llamadas, 1)
})

test('una respuesta de salud que no termina tiene plazo y permite volver a conectar', async () => {
  let disponible = false
  const monitor = crearMonitorConexion({ url: '/api/v1', pausa: 1, plazo: 30, porIntento: 10,
    solicitar: async (_url, { signal }) => disponible ? salud() : ({ ok: true, headers: new Headers({ 'Content-Type': 'application/json' }),
      json: () => new Promise((_resolve, reject) => signal.addEventListener('abort', () => reject(new DOMException('Tiempo', 'AbortError')))) }) })
  assert.equal(await monitor.comprobar(), false)
  assert.equal(monitor.leer().fase, 'sin-conexion')
  disponible = true
  assert.equal(await monitor.comprobar(), true)
})

test('los fallos temporales no invalidan una sesión; un rechazo explícito sí', () => {
  for (const codigo of [0, 404, 409, 429, 500, 502, 503, undefined]) assert.equal(sesionRechazada({ codigo }), false)
  for (const codigo of [401, 403]) assert.equal(sesionRechazada({ codigo }), true)
})

test('el panel conserva los recursos disponibles sin confundir un fallo con ausencia', async () => {
  const fallo = new Error('No se pudo consultar la rutina')
  const datos = await cargarRecursos({ plan: Promise.resolve({ calorias_objetivo: 2100 }), rutina: Promise.reject(fallo), perfil: Promise.resolve(null) })
  assert.deepEqual(datos.plan, { calorias_objetivo: 2100 })
  assert.equal(datos.rutina, null)
  assert.equal(datos.fallos.rutina, fallo)
  assert.equal(Object.hasOwn(datos.fallos, 'perfil'), false)
})

let vite, api, Ficha
before(async () => {
  vite = await createServer({ server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' })
  api = await vite.ssrLoadModule('/src/servicios/api.js')
  Ficha = (await vite.ssrLoadModule('/src/entrenamiento/FichaEjercicio.jsx')).default
})
after(async () => { await vite?.close() })

test('una escritura con fallo de red se envía una sola vez', async t => {
  let llamadas = 0
  t.mock.method(globalThis, 'fetch', async () => { llamadas++; throw new TypeError('Sin red') })
  await assert.rejects(api.peticion('/progreso', { metodo: 'POST', datos: { peso_kg: 75 } }), error => error.codigo === 0)
  assert.equal(llamadas, 1)
})

test('el cliente detecta HTML en lugar de JSON y muestra un error legible', async t => {
  t.mock.method(globalThis, 'fetch', async () => new Response('<html>Iniciando</html>', { headers: { 'Content-Type': 'text/html' } }))
  await assert.rejects(api.peticion('/rutina'), /página en lugar de los datos/)
})

test('un informe que recibe HTML no se descarga como si fuera un archivo válido', async t => {
  t.mock.method(globalThis, 'fetch', async () => new Response('<html>Iniciando</html>', { headers: { 'Content-Type': 'text/html' } }))
  await assert.rejects(api.descargarArchivo('/informes/personal/pdf'), /página en lugar de los datos/)
})

test('el plazo cubre también la lectura del cuerpo, no solo los encabezados', async t => {
  let leyendo
  t.mock.method(globalThis, 'fetch', async (_url, { signal }) => ({ ok: true, status: 200,
    headers: new Headers({ 'Content-Type': 'application/json' }),
    json: () => { leyendo = true; return new Promise((_resolve, reject) => signal.addEventListener('abort', () => reject(new DOMException('Tiempo', 'AbortError')))) } }))
  t.mock.timers.enable({ apis: ['setTimeout'] })
  const pendiente = api.peticion('/rutina')
  await Promise.resolve()
  assert.equal(leyendo, true)
  t.mock.timers.tick(30_000)
  await assert.rejects(pendiente, /consulta tardó demasiado/)
})

test('la ficha normal ofrece la guía animada y muestra su revisión técnica', async () => {
  const { FICHAS } = await import('../src/entrenamiento/fichas.mjs')
  const html = renderToStaticMarkup(React.createElement(Ficha, { ejercicio: FICHAS[0] }))
  assert.match(html, /Guía esquemática animada/)
  assert.match(html, /revisión técnica: Entrenador del Gimnasio FAMAS, octubre de 2026/)
  assert.doesNotMatch(html, /pendiente de revisión técnica/)
  assert.doesNotMatch(html, /vista estática/)
})

test('movimiento reducido muestra tres posiciones y desactiva la reproducción', async t => {
  const anterior = globalThis.matchMedia
  globalThis.matchMedia = () => ({ matches: true })
  t.after(() => { if (anterior === undefined) delete globalThis.matchMedia; else globalThis.matchMedia = anterior })
  const { FICHAS } = await import('../src/entrenamiento/fichas.mjs')
  const Demo = (await vite.ssrLoadModule('/src/entrenamiento/DemostracionEjercicio.jsx')).default
  const html = renderToStaticMarkup(React.createElement(Demo, { ficha: FICHAS[0], permitirReproducir: true }))
  assert.equal((html.match(/<figcaption>/g) ?? []).length, 3)
  assert.match(html, /Movimiento reducido activo/)
  assert.match(html, /disabled=""/)
  assert.doesNotMatch(html, /En movimiento/)
})

test('la plancha sigue siendo un sostén y no ofrece ciclos de repetición', async () => {
  const { FICHAS } = await import('../src/entrenamiento/fichas.mjs')
  const Demo = (await vite.ssrLoadModule('/src/entrenamiento/DemostracionEjercicio.jsx')).default
  const html = renderToStaticMarkup(React.createElement(Demo, { ficha: FICHAS.find(f => f.esIsometrico), permitirReproducir: true }))
  assert.match(html, /Sin repeticiones/)
  assert.doesNotMatch(html, /Pausar|Ver movimiento/)
})
