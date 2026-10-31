import { useCallback, useEffect, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioCatalogos } from '../servicios/api.js'
import AvisoDeError from '../componentes/AvisoDeError.jsx'
import FichaEjercicio from '../entrenamiento/FichaEjercicio.jsx'
import { FiguraEjercicio } from '../entrenamiento/DemostracionEjercicio.jsx'
import { fichaPara, filtrarEjercicios, GRUPOS } from '../entrenamiento/fichas.mjs'

export default function BibliotecaEjercicios() {
  const { token } = useSesion()
  const { ejercicioId } = useParams()
  const [consulta, setConsulta] = useSearchParams()
  const [ejercicios, setEjercicios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [intento, setIntento] = useState(0)
  const reintentar = useCallback(() => setIntento(n => n + 1), [])
  useEffect(() => {
    let activo = true
    setCargando(true)
    servicioCatalogos.listarEjercicios(token).then(datos => {
      if (activo) { setEjercicios(datos); setError(null) }
    }).catch(fallo => { if (activo) setError(fallo.message) }).finally(() => { if (activo) setCargando(false) })
    return () => { activo = false }
  }, [token, intento])
  useEffect(() => { window.scrollTo(0, 0) }, [ejercicioId])
  const cambiar = (clave, valor) => setConsulta(anterior => {
    const siguiente = new URLSearchParams(anterior)
    if (valor) siguiente.set(clave, valor)
    else siguiente.delete(clave)
    return siguiente
  }, { replace: true })

  if (cargando) return <p role="status">Cargando la biblioteca de ejercicios…</p>
  if (error) return <AvisoDeError mensaje={error} alReintentar={reintentar} />
  if (ejercicioId) {
    const ejercicio = ejercicios.find(e => String(e.id) === ejercicioId)
    return <div className="pila-5"><Link to="/entrenar/biblioteca" className="boton-texto">← Biblioteca de ejercicios</Link>
      {ejercicio ? <><h1 className="titulo-pantalla">{ejercicio.nombre}</h1>{!ejercicio.disponible_localmente && <p className="aviso">Este ejercicio está deshabilitado en el catálogo local.</p>}<FichaEjercicio key={ejercicio.id} ejercicio={ejercicio} /></>
        : <><h1 className="titulo-pantalla">Ejercicio no encontrado</h1><p>El enlace no corresponde a un ejercicio del catálogo actual.</p></>}
    </div>
  }
  const filtros = { busqueda: consulta.get('q') ?? '', grupo: consulta.get('grupo') ?? '', equipo: consulta.get('equipo') ?? '', soloGuias: consulta.get('guias') === '1' }
  const visibles = filtrarEjercicios(ejercicios, filtros)
  const disponibles = ejercicios.filter(e => e.disponible_localmente)
  const equipos = [...new Set(disponibles.map(e => e.equipamiento))].sort((a, b) => a.localeCompare(b, 'es'))
  return <div className="pila-5">
    <header className="pila-2"><p className="rotulo">ENTRENAR / APRENDER</p><h1 className="titulo-pantalla">Conoce el movimiento.</h1><p className="cuerpo">Prepara el equipo, entiende cada fase y vuelve a tu sesión con más claridad.</p></header>

    <section className="guia-filtros" aria-label="Filtrar ejercicios">
      <label className="campo"><span className="campo__etiqueta">Buscar ejercicio o equipo</span><input type="search" className="campo__control" placeholder="Por ejemplo: remo o mancuernas" value={filtros.busqueda} onChange={e => cambiar('q', e.target.value)} /></label>
      <div className="guia-dos-columnas"><label className="campo"><span className="campo__etiqueta">Grupo muscular</span><select className="campo__control" value={filtros.grupo} onChange={e => cambiar('grupo', e.target.value)}><option value="">Todos los grupos</option>{Object.entries(GRUPOS).map(([valor, nombre]) => <option key={valor} value={valor}>{nombre}</option>)}</select></label>
        <label className="campo"><span className="campo__etiqueta">Equipo del catálogo</span><select className="campo__control" value={filtros.equipo} onChange={e => cambiar('equipo', e.target.value)}><option value="">Cualquier equipo</option>{equipos.map(e => <option key={e}>{e}</option>)}</select></label></div>
      <label className="guia-check"><input type="checkbox" checked={filtros.soloGuias} onChange={e => cambiar('guias', e.target.checked ? '1' : '')} />Solo ejercicios con guía visual</label>
    </section>
    <p className="apoyo" role="status">{visibles.length} {visibles.length === 1 ? 'ejercicio disponible' : 'ejercicios disponibles'} · {disponibles.filter(fichaPara).length} con guía visual</p>
    {visibles.length ? <div className="guia-listado">{visibles.map(e => {
      const ficha = fichaPara(e)
      return <Link to={`/entrenar/biblioteca/${e.id}`} key={e.id} className="guia-tarjeta"><span className={ficha ? 'guia-miniatura' : 'guia-numero'} aria-hidden="true">{ficha ? <FiguraEjercicio ficha={ficha} progreso={.35} miniatura /> : GRUPOS[e.grupo_muscular]?.slice(0, 2).toUpperCase()}</span><span className="pila-2 crece"><span className="guia-nombre">{e.nombre}</span><span className="apoyo">{GRUPOS[e.grupo_muscular]} · {e.equipamiento}</span><span className="guia-tipo">{ficha ? ficha.esIsometrico ? 'Ver posición y pasos' : 'Ver movimiento y pasos' : 'Leer cómo hacerlo'}</span></span><span className="guia-tarjeta__abrir" aria-hidden="true">{ficha && !ficha.esIsometrico ? '▶' : '↗'}</span></Link>
    })}</div>
      : <div className="tarjeta"><h2 className="titulo-tarjeta">No hay coincidencias</h2><p>Prueba con otro nombre o quita algún filtro.</p><button type="button" className="boton boton--secundario" onClick={() => setConsulta({})}>Limpiar filtros</button></div>}
    <p className="nota-al-pie">Esta biblioteca permite consultar el catálogo; no determina qué ejercicios son adecuados para tu perfil. Sigue tu rutina y sus restricciones. El equipo disponible aún debe confirmarse en el gimnasio.</p>
  </div>
}
