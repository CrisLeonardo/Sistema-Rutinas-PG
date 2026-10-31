import test from 'node:test'
import assert from 'node:assert/strict'
import { FICHAS, GRUPOS, animacionPublicable, fichaPara, filtrarEjercicios } from '../src/entrenamiento/fichas.mjs'
import { avanzar, faseActual, posePara, CLAVES_MOVIMIENTO } from '../src/entrenamiento/movimientos.mjs'

test('ningún borrador se anuncia como técnicamente validado', () => {
  assert.equal(FICHAS.length, 25)
  assert.equal(new Set(FICHAS.map(f => f.clave)).size, 25)
  for (const ficha of FICHAS) {
    assert.equal(animacionPublicable(ficha), false)
    assert.equal(ficha.validacion.responsable, null)
    assert.equal(ficha.validacion.fecha, null)
    assert.equal(ficha.fases.length, 3)
    assert.ok(ficha.version && ficha.preparadaEl && ficha.autoria && ficha.licencia)
    assert.ok(new URL(ficha.fuente.url).protocol === 'https:')
  }
})
test('registrar la validación técnica exige estado, responsable y fecha', () => {
  const ficha = FICHAS[0]
  assert.equal(animacionPublicable({ ...ficha, validacion: { estado: 'revisada' } }), false)
  assert.equal(animacionPublicable({ ...ficha, validacion: { estado: 'revisada', responsable: 'Revisor', fecha: '2026-10-30' } }), true)
})
test('IDs locales distintos conservan la vinculación; otro nombre o equipo no la heredan', () => {
  const ficha = FICHAS[0]
  assert.equal(fichaPara({ ...ficha, id: 909 }), ficha)
  for (const cambios of [{ nombre: ficha.nombre + ' inclinado' }, { equipamiento: 'Máquina' }, { grupo_muscular: 'pierna' }]) {
    assert.equal(fichaPara({ ...ficha, ...cambios }), null)
  }
})
test('consulta normaliza tildes y combina filtros sin mostrar bajas', () => {
  const catalogo = FICHAS.map((f, i) => ({ ...f, id: i + 1, disponible_localmente: true }))
  catalogo[8].disponible_localmente = false
  assert.equal(filtrarEjercicios(catalogo, { busqueda: 'jalon polea' })[0].clave, 'jalon-pecho')
  assert.equal(filtrarEjercicios(catalogo, { busqueda: 'biceps' }).length, 0)
  assert.deepEqual(filtrarEjercicios(catalogo, { grupo: 'pecho', equipo: 'Peso corporal' }).map(f => f.clave), ['lagartijas'])
  assert.equal(filtrarEjercicios(catalogo, { grupo: 'inexistente' }).length, 0)
  assert.equal(filtrarEjercicios([{ nombre: 'Personalizado', disponible_localmente: true }], { soloGuias: true }).length, 0)
})
test('consultar una ficha no muta prescripción, carga ni catálogo', () => {
  const ejercicio = Object.freeze({ ...FICHAS[4], series: 3, carga: 25, descanso: 90 })
  const copia = JSON.stringify(ejercicio)
  fichaPara(ejercicio)
  filtrarEjercicios([ejercicio])
  assert.equal(JSON.stringify(ejercicio), copia)
})
test('la sesión usa las etiquetas del servidor y conserva la ficha exacta', () => {
  for (const ficha of FICHAS) {
    const ejercicioSesion = { ejercicio_id: 305, nombre: ficha.nombre, grupo_muscular: GRUPOS[ficha.grupo_muscular], equipamiento: ficha.equipamiento }
    assert.equal(fichaPara(ejercicioSesion), ficha)
    assert.equal(fichaPara({ ...ejercicioSesion, grupo_muscular: 'Cuerpo completo' }), null)
  }
})
test('cada ficha tiene un movimiento explícito; el desconocido usa texto', () => {
  assert.deepEqual([...CLAVES_MOVIMIENTO].sort(), FICHAS.map(f => f.clave).sort())
  assert.equal(posePara('inventado'), null)
})
test('reproducción termina en un ciclo, con velocidades y pasos válidos', () => {
  assert.equal(avanzar(0, 6000), 1)
  assert.equal(avanzar(0, 6000, .5), .5)
  assert.equal(avanzar(.99, 500, 1.5), 1)
  assert.equal(avanzar(.5, -500), .5)
  assert.deepEqual([0, .5, 1].map(faseActual), [0, 1, 2])
})
for (const ficha of FICHAS) test(`${ficha.nombre}: posiciones dentro del lienzo y retorno sin salto`, () => {
  const inicial = posePara(ficha.clave, 0)
  assert.deepEqual(posePara(ficha.clave, 1), inicial)
  assert.deepEqual(posePara(ficha.clave, -5), inicial)
  for (let i = 0; i <= 100; i++) {
    const pose = posePara(ficha.clave, i / 100)
    for (const punto of Object.values(pose).filter(Array.isArray)) {
      assert.ok(punto.every(Number.isFinite))
      assert.ok(punto[0] > 40 && punto[0] < 380 && punto[1] > 30 && punto[1] < 280)
    }
    for (const [hombro, codo, mano] of [[pose.hombroDer, pose.codoDer, pose.mano], [pose.hombroIzq, pose.codoIzq, pose.manoIzq]]) {
      if (ficha.esIsometrico) continue
      assert.ok(Math.abs(Math.hypot(codo[0] - hombro[0], codo[1] - hombro[1]) - (pose.longitudBrazo ?? 38)) < .02)
      assert.ok(Math.abs(Math.hypot(mano[0] - codo[0], mano[1] - codo[1]) - (pose.longitudBrazo ?? 38)) < .02)
    }
  }
})
test('la plancha representa sostén, sin ciclos de flexión del tronco', () => {
  assert.equal(FICHAS.find(f => f.clave === 'plancha').esIsometrico, true)
  assert.deepEqual(posePara('plancha', 0), posePara('plancha', .5))
})
test('los apoyos de las lagartijas y la sentadilla permanecen fijos', () => {
  for (const clave of ['lagartijas', 'sentadilla', 'zancadas']) {
    const inicio = posePara(clave, 0)
    for (let i = 0; i <= 100; i++) {
      const pose = posePara(clave, i / 100)
      assert.deepEqual(pose.pie, inicio.pie)
      if (clave === 'lagartijas') assert.deepEqual(pose.mano, [128, 263])
      if (clave === 'zancadas') assert.ok(pose.rodillaTrasera[1] < 253)
    }
  }
})
test('las elevaciones laterales mantienen los codos fuera del tronco', () => {
  for (let i = 0; i <= 100; i++) {
    const pose = posePara('laterales', i / 100)
    assert.ok(pose.codoDer[0] >= pose.hombroDer[0])
    assert.ok(pose.codoIzq[0] <= pose.hombroIzq[0])
  }
})
