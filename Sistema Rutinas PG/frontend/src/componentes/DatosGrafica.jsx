import { fechaBreve } from '../utilidades/formatos.js'

export default function DatosGrafica({ puntos, etiquetaValor, descripcion }) {
  return <details className="datos-grafica">
    <summary>Ver valores en texto{descripcion ? `: ${descripcion}` : ''}</summary>
    <table><caption className="solo-lectores">{descripcion || 'Valores de la gráfica'}</caption><thead><tr><th scope="col">Fecha</th><th scope="col">Valor {etiquetaValor}</th></tr></thead>
      <tbody>{puntos.map((p, i) => <tr key={`${p.etiqueta}-${i}`}><th scope="row">{fechaBreve(p.etiqueta)}</th><td>{p.valor} {etiquetaValor}</td></tr>)}</tbody>
    </table>
  </details>
}
