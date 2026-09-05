/**
 * Icono del conjunto Hugeicons «Stroke Rounded».
 *
 * Es el único conjunto permitido para todo lo que no sean los cinco iconos de
 * la barra inferior (véase Iconos.jsx). Hereda el color del texto que lo rodea,
 * de modo que un icono dentro de un botón de acento se pinta con la tinta del
 * acento sin decirlo dos veces.
 *
 * Por omisión es decorativo: lo que nombra la acción es el texto que lo
 * acompaña. Cuando el icono va solo —el botón de imprimir, la flecha de
 * volver— se le pasa `etiqueta` y entonces sí se anuncia.
 */
export default function Icono({ nombre, tamano = 18, etiqueta, className = '' }) {
  const accesibilidad = etiqueta
    ? { role: 'img', 'aria-label': etiqueta }
    : { 'aria-hidden': 'true' }

  return (
    <i
      className={`hgi-stroke hgi-${nombre} ${className}`.trim()}
      style={{ fontSize: `${tamano}px` }}
      {...accesibilidad}
    />
  )
}
