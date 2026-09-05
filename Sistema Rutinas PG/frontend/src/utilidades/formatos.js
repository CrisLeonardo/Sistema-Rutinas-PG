/**
 * Formato de cifras y fechas.
 *
 * Estaba repetido en cada pantalla, con pequeñas diferencias que hacían que la
 * misma cifra se leyera de dos maneras según dónde apareciera. Todo se escribe
 * en la convención de Guatemala, que es donde se usa el sistema.
 */

/** Entero con separador de millares: 2 180, no 2180. */
export function entero(valor) {
  if (valor === null || valor === undefined) return '—'
  return Math.round(valor).toLocaleString('es-GT')
}

/** Quetzales con dos decimales, como los precios del mercado. */
export function quetzales(valor) {
  if (valor === null || valor === undefined) return '—'
  return `Q${Number(valor).toFixed(2)}`
}

/**
 * Quetzales redondeados al entero.
 *
 * Los costos mensuales son una estimación de tres cifras: escribir los
 * centavos de una proyección a treinta días finge una precisión que el dato no
 * tiene.
 */
export function quetzalesEnteros(valor) {
  if (valor === null || valor === undefined) return '—'
  return `Q${entero(valor)}`
}

/** Fecha larga: 4 de septiembre de 2026. */
export function fechaLarga(valor) {
  if (!valor) return '—'
  return new Date(valor).toLocaleDateString('es-GT', { dateStyle: 'long' })
}

/** Fecha y hora largas, para los registros con marca de tiempo. */
export function fechaYHora(valor) {
  if (!valor) return '—'
  return new Date(valor).toLocaleString('es-GT', { dateStyle: 'long', timeStyle: 'short' })
}

/**
 * Fecha con día de la semana: «viernes 4 de septiembre».
 *
 * Se arma parte por parte porque `toLocaleDateString` intercala una coma
 * («viernes, 4 de septiembre») que no hace falta cuando la fecha va sola
 * debajo del saludo.
 */
export function fechaConDia(valor = new Date()) {
  const fecha = new Date(valor)
  const dia = fecha.toLocaleDateString('es-GT', { weekday: 'long' })
  const numero = fecha.getDate()
  const mes = fecha.toLocaleDateString('es-GT', { month: 'long' })
  return `${dia} ${numero} de ${mes}`
}

/** Fecha breve para las filas de una lista: 4 sep. */
export function fechaBreve(valor) {
  if (!valor) return '—'
  return new Date(valor).toLocaleDateString('es-GT', { day: 'numeric', month: 'short' })
}

/** Días transcurridos desde una fecha, redondeados hacia abajo. */
export function diasDesde(valor) {
  if (!valor) return null
  const transcurrido = Date.now() - new Date(valor).getTime()
  return Math.max(0, Math.floor(transcurrido / 86_400_000))
}

/** Iniciales de un nombre, para el avatar. */
export function iniciales(nombre) {
  if (!nombre) return '—'
  const partes = nombre.trim().split(/\s+/)
  const primera = partes[0]?.[0] ?? ''
  const segunda = partes.length > 1 ? partes[partes.length - 1][0] : ''
  return `${primera}${segunda}`.toUpperCase()
}

/** Cambio con signo explícito: −0.4, +1.2, 0. El menos es el signo, no un guion. */
export function conSigno(valor, decimales = 1) {
  if (valor === null || valor === undefined) return '—'
  const numero = Number(valor)
  if (numero === 0) return (0).toFixed(decimales)
  const signo = numero > 0 ? '+' : '−'
  return `${signo}${Math.abs(numero).toFixed(decimales)}`
}
