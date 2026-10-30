import test, { before, after } from 'node:test'
import assert from 'node:assert/strict'
import { createServer } from 'vite'
import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { compararComidas, crearTarjetaLogro, segundosRestantes, textoConfirmacionSerie, vibracionHabilitada } from '../src/interaccion/respuestas.mjs'

test('el descanso descuenta tiempo real aun tras suspender una pestaña', () => {
  const fin = 100_000 + 90_000
  assert.equal(segundosRestantes(fin, 100_000), 90)
  assert.equal(segundosRestantes(fin, 147_200), 43)
  assert.equal(segundosRestantes(fin, 250_000), 0)
  assert.equal(segundosRestantes(fin, fin), 0)
})

test('ningún aviso háptico se activa sin elección explícita', () => {
  for (const valor of [null, undefined, '', 'apagada', 'true', 'otro']) assert.equal(vibracionHabilitada(valor), false)
  assert.equal(vibracionHabilitada('encendida'), true)
})

test('confirmar una serie distingue el dispositivo del guardado en el servidor', () => {
  assert.match(textoConfirmacionSerie('Remo', 2, true), /serie 2 anotada en este dispositivo.*Guarde la sesión/)
  assert.match(textoConfirmacionSerie('Remo', 2, false), /desmarcada/)
})

test('comparación conserva cantidades antiguas tras cambiar los objetos del menú', () => {
  const antes = { receta: 'Pollo', energia_kcal: 600, costo_quetzales: null, porciones: [{ nombre: 'Arroz', gramos: 150, estado: 'cocido' }] }
  const despues = { receta: 'Tilapia', energia_kcal: 599, costo_quetzales: 15, porciones: [{ nombre: 'Arroz', gramos: 180, estado: 'cocido' }] }
  const comparacion = compararComidas(antes, despues, 3, 'Almuerzo')
  antes.porciones[0].gramos = 900
  despues.porciones[0].gramos = 950
  assert.equal(comparacion.antes.porciones[0].gramos, 150)
  assert.equal(comparacion.despues.porciones[0].gramos, 180)
  assert.equal(comparacion.antes.costo_quetzales, null)
  assert.equal(comparacion.dia, 3)
})

test('tarjeta compartible incluye solo el nombre de una insignia conseguida', () => {
  const datos = { obtenido: true, nombre: 'Primer paso', correo: 'privado@example.com', peso: 78, notas: 'lesión privada', carga: 90, calorias: 2100, puntos: 400 }
  const tarjeta = crearTarjetaLogro(datos)
  for (const prohibido of ['privado@example.com', 'lesión privada', '2100', '400', '78', '90']) {
    assert.ok(!tarjeta.svg.includes(prohibido))
    assert.ok(!tarjeta.texto.includes(prohibido))
  }
  assert.match(tarjeta.svg, /Primer paso/)
  assert.equal(tarjeta.nombreArchivo, 'senda-insignia.svg')
  assert.ok(!/<(?:image|script|foreignObject)|href=/i.test(tarjeta.svg))
})

test('una insignia bloqueada no produce una tarjeta', () => {
  assert.throws(() => crearTarjetaLogro({ obtenido: false, nombre: 'Pendiente' }))
  assert.throws(() => crearTarjetaLogro({ obtenido: true, nombre: '' }))
})

test('nombres con marcado quedan como texto y no código en SVG', () => {
  const { svg } = crearTarjetaLogro({ obtenido: true, nombre: '<script>alert("x")</script> & acción' })
  assert.ok(!svg.includes('<script>'))
  assert.match(svg, /&lt;script&gt;/)
  assert.ok(!svg.includes('"x"'))
})

let vite
before(async () => { vite = await createServer({ server: { middlewareMode: true }, appType: 'custom', logLevel: 'error' }) })
after(async () => { await vite?.close() })

for (const archivo of ['GraficaLineas', 'GraficaBarras']) test(`${archivo}: cada observación tiene una fila de texto accesible`, async () => {
  const { default: Componente } = await vite.ssrLoadModule(`/src/componentes/${archivo}.jsx`)
  const puntos = Object.freeze([{ etiqueta: '2026-10-01', valor: 72.5 }, { etiqueta: '2026-10-08', valor: 73 }, { etiqueta: '2026-10-15', valor: 72.9 }])
  const html = renderToStaticMarkup(React.createElement(Componente, { puntos, etiquetaValor: 'kg', descripcion: 'Peso de prueba' }))
  assert.match(html, /Ver valores en texto/)
  assert.match(html, /<th scope="col">Fecha<\/th>/)
  assert.equal((html.match(/<th scope="row">/g) ?? []).length, puntos.length)
  for (const p of puntos) assert.ok(html.includes(`${p.valor} kg`))
})

test('una gráfica vacía no inventa una observación', async () => {
  const { default: Grafica } = await vite.ssrLoadModule('/src/componentes/GraficaLineas.jsx')
  const html = renderToStaticMarkup(React.createElement(Grafica, { puntos: [] }))
  assert.match(html, /Todavía no hay datos/)
  assert.ok(!html.includes('<table'))
})

test('comparación de costos incompletos no anuncia un costo cero', async () => {
  const { default: Comparacion } = await vite.ssrLoadModule('/src/componentes/CambioComidaGuardado.jsx')
  const comida = { receta: 'Referencia', costo_quetzales: null, porciones: [] }
  const cambio = { ...compararComidas(comida, comida, 1, 'Cena'), costoSemanaAntes: null, costoSemanaDespues: null }
  const html = renderToStaticMarkup(React.createElement(Comparacion, { cambio }))
  assert.equal((html.match(/Precio incompleto/g) ?? []).length, 4)
  assert.ok(!html.includes('Q0.00'))
})
