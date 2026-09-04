/**
 * Iconos de la barra de navegación inferior.
 *
 * Se dibujan a mano en SVG, como las gráficas de los reportes y por la misma
 * razón: el requerimiento no funcional 4.5.5 pide que el sistema funcione sin
 * complementos adicionales, y una fuente de iconos de terceros son 70 KB más
 * que descargar sobre una conexión móvil para mostrar cinco figuras.
 *
 * Son decorativos: la etiqueta de texto que va debajo es la que nombra el
 * destino, de modo que se marcan como ocultos para el lector de pantalla y no
 * se lea dos veces lo mismo.
 */

const COMUN = {
  width: 22,
  height: 22,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  'aria-hidden': 'true',
  focusable: 'false',
}

/** Casa: el panel principal. */
export function IconoInicio() {
  return (
    <svg {...COMUN}>
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5.5 9.5V20h13V9.5" />
      <path d="M9.5 20v-5.5h5V20" />
    </svg>
  )
}

/** Plato con cubiertos: el menú del día. */
export function IconoComer() {
  return (
    <svg {...COMUN}>
      <circle cx="12" cy="12" r="8.5" />
      <circle cx="12" cy="12" r="4" />
    </svg>
  )
}

/** Mancuerna: la rutina de entrenamiento. */
export function IconoEntrenar() {
  return (
    <svg {...COMUN}>
      <path d="M4 9v6" />
      <path d="M7 7v10" />
      <path d="M17 7v10" />
      <path d="M20 9v6" />
      <path d="M7 12h10" />
    </svg>
  )
}

/** Flecha ascendente: el registro del avance. */
export function IconoAvance() {
  return (
    <svg {...COMUN}>
      <path d="M4 18 10 11l4 4 6-7" />
      <path d="M20 12V8h-4" />
    </svg>
  )
}

/** Gráfica de barras: los reportes de evolución. */
export function IconoEvolucion() {
  return (
    <svg {...COMUN}>
      <path d="M4 20h16" />
      <path d="M7 20v-6" />
      <path d="M12 20V6" />
      <path d="M17 20v-9" />
    </svg>
  )
}
