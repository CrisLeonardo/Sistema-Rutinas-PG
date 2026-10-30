import { useEffect, useId, useRef, useState } from 'react'
import { avanzar, faseActual, posePara } from './movimientos.mjs'

const puntos = (...lista) => lista.map(p => p.join(',')).join(' ')

export function FiguraEjercicio({ ficha, progreso = 0, miniatura = false }) {
  const id = useId()
  const pose = posePara(ficha.clave, progreso)
  if (!pose) return <p>Ilustración no disponible. Consulta las fases escritas.</p>
  const { cabeza, hombro, cadera, caderaDer, caderaIzq, pie, pieTrasero, mano, manoIzq, hombroIzq, hombroDer, codoDer, codoIzq, rodilla, rodillaTrasera } = pose
  const barra = ['press-banca', 'remo-barra', 'curl-barra', 'sentadilla'].includes(ficha.clave)
  const carga = ficha.clave === 'sentadilla' ? [hombro[0] - 12, hombro[1] - 5] : mano
  const dosLados = pose.frontal || ficha.clave === 'zancadas'
  const articulaciones = [hombroDer, codoDer, mano, caderaDer, rodilla, pie]
  return <svg className={`guia-figura${miniatura ? ' guia-figura--mini' : ''}`} viewBox="0 0 420 300" role="img" aria-labelledby={`${id}-titulo ${id}-detalle`}>
    <title id={`${id}-titulo`}>{ficha.nombre} · {ficha.vista.toLowerCase()}</title>
    <desc id={`${id}-detalle`}>{ficha.esIsometrico ? 'Posición de sostén, sin movimiento repetido.' : `Esquema de la fase ${ficha.fases[faseActual(progreso)][0].toLowerCase()}. ${ficha.fases[faseActual(progreso)][1]}`} Los círculos señalan las articulaciones. La vista es simplificada.</desc>
    <path d="M 54 267 H 366" className="guia-suelo" />
    {ficha.clave === 'press-banca' && <g className="guia-equipo"><path d="M110 188 V264 M235 188 V264" /><path d="M92 185 H250" className="guia-banca" /><text x="101" y="229" className="guia-vista">BANCA</text></g>}
    {ficha.clave === 'jalon-pecho' && <g className="guia-equipo"><path d="M94 265 V31 H306 V265 M163 223 H237 M200 223 V265" /><circle cx="200" cy="33" r="7" /><path d={`M200 40 V${mano[1] - 8}`} className="guia-cable" /><path d={`M${manoIzq[0]} ${mano[1]} Q200 ${mano[1] - 16} ${mano[0]} ${mano[1]}`} className="guia-barra-polea" /></g>}
    {dosLados && <g className="guia-miembro guia-miembro--lejos"><polyline points={puntos(caderaIzq, rodillaTrasera, pieTrasero)} />{pose.frontal && <polyline points={puntos(hombroIzq, codoIzq, manoIzq)} />}</g>}
    <g className="guia-miembro"><polyline className={ficha.grupo_muscular === 'pierna' ? 'guia-segmento-activo' : undefined} points={puntos(caderaDer, rodilla, pie)} /><path d={`M${cadera[0]} ${cadera[1]} L${hombro[0]} ${hombro[1]}`} />
      {pose.frontal && <><path d={`M${hombroIzq[0]} ${hombroIzq[1]} H${hombroDer[0]}`} /><path d={`M${caderaIzq[0]} ${caderaIzq[1]} H${caderaDer[0]}`} /></>}
      <polyline className={ficha.grupo_muscular !== 'pierna' ? 'guia-segmento-activo' : undefined} points={puntos(hombroDer, codoDer, mano)} /></g>
    <path d={`M${hombro[0]} ${hombro[1]} L${cabeza[0]} ${cabeza[1]}`} className="guia-cuello" />
    <circle cx={cabeza[0]} cy={cabeza[1]} r="13" className="guia-cabeza" />
    {articulaciones.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r="4.5" className="guia-articulacion" />)}
    {dosLados && (pose.frontal ? [hombroIzq, codoIzq, caderaIzq, rodillaTrasera] : [rodillaTrasera]).map((p, i) => <circle key={`trasera-${i}`} cx={p[0]} cy={p[1]} r="3.5" className="guia-articulacion guia-articulacion--lejos" />)}
    <g className="guia-zapatos">{dosLados && <path d={`M${pieTrasero[0] - 4} ${pieTrasero[1]} L${pieTrasero[0] + 10} 263`} />}<path d={`M${pie[0] - 4} ${pie[1]} L${pie[0] + 13} 263`} /></g>
    {barra && <g className="guia-pesas"><circle cx={carga[0]} cy={carga[1]} r="10" /><circle cx={carga[0]} cy={carga[1]} r="2" /><path d={`M${carga[0] - 16} ${carga[1]} H${carga[0] + 16}`} /></g>}
    {['laterales', 'zancadas'].includes(ficha.clave) && <g className="guia-pesas">{(pose.frontal ? [manoIzq, mano] : [mano]).map((p, i) => <g key={i}><path d={`M${p[0] - 10} ${p[1]} H${p[0] + 10}`} /><path d={`M${p[0] - 8} ${p[1] - 6} V${p[1] + 6} M${p[0] + 8} ${p[1] - 6} V${p[1] + 6}`} /></g>)}</g>}
    {!miniatura && <text x="24" y="28" className="guia-vista">VISTA {ficha.vista.toUpperCase()}</text>}
  </svg>
}

export default function DemostracionEjercicio({ ficha, permitirReproducir = false }) {
  const [progreso, setProgreso] = useState(0)
  const [reproduciendo, setReproduciendo] = useState(false)
  const [velocidad, setVelocidad] = useState(1)
  const [reducido, setReducido] = useState(() => typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches)
  const contenedor = useRef(null)
  const progresoActual = useRef(0)
  const detener = () => setReproduciendo(false)
  const seleccionar = valor => { detener(); progresoActual.current = valor; setProgreso(valor) }

  useEffect(() => {
    const preferencia = matchMedia('(prefers-reduced-motion: reduce)')
    const cambiar = () => { setReducido(preferencia.matches); setReproduciendo(false) }
    preferencia.addEventListener('change', cambiar)
    const alOcultar = () => { if (document.hidden) setReproduciendo(false) }
    document.addEventListener('visibilitychange', alOcultar)
    const observador = typeof IntersectionObserver !== 'undefined' ? new IntersectionObserver(([entrada]) => { if (!entrada.isIntersecting) setReproduciendo(false) }) : null
    if (contenedor.current) observador?.observe(contenedor.current)
    return () => { preferencia.removeEventListener('change', cambiar); document.removeEventListener('visibilitychange', alOcultar); observador?.disconnect() }
  }, [])

  useEffect(() => {
    if (!reproduciendo || reducido || !permitirReproducir) return
    let cuadro, anterior
    const animar = tiempo => {
      // No se recuperan de golpe segundos de una pestaña bloqueada.
      const siguiente = avanzar(progresoActual.current, anterior === undefined ? 0 : Math.min(100, tiempo - anterior), velocidad)
      anterior = tiempo
      progresoActual.current = siguiente
      setProgreso(siguiente)
      if (siguiente >= 1) setReproduciendo(false)
      else cuadro = requestAnimationFrame(animar)
    }
    cuadro = requestAnimationFrame(animar)
    return () => cancelAnimationFrame(cuadro)
  }, [reproduciendo, reducido, permitirReproducir, velocidad])

  const fase = faseActual(progreso)
  return <section className="guia-demostracion" aria-label={`Demostración de ${ficha.nombre}`} ref={contenedor}>
    {reducido && !ficha.esIsometrico ? <div className="guia-fotogramas">{[0, .5, 1].map((p, i) => <figure key={p}><FiguraEjercicio ficha={ficha} progreso={p} miniatura /><figcaption>{i + 1}. {ficha.fases[i][0]}</figcaption></figure>)}</div>
      : <FiguraEjercicio ficha={ficha} progreso={progreso} />}
    <div className="guia-controles">
      {permitirReproducir && !ficha.esIsometrico && <div className="guia-reproduccion"><button type="button" className="boton boton--principal" disabled={reducido} onClick={() => {
        if (reproduciendo) detener()
        else { if (progresoActual.current >= 1) { progresoActual.current = 0; setProgreso(0) } setReproduciendo(true) }
      }}>{reproduciendo ? 'Pausar' : 'Reproducir'}</button><button type="button" className="boton boton--secundario" onClick={() => seleccionar(0)}>Reiniciar</button>
        <label className="guia-velocidad">Velocidad<select value={velocidad} onChange={e => setVelocidad(Number(e.target.value))}><option value="0.5">0.5×</option><option value="1">1×</option><option value="1.5">1.5×</option></select></label></div>}
      {reducido && <p className="apoyo">Movimiento reducido activo. Consulta las tres posiciones y sus indicaciones.</p>}
      {!reducido && permitirReproducir && !ficha.esIsometrico && <label className="guia-avance">Recorrido de la demostración<input type="range" min="0" max="100" step="1" value={Math.round(progreso * 100)} onChange={e => seleccionar(Number(e.target.value) / 100)} /></label>}
      <div className="guia-fases" aria-label="Ver fases del ejercicio">{ficha.fases.map(([nombre], i) => <button type="button" key={nombre} aria-pressed={fase === i} onClick={() => seleccionar(i / 2)}><span>0{i + 1}</span>{nombre}</button>)}</div>
      <p className="guia-instruccion"><strong>{ficha.fases[fase][0]}.</strong> {ficha.fases[fase][1]}</p>
      {ficha.esIsometrico && <p className="apoyo">El dibujo muestra la posición de sostén. La preparación y la salida se explican en texto. Es un ejercicio estático; no cuenta repeticiones ni prescribe segundos.</p>}
    </div>
  </section>
}
