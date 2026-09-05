/**
 * Gráfica de barras (historia HU-10).
 *
 * Se usa para las sesiones cumplidas y la adherencia, magnitudes que se
 * comparan mejor por altura que por pendiente.
 *
 * El rediseño la saca del SVG: son cajas de altura variable repartidas con
 * `flex`, de modo que se adaptan al ancho disponible sin recalcular nada y sin
 * que el texto encoja con la figura. La última barra va en acento pleno porque
 * es la semana en curso, que es la que se está mirando.
 */

import { fechaBreve } from '../utilidades/formatos.js'

export default function GraficaBarras({ puntos, etiquetaValor = '', descripcion }) {
  if (!puntos || puntos.length === 0) {
    return <p className="apoyo">Todavía no hay datos que graficar.</p>
  }

  const maximo = Math.max(...puntos.map((punto) => punto.valor), 1)

  const rotulos =
    puntos.length <= 3
      ? puntos
      : [puntos[0], puntos[Math.floor((puntos.length - 1) / 2)], puntos[puntos.length - 1]]

  return (
    <figure className="pila-3" style={{ margin: 0 }}>
      <div className="barras" role="img" aria-label={descripcion}>
        {puntos.map((punto, indice) => (
          <div
            key={`${punto.etiqueta}-${indice}`}
            className={`barras__barra${
              indice === puntos.length - 1 ? ' barras__barra--ultima' : ''
            }`}
            style={{ height: `${Math.max((punto.valor / maximo) * 100, 3)}%` }}
            title={`${fechaBreve(punto.etiqueta)}: ${punto.valor} ${etiquetaValor}`}
          />
        ))}
      </div>

      <div className="grafica__ejes">
        {rotulos.map((punto, indice) => (
          <span key={`${punto.etiqueta}-${indice}`}>{fechaBreve(punto.etiqueta)}</span>
        ))}
      </div>

      {descripcion && <figcaption className="solo-lectores">{descripcion}</figcaption>}
    </figure>
  )
}
