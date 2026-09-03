/**
 * Gráfica de barras dibujada con SVG (historia HU-10).
 *
 * Se usa para las sesiones cumplidas y la adherencia, magnitudes que se
 * comparan mejor por altura que por pendiente. Igual que la gráfica de líneas,
 * se dibuja sin bibliotecas de terceros y se escala con `viewBox` para que
 * resulte legible desde 320 píxeles de ancho.
 */

const ANCHO = 320
const ALTO = 160
const MARGEN = { arriba: 14, derecha: 8, abajo: 26, izquierda: 30 }

function fechaCorta(valor) {
  return new Date(valor).toLocaleDateString('es-GT', { day: 'numeric', month: 'short' })
}

export default function GraficaBarras({
  puntos,
  maximoFijo = null,
  etiquetaValor = '',
  color = 'var(--color-acento)',
  descripcion,
}) {
  if (!puntos || puntos.length === 0) {
    return <p className="texto-ayuda mb-0">Todavía no hay datos que graficar.</p>
  }

  const maximo = maximoFijo ?? Math.max(...puntos.map((punto) => punto.valor), 1)
  const anchoUtil = ANCHO - MARGEN.izquierda - MARGEN.derecha
  const altoUtil = ALTO - MARGEN.arriba - MARGEN.abajo

  // El ancho de barra se calcula a partir de la cantidad de puntos, con una
  // separación proporcional, para que la gráfica no se deforme al crecer el
  // historial.
  const paso = anchoUtil / puntos.length
  const anchoBarra = Math.max(paso * 0.6, 3)

  return (
    <figure className="mb-0">
      <svg
        viewBox={`0 0 ${ANCHO} ${ALTO}`}
        preserveAspectRatio="xMidYMid meet"
        className="grafica"
        role="img"
        aria-label={descripcion}
      >
        {[0, maximo / 2, maximo].map((valor) => {
          const y = MARGEN.arriba + altoUtil - (valor / maximo) * altoUtil
          return (
            <g key={valor}>
              <line
                x1={MARGEN.izquierda}
                y1={y}
                x2={ANCHO - MARGEN.derecha}
                y2={y}
                className="grafica-cuadricula"
              />
              <text
                x={MARGEN.izquierda - 6}
                y={y + 3}
                textAnchor="end"
                className="grafica-texto"
              >
                {Math.round(valor)}
              </text>
            </g>
          )
        })}

        {puntos.map((punto, indice) => {
          const altura = (punto.valor / maximo) * altoUtil
          const x = MARGEN.izquierda + paso * indice + (paso - anchoBarra) / 2
          return (
            <rect
              key={punto.etiqueta + indice}
              x={x}
              y={MARGEN.arriba + altoUtil - altura}
              width={anchoBarra}
              height={Math.max(altura, 1)}
              fill={color}
              rx="2"
            >
              <title>
                {fechaCorta(punto.etiqueta)}: {punto.valor} {etiquetaValor}
              </title>
            </rect>
          )
        })}

        <text x={MARGEN.izquierda} y={ALTO - 8} textAnchor="start" className="grafica-texto">
          {fechaCorta(puntos[0].etiqueta)}
        </text>
        {puntos.length > 1 && (
          <text
            x={ANCHO - MARGEN.derecha}
            y={ALTO - 8}
            textAnchor="end"
            className="grafica-texto"
          >
            {fechaCorta(puntos[puntos.length - 1].etiqueta)}
          </text>
        )}
      </svg>
      {descripcion && <figcaption className="texto-ayuda mt-2">{descripcion}</figcaption>}
    </figure>
  )
}
