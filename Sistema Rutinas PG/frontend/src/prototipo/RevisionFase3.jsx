import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import CabeceraCuenta from '../componentes/MarcaProducto.jsx'
import MetadatosPrivados from '../componentes/MetadatosPrivados.jsx'
import FichaEjercicio from '../entrenamiento/FichaEjercicio.jsx'
import { FICHAS, GRUPOS } from '../entrenamiento/fichas.mjs'
import { FiguraEjercicio } from '../entrenamiento/DemostracionEjercicio.jsx'

const CLAVE = 'senda.revision-fase3.v1'
function leer() { try { return JSON.parse(localStorage.getItem(CLAVE)) || {} } catch { return {} } }
export default function RevisionFase3() {
  const [consulta, setConsulta] = useSearchParams()
  const ficha = FICHAS.find(f => f.clave === consulta.get('ejercicio')) ?? FICHAS[0]
  const [notas, setNotas] = useState(leer)
  const [fallo, setFallo] = useState(false)
  const anotacion = notas[ficha.clave]?.version === ficha.version ? notas[ficha.clave] : {}
  useEffect(() => { document.title = 'Senda · Revisión del piloto de ejercicios' }, [])
  const actualizar = cambio => {
    const siguiente = { ...notas, [ficha.clave]: { ...anotacion, ...cambio, version: ficha.version, actualizadoEl: new Date().toISOString() } }
    try { localStorage.setItem(CLAVE, JSON.stringify(siguiente)); setFallo(false) } catch { setFallo(true) }
    setNotas(siguiente)
  }
  const exportar = () => {
    const salida = { proyecto: 'Senda', fase: 3, exportadoEl: new Date().toISOString(), estado: 'observaciones; no publica ni valida fichas',
      fichas: FICHAS.map(f => ({ clave: f.clave, nombre: f.nombre, version: f.version, fuente: f.fuente, observaciones: notas[f.clave] ?? {} })) }
    const url = URL.createObjectURL(new Blob([JSON.stringify(salida, null, 2)], { type: 'application/json' }))
    const enlace = document.createElement('a'); enlace.href = url; enlace.download = 'senda-revision-fase-3.json'; enlace.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  return <div className="revision-entrenamiento">
    <MetadatosPrivados /><CabeceraCuenta />
    <header className="revision-cabecera"><p className="rotulo">SENDA / FASE 3 / PILOTO</p><h1>Un movimiento.<br /><em>Cada detalle cuenta.</em></h1><p>{FICHAS.length} fichas para revisar: postura, equipo, recorrido y explicación. Las ilustraciones son esquemas 2D originales y siguen pendientes de validación.</p><Link to="/entrenar/biblioteca" className="boton-texto">Abrir la biblioteca del sistema ↗</Link></header>
    <div className="revision-distribucion"><aside className="revision-indice"><h2 className="rotulo">GUÍAS PARA REVISAR</h2><nav aria-label="Ejercicios del piloto">{FICHAS.map((f, i) => <Link key={f.clave} to={`?ejercicio=${f.clave}`} aria-current={consulta.get('vista') !== 'lamina' && f.clave === ficha.clave ? 'page' : undefined}><span className="mono">{String(i + 1).padStart(2, '0')}</span><span>{f.nombre}<small>{GRUPOS[f.grupo_muscular]}</small></span></Link>)}</nav><Link to="?vista=lamina" className="boton-texto">Comparar posiciones ↗</Link><button type="button" className="boton boton--secundario" onClick={exportar}>Descargar observaciones</button></aside>
      {consulta.get('vista') === 'lamina' ? <main className="revision-contenido revision-lamina">
        <h2 className="titulo-pantalla">Las posiciones de las guías</h2>
        <p className="apoyo">Inicio, punto de acción y regreso. La plancha se muestra como posición sostenida. Son esquemas para revisión.</p>
        {FICHAS.map(f => <section className="tarjeta" key={f.clave}>
          <h3 className="titulo-tarjeta">{f.nombre}</h3>
          <div className={`guia-fotogramas${f.esIsometrico ? ' guia-fotogramas--sosten' : ''}`}>
            {(f.esIsometrico ? [0] : [0, .5, 1]).map((p, i) => <figure key={i}><FiguraEjercicio ficha={f} progreso={p} miniatura /><figcaption>{f.esIsometrico ? 'Posición de sostén' : f.fases[i][0]}</figcaption></figure>)}
          </div>
          <Link to={`?ejercicio=${f.clave}`}>Revisar esta ficha ↗</Link>
        </section>)}
      </main> : <main className="revision-contenido"><h2 className="titulo-pantalla">{ficha.nombre}</h2><FichaEjercicio key={ficha.clave} ejercicio={ficha} revision />
        <section className="revision-notas pila-4" aria-label="Tus observaciones"><h2 className="titulo-tarjeta">Tu revisión de esta ficha</h2><p className="apoyo">Las notas se guardan en este navegador. Descargar observaciones permite conservarlas y compartir las correcciones. Esto no publica ni marca la ficha como validada.</p>
          {['Postura y apoyos', 'Equipo representado', 'Recorrido y fases', 'Texto y errores frecuentes'].map(t => <label className="guia-check" key={`${ficha.clave}-${t}`}><input type="checkbox" checked={Boolean(anotacion[t])} onChange={e => actualizar({ [t]: e.target.checked })} />He comprobado: {t.toLowerCase()}</label>)}
          <label className="campo"><span className="campo__etiqueta">Qué ajustar</span><textarea className="campo__control" rows="4" maxLength="3000" value={anotacion.comentario ?? ''} onChange={e => actualizar({ comentario: e.target.value })} placeholder="Indica la fase y el detalle que cambiarías." /></label>
          {fallo && <p role="alert">No fue posible guardar en este navegador. Descarga las observaciones antes de salir.</p>}
        </section>
      </main>}</div>
  </div>
}
