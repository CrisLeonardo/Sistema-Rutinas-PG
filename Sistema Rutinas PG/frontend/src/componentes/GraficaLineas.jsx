/**
 * Gráfica de líneas dibujada con SVG (historia HU-10).
 *
 * Se dibuja a mano en lugar de incorporar una biblioteca de terceros por dos
 * razones: el requerimiento no funcional 4.5.5 exige que el sistema funcione sin
 * complementos adicionales, y el control directo del trazo permite garantizar
 * que la gráfica sea legible en una pantalla de 320 píxeles, como pide el
 * criterio de la historia HU-10.
 *
 * El rediseño le quita todo lo que no es la línea: los rótulos del eje vertical
 * desaparecen —la cifra que importa ya está arriba, en grande— y quedan tres
 * filetes horizontales para dar referencia. Las fechas van debajo, en texto
 * normal, y no dentro del SVG: así se leen al mismo tamaño que el resto de la
 * pantalla y no encogen con ella.
 */

import { fechaBreve } from '../utilidades/formatos.js'

const ANCHO = 320
const ALTO = 120
const MARGEN = { arriba: 12, abajo: 12, lados: 8 }

export default function GraficaLineas({ puntos, etiquetaValor = '', descripcion }) {
  if (!puntos || puntos.length === 0) {
    return <p className="apoyo">Todavía no hay datos que graficar.</p>
  }

  const valores = puntos.map((punto) => punto.valor)
  const maximoDato = Math.max(...valores)
  const minimoDato = Math.min(...valores)

  // Se abre un margen arriba y abajo para que la línea no quede pegada al
  // borde; si todos los valores son iguales se abre un rango artificial, porque
  // una escala de altura cero no se puede dibujar.
  const rango = maximoDato - minimoDato
  const holgura = rango === 0 ? Math.max(maximoDato * 0.05, 1) : rango * 0.14
  const maximo = maximoDato + holgura
  const minimo = minimoDato - holgura

  const anchoUtil = ANCHO - MARGEN.lados * 2
  const altoUtil = ALTO - MARGEN.arriba - MARGEN.abajo

  const coordenadaX = (indice) =>
    puntos.length === 1
      ? MARGEN.lados + anchoUtil / 2
      : MARGEN.lados + (indice / (puntos.length - 1)) * anchoUtil

  const coordenadaY = (valor) =>
    MARGEN.arriba + altoUtil - ((valor - minimo) / (maximo - minimo)) * altoUtil

  const trazo = puntos
    .map((punto, indice) => `${coordenadaX(indice)},${coordenadaY(punto.valor)}`)
    .join(' ')

  const ultimo = puntos[puntos.length - 1]

  // Tres fechas bastan para situar la línea: la primera, la del medio y la
  // última. Con una por punto el texto se encima en un teléfono.
  const rotulos =
    puntos.length <= 3
      ? puntos
      : [puntos[0], puntos[Math.floor((puntos.length - 1) / 2)], ultimo]

  return (
    <figure className="pila-3 figura">
      <svg
        viewBox={`0 0 ${ANCHO} ${ALTO}`}
        preserveAspectRatio="xMidYMid meet"
        className="grafica"
        role="img"
        aria-label={descripcion}
      >
        {[0, 0.5, 1].map((proporcion) => {
          const y = MARGEN.arriba + altoUtil * proporcion
          return (
            <line
              key={proporcion}
              x1={0}
              y1={y}
              x2={ANCHO}
              y2={y}
              className="grafica__cuadricula"
              vectorEffect="non-scaling-stroke"
            />
          )
        })}

        <polyline points={trazo} className="grafica__linea" vectorEffect="non-scaling-stroke" />

        <circle
          cx={coordenadaX(puntos.length - 1)}
          cy={coordenadaY(ultimo.valor)}
          r="5"
          className="grafica__punto"
        >
          <title>
            {fechaBreve(ultimo.etiqueta)}: {ultimo.valor} {etiquetaValor}
          </title>
        </circle>
      </svg>

      <div className="grafica__ejes">
        {rotulos.map((punto, indice) => (
          <span key={`${punto.etiqueta}-${indice}`}>{fechaBreve(punto.etiqueta)}</span>
        ))}
      </div>

      {descripcion && <figcaption className="solo-lectores">{descripcion}</figcaption>}
    </figure>
  )
}
