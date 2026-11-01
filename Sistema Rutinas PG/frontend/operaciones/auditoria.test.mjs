// Regresiones de la auditoría final del 31 de octubre de 2026.
import test from 'node:test'
import assert from 'node:assert/strict'
import { describirValidacion } from '../src/servicios/validacion.mjs'
import { aFecha, fechaBreve, fechaYHora } from '../src/utilidades/formatos.js'

test('un número fuera de rango se explica en español y nombra el dato y la serie', () => {
  const mensaje = describirValidacion([{
    type: 'less_than_equal', loc: ['body', 'series', 0, 'repeticiones'],
    msg: 'Input should be less than or equal to 100', ctx: { le: 100 },
  }])
  assert.equal(mensaje, 'Repeticiones de la serie 1: debe ser como máximo 100.')
  assert.doesNotMatch(mensaje, /Input should/)
})

test('los mensajes estándar en inglés nunca llegan a la pantalla', () => {
  const casos = [
    { type: 'int_parsing', loc: ['path', 'sesion_id'], msg: 'Input should be a valid integer, unable to parse string as an integer' },
    { type: 'value_error', loc: ['body', 'correo'], msg: 'value is not a valid email address: An email address must have an @-sign.' },
    { type: 'string_too_short', loc: ['body', 'nombre'], msg: 'String should have at least 2 characters', ctx: { min_length: 2 } },
    { type: 'algo_desconocido', loc: ['body', 'peso_kg'], msg: 'Something went wrong' },
  ]
  const mensajes = casos.map(caso => describirValidacion([caso]))
  assert.deepEqual(mensajes, [
    'Sesión: debe ser un número entero.',
    'Correo electrónico: no es una dirección de correo válida.',
    'Nombre: debe tener al menos 2 caracteres.',
    'Peso: tiene un valor no válido.',
  ])
})

test('los validadores propios del servidor conservan su texto en español', () => {
  const mensaje = describirValidacion([{ type: 'value_error', loc: ['body'], msg: 'Value error, La energía declarada no concuerda. Revise los valores.' }])
  assert.equal(mensaje, 'La energía declarada no concuerda. Revise los valores.')
})

test('una fecha sola es ese día en la hora local, no el anterior', () => {
  const fecha = aFecha('2026-10-31')
  assert.deepEqual([fecha.getFullYear(), fecha.getMonth(), fecha.getDate()], [2026, 9, 31])
  assert.match(fechaBreve('2026-10-31'), /31/)
})

test('una marca UTC con zona se muestra en la hora local', () => {
  const marca = '2026-11-01T00:26:14+00:00'
  assert.equal(aFecha(marca).getTime(), Date.UTC(2026, 10, 1, 0, 26, 14))
  // El texto depende de la zona del equipo; la conversión, no.
  const esperado = new Date(Date.UTC(2026, 10, 1, 0, 26, 14)).toLocaleString('es-GT', { dateStyle: 'long', timeStyle: 'short' })
  assert.equal(fechaYHora(marca), esperado)
})
