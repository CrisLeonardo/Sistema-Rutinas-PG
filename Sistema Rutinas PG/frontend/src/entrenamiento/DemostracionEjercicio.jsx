import { useEffect, useId, useRef, useState } from 'react'
import { avanzar, faseActual, fotogramasPara, posePara } from './movimientos.mjs'
import { movimientoReducido, useMovimientoReducido } from '../interaccion/movimiento.js'

const puntos = (...lista) => lista.map(p => p.join(',')).join(' ')

export function FiguraEjercicio({ ficha, progreso = 0, miniatura = false }) {
  const id = useId()
  const pose = posePara(ficha.clave, progreso)
  if (!pose) return <p>Ilustración no disponible. Consulta las fases escritas.</p>
  const { cabeza, hombro, cadera, caderaDer, caderaIzq, pie, pieTrasero, mano, manoIzq, hombroIzq, hombroDer, codoDer, codoIzq, rodilla, rodillaTrasera } = pose
  const barra = ['press-banca', 'remo-barra', 'curl-barra', 'sentadilla', 'peso-muerto-rumano', 'press-militar'].includes(ficha.clave)
  const carga = ficha.clave === 'sentadilla' ? [hombro[0] - 12, hombro[1] - 5] : mano
  const dosLados = pose.dosLados || pose.frontal || ficha.clave === 'zancadas'
  const soloTrenSuperior = ficha.clave === 'aperturas'
  const articulaciones = soloTrenSuperior ? [hombroDer, codoDer, mano] : [hombroDer, codoDer, mano, caderaDer, rodilla, pie]
  return <svg className={`guia-figura${miniatura ? ' guia-figura--mini' : ''}`} viewBox="0 0 420 300" role={miniatura ? undefined : 'img'} aria-hidden={miniatura || undefined} aria-labelledby={miniatura ? undefined : `${id}-titulo ${id}-detalle`}>
    {!miniatura && <><title id={`${id}-titulo`}>{`${ficha.nombre} · ${ficha.vista.toLowerCase()}`}</title>
    <desc id={`${id}-detalle`}>{ficha.esIsometrico ? 'Posición de sostén, sin movimiento repetido.' : `Esquema de la fase ${ficha.fases[faseActual(progreso, ficha)][0].toLowerCase()}. ${ficha.fases[faseActual(progreso, ficha)][1]}`} Los círculos señalan las articulaciones. La vista es simplificada.</desc></>}
    {!pose.colgado && <path d="M 54 267 H 366" className="guia-suelo" />}
    {ficha.clave === 'press-inclinado' && <g className="guia-equipo"><path d="M136 118 L210 190 H236 M154 142 V263 M227 190 V263" className="guia-banca" /></g>}
    {ficha.clave === 'aperturas' && <g className="guia-equipo"><path d="M186 157 H234 L247 237 H173 Z M180 237 V263 M240 237 V263" /><text x="275" y="223" className="guia-vista">BANCA</text></g>}
    {ficha.clave === 'remo-mancuerna' && <g className="guia-equipo"><path d="M99 190 H278 M119 190 V263 M263 190 V263" className="guia-banca" /></g>}
    {pose.colgado && <g className="guia-equipo"><path d="M106 265 V46 H321 V265" /><path d="M152 46 H270" className="guia-banca" /></g>}
    {ficha.clave === 'prensa' && <g className="guia-equipo"><path d="M107 151 L173 224 H197 M116 165 V263 M190 224 V263 M220 213 L320 121 M237 228 L337 136" /><path d={`M${pie[0] - 14} ${pie[1] - 19} L${pie[0] + 14} ${pie[1] + 19}`} className="guia-banca" /></g>}
    {ficha.clave === 'triceps-polea' && <g className="guia-equipo"><path d="M333 265 V40 H266" /><circle cx="266" cy="40" r="6" /><path d={`M266 46 L${mano[0]} ${mano[1]}`} className="guia-cable" /><path d={`M${mano[0] - 10} ${mano[1]} H${mano[0] + 10}`} className="guia-barra-polea" /></g>}
    {ficha.clave === 'fondos-bancas' && <g className="guia-equipo"><path d="M79 154 H156 M92 154 V263 M145 154 V263 M274 224 H335 M282 224 V263 M327 224 V263" className="guia-banca" /></g>}
    {ficha.clave === 'press-banca' && <g className="guia-equipo"><path d="M110 188 V264 M235 188 V264" /><path d="M92 185 H250" className="guia-banca" /><text x="101" y="229" className="guia-vista">BANCA</text></g>}
    {ficha.clave === 'jalon-pecho' && <g className="guia-equipo"><path d="M94 265 V31 H306 V265 M163 223 H237 M200 223 V265" /><circle cx="200" cy="33" r="7" /><path d={`M200 40 V${mano[1] - 8}`} className="guia-cable" /><path d={`M${manoIzq[0]} ${mano[1]} Q200 ${mano[1] - 16} ${mano[0]} ${mano[1]}`} className="guia-barra-polea" /></g>}
    {dosLados && <g className="guia-miembro guia-miembro--lejos">{!soloTrenSuperior && <polyline points={puntos(caderaIzq, rodillaTrasera, pieTrasero)} />}{(pose.frontal || pose.dosLados) && <polyline points={puntos(hombroIzq, codoIzq, manoIzq)} />}</g>}
    <g className="guia-miembro">{!soloTrenSuperior && <polyline className={ficha.grupo_muscular === 'pierna' ? 'guia-segmento-activo' : undefined} points={puntos(caderaDer, rodilla, pie)} />}<path d={`M${cadera[0]} ${cadera[1]} L${hombro[0]} ${hombro[1]}`} />
      {pose.frontal && <><path d={`M${hombroIzq[0]} ${hombroIzq[1]} H${hombroDer[0]}`} />{!soloTrenSuperior && <path d={`M${caderaIzq[0]} ${caderaIzq[1]} H${caderaDer[0]}`} />}</>}
      <polyline className={ficha.grupo_muscular !== 'pierna' ? 'guia-segmento-activo' : undefined} points={puntos(hombroDer, codoDer, mano)} /></g>
    <path d={`M${hombro[0]} ${hombro[1]} L${cabeza[0]} ${cabeza[1]}`} className="guia-cuello" />
    <circle cx={cabeza[0]} cy={cabeza[1]} r="13" className="guia-cabeza" />
    {articulaciones.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r="4.5" className="guia-articulacion" />)}
    {dosLados && (soloTrenSuperior ? [hombroIzq, codoIzq] : pose.frontal ? [hombroIzq, codoIzq, caderaIzq, rodillaTrasera] : [rodillaTrasera]).map((p, i) => <circle key={`trasera-${i}`} cx={p[0]} cy={p[1]} r="3.5" className="guia-articulacion guia-articulacion--lejos" />)}
    {!soloTrenSuperior && <g className="guia-zapatos">{dosLados && <path d={`M${pieTrasero[0] - 4} ${pieTrasero[1]} H${pieTrasero[0] + 10}`} />}<path d={`M${pie[0] - 4} ${pie[1]} H${pie[0] + 13}`} /></g>}
    {barra && <g className="guia-pesas"><circle cx={carga[0]} cy={carga[1]} r="10" /><circle cx={carga[0]} cy={carga[1]} r="2" /><path d={`M${carga[0] - 16} ${carga[1]} H${carga[0] + 16}`} /></g>}
    {['laterales', 'zancadas', 'press-inclinado', 'aperturas', 'remo-mancuerna', 'pajaros', 'press-arnold', 'curl-alterno'].includes(ficha.clave) && <g className="guia-pesas">{(pose.frontal || ficha.clave === 'press-inclinado' ? [manoIzq, mano] : [mano]).map((p, i) => <g key={i}><path d={`M${p[0] - 10} ${p[1]} H${p[0] + 10}`} /><path d={`M${p[0] - 8} ${p[1] - 6} V${p[1] + 6} M${p[0] + 8} ${p[1] - 6} V${p[1] + 6}`} /></g>)}</g>}
    {ficha.clave === 'rueda' && <g className="guia-pesas"><circle cx={mano[0]} cy={mano[1]} r="11" /><circle cx={mano[0]} cy={mano[1]} r="3" /><path d={`M${mano[0] - 14} ${mano[1]} H${mano[0] + 14}`} /></g>}
    {pose.agarre && !miniatura && <text x="24" y="287" className="guia-vista">{pose.agarre.toUpperCase()}</text>}
    {!miniatura && <text x="24" y="28" className="guia-vista">VISTA {ficha.vista.toUpperCase()}</text>}
  </svg>
}

export default function DemostracionEjercicio({ ficha, permitirReproducir = false }) {
  const [progreso, setProgreso] = useState(0)
  // Una demostración al abrir, con pausa inmediata y sin bucle obligatorio.
  const [reproduciendo, setReproduciendo] = useState(() => permitirReproducir && !ficha.esIsometrico && !movimientoReducido())
  const [velocidad, setVelocidad] = useState(1)
  const [repetir, setRepetir] = useState(false)
  const reducido = useMovimientoReducido()
  const contenedor = useRef(null)
  const progresoActual = useRef(0)
  const detener = () => setReproduciendo(false)
  const seleccionar = valor => { detener(); progresoActual.current = valor; setProgreso(valor) }

  useEffect(() => {
    const alOcultar = () => { if (document.hidden) setReproduciendo(false) }
    document.addEventListener('visibilitychange', alOcultar)
    const observador = typeof IntersectionObserver !== 'undefined' ? new IntersectionObserver(([entrada]) => { if (!entrada.isIntersecting) setReproduciendo(false) }) : null
    if (contenedor.current) observador?.observe(contenedor.current)
    return () => { document.removeEventListener('visibilitychange', alOcultar); observador?.disconnect() }
  }, [])

  useEffect(() => { if (reducido) setReproduciendo(false) }, [reducido])

  useEffect(() => {
    if (!reproduciendo || reducido || !permitirReproducir) return
    let cuadro, anterior
    const animar = tiempo => {
      // No se recuperan de golpe segundos de una pestaña bloqueada.
      const siguiente = avanzar(progresoActual.current, anterior === undefined ? 0 : Math.min(100, tiempo - anterior), velocidad)
      anterior = tiempo
      progresoActual.current = siguiente
      setProgreso(siguiente)
      if (siguiente >= 1 && !repetir) setReproduciendo(false)
      else {
        if (siguiente >= 1) { progresoActual.current = 0; setProgreso(0) }
        cuadro = requestAnimationFrame(animar)
      }
    }
    cuadro = requestAnimationFrame(animar)
    return () => cancelAnimationFrame(cuadro)
  }, [reproduciendo, reducido, permitirReproducir, velocidad, repetir])

  const fase = faseActual(progreso, ficha)
  const fotogramas = fotogramasPara(ficha)
  return <section className="guia-demostracion" aria-label={`Demostración de ${ficha.nombre}`} ref={contenedor}>
    <div className="guia-escenario"><span>{ficha.esIsometrico ? 'POSICIÓN DE SOSTÉN' : 'MIRA · PAUSA · PRACTICA'}</span><span className="guia-escenario__estado">{ficha.esIsometrico ? 'Sin repeticiones' : reproduciendo ? 'En movimiento' : progreso >= 1 ? 'Recorrido completo' : 'En pausa'}</span></div>
    <div className="guia-lienzo">{reducido && !ficha.esIsometrico ? <div className="guia-fotogramas">{fotogramas.map((p, i) => <figure key={p}><FiguraEjercicio ficha={ficha} progreso={p} miniatura /><figcaption>{i + 1}. {ficha.fases[i][0]}</figcaption></figure>)}</div>
      : <FiguraEjercicio ficha={ficha} progreso={progreso} />}</div>
    <div className="guia-controles">
      {permitirReproducir && !ficha.esIsometrico && <div className="guia-reproduccion"><button type="button" className="boton boton--principal" disabled={reducido} onClick={() => {
        if (reproduciendo) detener()
        else { if (progresoActual.current >= 1) { progresoActual.current = 0; setProgreso(0) } setReproduciendo(true) }
      }} aria-pressed={reproduciendo}><span aria-hidden="true">{reproduciendo ? 'Ⅱ' : '▶'}</span>{reproduciendo ? 'Pausar' : progreso >= 1 ? 'Ver de nuevo' : 'Ver movimiento'}</button><button type="button" className="boton boton--secundario" onClick={() => seleccionar(0)}>Al inicio</button>
        <label className="guia-velocidad">Velocidad<select value={velocidad} onChange={e => setVelocidad(Number(e.target.value))}><option value="0.5">0.5×</option><option value="1">1×</option><option value="1.5">1.5×</option></select></label></div>}
      {reducido && <p className="apoyo">Movimiento reducido activo. Consulta las tres posiciones y sus indicaciones.</p>}
      {permitirReproducir && !ficha.esIsometrico && !reducido && <label className="guia-check guia-repetir"><input type="checkbox" checked={repetir} onChange={evento => setRepetir(evento.target.checked)} />Repetir el recorrido mientras lo veo</label>}
      {!reducido && permitirReproducir && !ficha.esIsometrico && <label className="guia-avance">Recorrido de la demostración<input type="range" min="0" max="100" step="1" value={Math.round(progreso * 100)} onChange={e => seleccionar(Number(e.target.value) / 100)} /></label>}
      <div className="guia-fases" aria-label="Ver fases del ejercicio">{ficha.fases.map(([nombre], i) => <button type="button" key={nombre} aria-pressed={fase === i} onClick={() => seleccionar(fotogramas[i])}><span>0{i + 1}</span>{nombre}</button>)}</div>
      <p className="guia-instruccion"><strong>{ficha.fases[fase][0]}.</strong> {ficha.fases[fase][1]}</p>
      {ficha.esIsometrico && <p className="apoyo">El dibujo muestra la posición de sostén. La preparación y la salida se explican en texto. Es un ejercicio estático; no cuenta repeticiones ni prescribe segundos.</p>}
    </div>
  </section>
}
