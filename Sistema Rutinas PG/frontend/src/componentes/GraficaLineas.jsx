/**
 * Gráfica de líneas dibujada con SVG (historia HU-10).
 *
 * Se dibuja a mano en lugar de incorporar una biblioteca de terceros por dos
 * razones: el requerimiento no funcional 4.5.5 exige que el sistema funcione sin
 * complementos adicionales, y el control directo del trazo permite garantizar
 * que la gráfica sea legible en una pantalla de 320 píxeles, como pide el
 * criterio de la historia HU-10.
 *
 * El SVG se escala con `viewBox` y `preserveAspectRatio`, de modo que ocupe el
 * ancho disponible sin desbordarlo en ningún tamaño de pantalla.
 */

const ANCHO = 320
const ALTO = 180
const MARGEN = { arriba: 16, derecha: 12, abajo: 28, izquierda: 40 }

/**
 * Elige las marcas del eje vertical.
 *
 * Se descartan las que quedarían con la misma etiqueta después de redondear: en
 * un rango estrecho, dos marcas distintas pueden rotularse igual y el eje
 * parecería repetido.
 */
function marcasVerticales(minimo, maximo, decimales, cantidad = 4) {
  if (minimo === maximo) return [minimo]
  const paso = (maximo - minimo) / cantidad
  const todas = Array.from({ length: cantidad + 1 }, (_, indice) => minimo + paso * indice)

  const vistas = new Set()
  return todas.filter((valor) => {
    const etiqueta = valor.toFixed(decimales)
    if (vistas.has(etiqueta)) return false
    vistas.add(etiqueta)
    return true
  })
}

function fechaCorta(valor) {
  return new Date(valor).toLocaleDateString('es-GT', { day: 'numeric', month: 'short' })
}

export default function GraficaLineas({
  puntos,
  etiquetaValor = '',
  color = 'var(--color-principal)',
  decimales = 1,
  descripcion,
}) {
  if (!puntos || puntos.length === 0) {
    return <p className="texto-ayuda mb-0">Todavía no hay datos que graficar.</p>
  }

  const valores = puntos.map((punto) => punto.valor)
  const maximoDato = Math.max(...valores)
  const minimoDato = Math.min(...valores)

  // Se añade un margen del diez por ciento arriba y abajo para que la línea no
  // quede pegada a los bordes; si todos los valores son iguales se abre un
  // rango artificial, porque una escala de altura cero no se puede dibujar.
  const rango = maximoDato - minimoDato
  const holgura = rango === 0 ? Math.max(maximoDato * 0.05, 1) : rango * 0.1
  const maximo = maximoDato + holgura
  const minimo = minimoDato - holgura

  const anchoUtil = ANCHO - MARGEN.izquierda - MARGEN.derecha
  const altoUtil = ALTO - MARGEN.arriba - MARGEN.abajo

  const coordenadaX = (indice) =>
    puntos.length === 1
      ? MARGEN.izquierda + anchoUtil / 2
      : MARGEN.izquierda + (indice / (puntos.length - 1)) * anchoUtil

  const coordenadaY = (valor) =>
    MARGEN.arriba + altoUtil - ((valor - minimo) / (maximo - minimo)) * altoUtil

  const trazo = puntos
    .map((punto, indice) => `${indice === 0 ? 'M' : 'L'} ${coordenadaX(indice)} ${coordenadaY(punto.valor)}`)
    .join(' ')

  // Solo se rotulan el primer y el último punto del eje horizontal: con más
  // etiquetas el texto se encima en una pantalla de teléfono.
  const indicesRotulados =
    puntos.length === 1 ? [0] : [0, puntos.length - 1]

  return (
    <figure className="mb-0">
      <svg
        viewBox={`0 0 ${ANCHO} ${ALTO}`}
        preserveAspectRatio="xMidYMid meet"
        className="grafica"
        role="img"
        aria-label={descripcion}
      >
        {marcasVerticales(minimo, maximo, decimales).map((valor) => (
          <g key={valor}>
            <line
              x1={MARGEN.izquierda}
              y1={coordenadaY(valor)}
              x2={ANCHO - MARGEN.derecha}
              y2={coordenadaY(valor)}
              className="grafica-cuadricula"
            />
            <text
              x={MARGEN.izquierda - 6}
              y={coordenadaY(valor) + 3}
              textAnchor="end"
              className="grafica-texto"
            >
              {valor.toFixed(decimales)}
            </text>
          </g>
        ))}

        <path d={trazo} fill="none" stroke={color} strokeWidth="2.5" strokeLinejoin="round" />

        {puntos.map((punto, indice) => (
          <circle
            key={punto.etiqueta + indice}
            cx={coordenadaX(indice)}
            cy={coordenadaY(punto.valor)}
            r="4"
            fill={color}
          >
            <title>
              {fechaCorta(punto.etiqueta)}: {punto.valor} {etiquetaValor}
            </title>
          </circle>
        ))}

        {indicesRotulados.map((indice) => (
          <text
            key={`eje-${indice}`}
            x={coordenadaX(indice)}
            y={ALTO - 8}
            textAnchor={indice === 0 && puntos.length > 1 ? 'start' : indice === 0 ? 'middle' : 'end'}
            className="grafica-texto"
          >
            {fechaCorta(puntos[indice].etiqueta)}
          </text>
        ))}
      </svg>
      {descripcion && <figcaption className="texto-ayuda mt-2">{descripcion}</figcaption>}
    </figure>
  )
}
