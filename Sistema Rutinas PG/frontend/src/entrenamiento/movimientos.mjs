// Esquemas 2D propios: coordenadas en un lienzo de 420 × 300.
// Las longitudes son gráficas, no medidas antropométricas ni una evaluación.
import { CLAVES_ADICIONALES, poseAdicional } from './posesAdicionales.mjs'
export const acotar = (n, min = 0, max = 1) => Math.min(max, Math.max(min, Number.isFinite(n) ? n : min))
const mezclar = (a, b, t) => a.map((n, i) => n + (b[i] - n) * t)

export function articulacion(a, b, largoA = 38, largoB = 38, lado = 1) {
  const dx = b[0] - a[0], dy = b[1] - a[1]
  const distancia = Math.max(0.001, Math.hypot(dx, dy))
  const d = Math.min(distancia, largoA + largoB - 0.001)
  const avance = (largoA ** 2 - largoB ** 2 + d ** 2) / (2 * d)
  const alto = Math.sqrt(Math.max(0, largoA ** 2 - avance ** 2)) * lado
  return [a[0] + (dx * avance - dy * alto) / distancia, a[1] + (dy * avance + dx * alto) / distancia]
}

const dePie = { hombro: [201, 79], cadera: [201, 157], pie: [201, 263], pieTrasero: [197, 263], mano: [208, 153] }
const posiciones = {
  'press-banca': [
    { hombro: [145, 177], cadera: [222, 177], pie: [282, 263], pieTrasero: [269, 263], mano: [165, 107] },
    { hombro: [145, 177], cadera: [222, 177], pie: [282, 263], pieTrasero: [269, 263], mano: [179, 151] },
  ],
  'lagartijas': [
    { hombro: [135, 189], cadera: [216, 224], pie: [302, 261], pieTrasero: [298, 259], mano: [128, 263] },
    { hombro: [136, 230], cadera: [219, 246], pie: [302, 261], pieTrasero: [298, 259], mano: [128, 263] },
  ],
  'remo-barra': [
    { hombro: [233, 110], cadera: [176, 162], pie: [191, 263], pieTrasero: [181, 263], mano: [240, 183] },
    { hombro: [233, 110], cadera: [176, 162], pie: [191, 263], pieTrasero: [181, 263], mano: [203, 158] },
  ],
  'sentadilla': [ dePie,
    { hombro: [205, 143], cadera: [163, 208], pie: [201, 263], pieTrasero: [197, 263], mano: [190, 148] },
  ],
  'zancadas': [
    { hombro: [205, 101], cadera: [205, 179], pie: [268, 263], pieTrasero: [135, 254], mano: [211, 175] },
    { hombro: [205, 123], cadera: [205, 201], pie: [268, 263], pieTrasero: [135, 254], mano: [211, 197] },
  ],
  'talones': [dePie, { hombro: [201, 66], cadera: [201, 144], pie: [201, 250], pieTrasero: [197, 250], mano: [208, 140] }],
  'curl-barra': [dePie, { ...dePie, mano: [232, 92] }],
  'plancha': [
    { hombro: [137, 218], cadera: [218, 237], pie: [306, 259], pieTrasero: [298, 257], mano: [106, 263] },
    { hombro: [137, 218], cadera: [218, 237], pie: [306, 259], pieTrasero: [298, 257], mano: [106, 263] },
  ],
  'laterales': [
    { hombro: [200, 79], cadera: [200, 157], pie: [224, 263], pieTrasero: [176, 263], mano: [225, 152] },
    { hombro: [200, 79], cadera: [200, 157], pie: [224, 263], pieTrasero: [176, 263], mano: [294, 79] },
  ],
  'jalon-pecho': [
    { hombro: [200, 133], cadera: [200, 209], pie: [234, 263], pieTrasero: [166, 263], mano: [252, 65] },
    { hombro: [200, 133], cadera: [200, 209], pie: [234, 263], pieTrasero: [166, 263], mano: [252, 153] },
  ],
}

export const CLAVES_MOVIMIENTO = [...Object.keys(posiciones), ...CLAVES_ADICIONALES]
export function faseActual(progreso, ficha) {
  const p = acotar(progreso)
  if (ficha?.clave === 'curl-alterno') return p < .12 ? 0 : p > .88 ? 2 : 1
  return Math.min(2, Math.floor(p * 3))
}
export const fotogramasPara = ficha => [0, ficha?.clave === 'curl-alterno' ? .25 : .5, 1]
export function avanzar(progreso, milisegundos, velocidad = 1) { return acotar(progreso + Math.max(0, milisegundos) / 6000 * velocidad) }

export function posePara(clave, progreso = 0) {
  const adicional = poseAdicional(clave, acotar(progreso), articulacion)
  if (adicional) return adicional
  const estados = posiciones[clave]
  if (!estados) return null
  const p = acotar(progreso)
  // Inicio → punto de acción → regreso. Un solo ciclo termina y se pausa.
  const recorrido = p <= 0.5 ? p * 2 : (1 - p) * 2
  const t = (1 - Math.cos(Math.PI * recorrido)) / 2
  const pose = Object.fromEntries(Object.keys(estados[0]).map(k => [k, mezclar(estados[0][k], estados[1][k], t)]))
  if (clave === 'sentadilla') pose.mano = [pose.hombro[0] - 15, pose.hombro[1] + 5]
  let codoLateral
  if (clave === 'laterales') {
    // Dos segmentos de longitud fija, con el codo hacia fuera del tronco.
    const angulo = (80 - 90 * t) * Math.PI / 180
    codoLateral = [pose.hombro[0] + 20 + 38 * Math.cos(angulo), pose.hombro[1] + 38 * Math.sin(angulo)]
    pose.mano = [codoLateral[0] + 38 * Math.cos(angulo + Math.PI / 9), codoLateral[1] + 38 * Math.sin(angulo + Math.PI / 9)]
  }
  const frontal = clave === 'laterales' || clave === 'jalon-pecho'
  const { hombro, cadera, mano, pie, pieTrasero } = pose
  const dx = hombro[0] - cadera[0], dy = hombro[1] - cadera[1], largo = Math.hypot(dx, dy)
  const cabeza = [hombro[0] + dx / largo * 29, hombro[1] + dy / largo * 29]
  if (clave === 'press-banca') cabeza[1] -= 10
  const hombroIzq = frontal ? [hombro[0] - 20, hombro[1]] : [hombro[0] - 5, hombro[1] + 2]
  const hombroDer = frontal ? [hombro[0] + 20, hombro[1]] : hombro
  const manoIzq = frontal ? [400 - mano[0], mano[1]] : [mano[0] - 6, mano[1] + 1]
  const signoBrazo = ['lagartijas', 'sentadilla'].includes(clave) ? -1 : 1
  const codoDer = codoLateral ?? (clave === 'plancha' ? [137, 263] : articulacion(hombroDer, mano, 38, 38, signoBrazo))
  const codoIzq = codoLateral ? [400 - codoLateral[0], codoLateral[1]] : clave === 'plancha' ? [132, 260] : articulacion(hombroIzq, manoIzq, 38, 38, frontal ? -1 : signoBrazo)
  const recta = clave === 'lagartijas' || clave === 'plancha'
  const caderaDer = frontal ? [cadera[0] + 10, cadera[1]] : cadera
  const caderaIzq = frontal ? [cadera[0] - 10, cadera[1]] : cadera
  const rodilla = clave === 'jalon-pecho' ? [pie[0], 218] : frontal ? mezclar(caderaDer, pie, .5) : recta ? mezclar(cadera, pie, 0.52) : articulacion(cadera, pie, 53, 53, -1)
  const rodillaTrasera = clave === 'jalon-pecho' ? [pieTrasero[0], 218] : frontal ? mezclar(caderaIzq, pieTrasero, .5) : recta ? mezclar(cadera, pieTrasero, 0.52) : articulacion(cadera, pieTrasero, 53, 53, clave === 'zancadas' ? -1 : 1)
  return { ...pose, cabeza, hombroIzq, hombroDer, caderaDer, caderaIzq, manoIzq, codoDer, codoIzq, rodilla, rodillaTrasera, frontal }
}
