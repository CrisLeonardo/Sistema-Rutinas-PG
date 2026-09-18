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

/**
 * «Avance» es la única sección con cuatro pestañas. Las otras dos tienen tres,
 * pero aquí la cuarta no es una pantalla más: la senda estaba colgada de un
 * enlace en el panel y no se llegaba a ella desde su propia sección, que es
 * donde se busca el avance. Las píldoras desplazan en horizontal cuando no
 * caben, de modo que la cuarta no rompe la fila en un teléfono estrecho.
 *
 * «Editar medidas» no aparece: cuelga de «Medidas» y conserva su flecha de
 * volver, igual que las pantallas hijas de las otras secciones.
 */
export const PESTANAS_AVANCE = [
  { ruta: '/avance', etiqueta: 'Peso' },
  { ruta: '/avance/senda', etiqueta: 'Senda' },
  { ruta: '/avance/evolucion', etiqueta: 'Evolución' },
  { ruta: '/avance/medidas', etiqueta: 'Medidas' },
]
