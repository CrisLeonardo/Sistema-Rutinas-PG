import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioJuego } from '../servicios/api.js'
import TarjetaLogro from './TarjetaLogro.jsx'

/** Las recompensas proceden de la respuesta del servidor, nunca de animar una cifra. */
export default function RecompensaAccion({ recompensa }) {
  const { token } = useSesion()
  const [logros, setLogros] = useState([])
  const [fallo, setFallo] = useState(false)
  const firma = (recompensa?.logros_nuevos ?? []).join('|')
  useEffect(() => {
    let vigente = true
    setLogros([]); setFallo(false)
    if (firma) servicioJuego.consultarEstado(token).then(estado => {
      if (vigente) {
        const encontrados = estado.logros.filter(l => l.obtenido && firma.split('|').includes(l.clave))
        setLogros(encontrados)
        setFallo(encontrados.length === 0)
      }
    }).catch(() => { if (vigente) setFallo(true) })
    return () => { vigente = false }
  }, [firma, token])
  if (!recompensa) return null

  return <section className="pila-3" aria-label="Recompensa de esta acción">
    <div className="ganancia resultado-accion">
      <span className="ganancia__cifra">+{recompensa.puntos_ganados}</span><span className="cifras__rotulo">puntos de esta acción</span>
      {recompensa.subio_de_nivel && <span className="ganancia__subida">Nivel {recompensa.nivel_actual} · {recompensa.nombre_nivel}</span>}
    </div>
    {recompensa.puntos_ganados === 0 && <p className="apoyo">El registro se guardó. Esta acción no añadió puntos; conserve la frecuencia indicada en su plan.</p>}
    {recompensa.detalle?.length > 0 && <details className="tarjeta tarjeta--densa"><summary>De dónde salieron los puntos</summary><ul className="recompensa-detalle">{recompensa.detalle.map((p, i) => <li key={`${p.tipo}-${i}`}><span>{p.motivo}</span><strong>+{p.puntos}</strong></li>)}</ul></details>}
    {firma && <div className="pila-3"><h2 className="titulo-tarjeta">{recompensa.logros_nuevos.length === 1 ? 'Nueva insignia' : 'Nuevas insignias'}</h2>
      {!logros.length && <p className="apoyo">{fallo ? 'El registro y los puntos están guardados. Consulte el detalle de sus nuevas insignias en Mi senda.' : 'Consultando el detalle de sus nuevas insignias…'}</p>}
      {logros.map(logro => <article key={logro.clave} className="tarjeta insignia-revelada"><h3 className="titulo-tarjeta">{logro.nombre}</h3><p className="apoyo">{logro.descripcion}</p><TarjetaLogro logro={logro} /></article>)}
      <Link className="boton-texto" to="/avance/senda">Ver mis insignias en Mi senda</Link>
    </div>}
  </section>
}
