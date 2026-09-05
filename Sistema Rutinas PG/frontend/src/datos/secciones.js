/**
 * Pestañas de las secciones que agrupan más de una pantalla.
 *
 * Viven aquí y no en cada pantalla porque las tres pantallas de una sección
 * dibujan las mismas píldoras: si la lista estuviera repetida, bastaría
 * cambiarla en dos sitios y olvidarse del tercero para que la navegación
 * dejara de coincidir consigo misma.
 */

export const PESTANAS_COMER = [
  { ruta: '/comer', etiqueta: 'Menú' },
  { ruta: '/comer/plan', etiqueta: 'Mi plan' },
  { ruta: '/comer/compras', etiqueta: 'Compras' },
]

export const PESTANAS_ENTRENAR = [
  { ruta: '/entrenar', etiqueta: 'Rutina' },
  { ruta: '/entrenar/bitacora', etiqueta: 'Bitácora' },
  { ruta: '/entrenar/marcas', etiqueta: 'Marcas' },
]
