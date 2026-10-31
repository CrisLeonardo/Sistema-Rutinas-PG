import test, { before, after } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createServer } from 'vite'
import { FICHAS, fichaPara } from '../src/entrenamiento/fichas.mjs'
import { posePara, faseActual, fotogramasPara } from '../src/entrenamiento/movimientos.mjs'
import { recorridoPara, rutaActiva } from '../src/datos/recorridos.mjs'
import { PESTANAS_AVANCE, PESTANAS_ENTRENAR } from '../src/datos/secciones.js'

test('las guías cubren exactamente los 25 ejercicios del catálogo inicial del servidor', () => {
  const catalogo = readFileSync(new URL('../../backend/app/nucleo/catalogo_inicial.py', import.meta.url), 'utf8')
  const equipos = Object.fromEntries([...catalogo.matchAll(/^(EQUIPAMIENTO_[A-Z_]+) = "([^"]+)"/gm)].map(m => [m[1], m[2]]))
  const ejercicios = [...catalogo.matchAll(/\(\s*"([^"]+)",\s*GrupoMuscular\.([A-Z]+),\s*NivelExperiencia\.[A-Z]+,\s*(EQUIPAMIENTO_[A-Z_]+),/g)]
  assert.equal(ejercicios.length, 25)
  for (const [, nombre, grupo, equipo] of ejercicios) assert.ok(fichaPara({ nombre, grupo_muscular: grupo.toLowerCase(), equipamiento: equipos[equipo] }), nombre)
  assert.equal(FICHAS.length, ejercicios.length)
})

test('las guías suspendidas mantienen las manos ancladas a la barra', () => {
  for (const clave of ['dominadas', 'piernas-colgado']) {
    const inicio = posePara(clave, 0)
    for (let i = 0; i <= 100; i++) {
      const pose = posePara(clave, i / 100)
      assert.deepEqual(pose.mano, inicio.mano)
      assert.deepEqual(pose.manoIzq, inicio.manoIzq)
      assert.equal(pose.colgado, true)
    }
  }
})

test('el remo apoyado conserva mano y rodilla de apoyo; la prensa conserva el respaldo', () => {
  const remo = posePara('remo-mancuerna', 0), prensa = posePara('prensa', 0)
  for (let i = 0; i <= 100; i++) {
    const p = i / 100
    assert.deepEqual(posePara('remo-mancuerna', p).manoIzq, remo.manoIzq)
    assert.deepEqual(posePara('remo-mancuerna', p).rodillaTrasera, remo.rodillaTrasera)
    assert.deepEqual(posePara('prensa', p).cadera, prensa.cadera)
    assert.deepEqual(posePara('prensa', p).hombro, prensa.hombro)
  }
})

test('el curl alterno mueve un brazo a la vez y su fase manual muestra una flexión', () => {
  const inicial = posePara('curl-alterno', 0), derecha = posePara('curl-alterno', .25), izquierda = posePara('curl-alterno', .75)
  assert.deepEqual(derecha.manoIzq, inicial.manoIzq)
  assert.notDeepEqual(derecha.mano, inicial.mano)
  assert.deepEqual(izquierda.mano, inicial.mano)
  assert.notDeepEqual(izquierda.manoIzq, inicial.manoIzq)
  const ficha = FICHAS.find(f => f.clave === 'curl-alterno')
  assert.equal(faseActual(fotogramasPara(ficha)[1], ficha), 1)
})

test('el press Arnold identifica el cambio de agarre sin fingir una vista tridimensional', () => {
  assert.equal(posePara('press-arnold', 0).agarre, 'Palmas hacia ti')
  assert.equal(posePara('press-arnold', .5).agarre, 'Palmas al frente')
  assert.equal(posePara('press-arnold', 1).agarre, 'Palmas hacia ti')
})

test('cada recorrido individual y de administración tiene ayuda accionable', () => {
  for (const ruta of ['/panel','/bienvenida','/comer','/comer/semana','/comer/recetas','/comer/preferencias','/comer/plan','/comer/compras','/entrenar','/entrenar/biblioteca','/entrenar/biblioteca/25','/entrenar/42','/entrenar/bitacora','/entrenar/marcas','/avance','/avance/senda','/avance/evolucion','/avance/medidas','/avance/medidas/editar','/avance/informes','/mas','/mas/contrasena','/admin/catalogos','/admin/cuentas','/admin/informes']) {
    const guia = recorridoPara(ruta)
    assert.ok(guia?.titulo && guia.resumen, ruta)
    assert.equal(guia.pasos.length, 3, ruta)
    assert.ok(guia.pasos.every(p => p.length > 20), ruta)
  }
  assert.equal(recorridoPara('/ruta-inexistente'), null)
})

test('la navegación marca la sección más específica en fichas y formularios interiores', () => {
  assert.equal(rutaActiva('/entrenar/biblioteca/25', PESTANAS_ENTRENAR), '/entrenar/biblioteca')
  assert.equal(rutaActiva('/avance/medidas/editar', PESTANAS_AVANCE), '/avance/medidas')
  assert.equal(rutaActiva('/avance', PESTANAS_AVANCE), '/avance')
  assert.equal(rutaActiva('/desconocida', PESTANAS_AVANCE), undefined)
})

let vite
before(async () => { vite = await createServer({ server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' }) })
after(async () => { await vite?.close() })

test('reducir movimiento en Senda detiene el reproductor aunque el sistema permita animaciones', async t => {
  const previoDocumento = globalThis.document, previoMedio = globalThis.matchMedia
  globalThis.document = { documentElement: { dataset: { movimiento: 'reducido' } } }
  globalThis.matchMedia = () => ({ matches: false })
  t.after(() => {
    if (previoDocumento === undefined) delete globalThis.document; else globalThis.document = previoDocumento
    if (previoMedio === undefined) delete globalThis.matchMedia; else globalThis.matchMedia = previoMedio
  })
  const { movimientoReducido } = await vite.ssrLoadModule('/src/interaccion/movimiento.js')
  assert.equal(movimientoReducido(), true)
  globalThis.document.documentElement.dataset.movimiento = 'normal'
  assert.equal(movimientoReducido(), false)
  globalThis.matchMedia = () => ({ matches: true })
  assert.equal(movimientoReducido(), true)
})
