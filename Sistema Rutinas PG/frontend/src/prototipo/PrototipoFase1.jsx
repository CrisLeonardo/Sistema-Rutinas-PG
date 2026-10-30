import { createContext, useContext, useEffect, useRef, useState } from 'react'
import { Link, Navigate, Route, Routes, useLocation, useSearchParams } from 'react-router-dom'
import { usePreferencias } from '../contexto/ContextoPreferencias.jsx'
import { Icono, MarcaSenda, PaisajeSenda, SimboloSenda } from './MarcaSenda.jsx'

const BASE = '/prototipo/fase-1'
const Diseno = createContext(null)
const SIMBOLOS = [
  { id: 'camino', nombre: '01 / Camino', idea: 'Una S que avanza. Continuidad, flexibilidad y un siguiente paso.', ventaja: 'Une el nombre y el recorrido en una forma sencilla.', limite: 'Comprobar que se reconoce la S a tamaño pequeño.' },
  { id: 'paso', nombre: '02 / Paso', idea: 'Una persona en movimiento. Energía y acompañamiento cotidiano.', ventaja: 'Comunica actividad física de manera directa.', limite: 'Puede asociarse más con correr que con alimentación.' },
  { id: 'cumbre', nombre: '03 / Cumbre', idea: 'Un camino y su horizonte. Construir progreso a tu ritmo.', ventaja: 'Silueta compacta para un icono instalado.', limite: 'Puede parecer una marca de senderismo.' },
]

function Enlace({ a = '', children, className = '', ...props }) {
  const { consulta } = useContext(Diseno)
  return <Link to={`${BASE}${a ? `/${a}` : ''}${consulta}`} className={className} {...props}>{children}</Link>
}

function BotonEnlace({ a, children, secundario = false }) {
  return <Enlace a={a} className={`s1-boton${secundario ? ' s1-boton--secundario' : ''}`}>{children}<Icono nombre="flecha" /></Enlace>
}

export default function PrototipoFase1() {
  const [parametros, setParametros] = useSearchParams()
  const { pathname } = useLocation()
  const { tema, elegirTema } = usePreferencias()
  // Se conservan los enlaces de comparación antiguos. Sin parámetro explícito,
  // el prototipo sigue la misma preferencia que las pantallas del producto.
  const direccionUrl = parametros.get('direccion')
  const direccion = direccionUrl === 'tierra' || direccionUrl === 'pulso'
    ? direccionUrl
    : tema === 'light' ? 'tierra' : 'pulso'
  const simbolo = SIMBOLOS.some((s) => s.id === parametros.get('simbolo')) ? parametros.get('simbolo') : 'camino'
  const movil = parametros.get('vista') === 'movil'
  const [preferencias, setPreferencias] = useState({ objetivo: 'Crear constancia', experiencia: 'Estoy empezando', dias: '3 días' })
  const [completada, setCompletada] = useState(false)
  const contenido = useRef(null)
  const consulta = `?direccion=${direccion}&simbolo=${simbolo}${movil ? '&vista=movil' : ''}`

  function cambiar(clave, valor) {
    const siguiente = new URLSearchParams(parametros)
    siguiente.set(clave, valor)
    setParametros(siguiente, { replace: true })
  }

  useEffect(() => {
    if (direccionUrl === 'tierra' || direccionUrl === 'pulso') {
      elegirTema(direccionUrl === 'tierra' ? 'light' : 'dark')
    }
  }, [direccionUrl, elegirTema])

  useEffect(() => {
    const anterior = document.title
    document.title = 'Senda · Prototipo de identidad y experiencia'
    // El prototipo es una revisión de diseño, no una página pública indexable.
    const robots = document.createElement('meta')
    robots.name = 'robots'
    robots.content = 'noindex, nofollow'
    document.head.appendChild(robots)
    return () => { document.title = anterior; robots.remove() }
  }, [])

  useEffect(() => {
    contenido.current?.querySelector('h1')?.focus({ preventScroll: true })
    window.scrollTo({ top: 0, behavior: 'instant' })
  }, [pathname])

  const contexto = { consulta, simbolo, direccion, cambiar, preferencias, setPreferencias, completada, setCompletada }
  return <Diseno.Provider value={contexto}>
    <div className={`fase1 fase1--${direccion}${movil ? ' fase1--movil' : ''}`}>
      <a className="s1-saltar" href="#s1-contenido">Saltar al contenido</a>
      <aside className="s1-taller" aria-label="Controles de revisión del prototipo">
        <span><span className="s1-punto" /> Fase 1 <span className="s1-taller-detalle">/ Prototipo · datos ficticios</span></span>
        <div className="s1-controles">
          <label>Tema <select value={direccion} onChange={(e) => cambiar('direccion', e.target.value)}><option value="tierra">Claro · A / Tierra y camino</option><option value="pulso">Oscuro · B / Pulso y contraste</option></select></label>
          <button type="button" aria-pressed={movil} onClick={() => cambiar('vista', movil ? 'adaptable' : 'movil')}>Vista móvil</button>
          <Enlace a="identidad">Identidad <span aria-hidden="true">↗</span></Enlace>
          <Link to="/">Ir a la aplicación <span aria-hidden="true">↗</span></Link>
        </div>
      </aside>
      <div className="s1-lienzo">
        <header className="s1-cabecera">
          <Enlace aria-label="Senda, portada del prototipo"><MarcaSenda variante={simbolo} /></Enlace>
          <nav aria-label="Recorridos del prototipo">
            <Enlace a="hoy">Explorar mi día</Enlace>
            <Enlace a="primer-uso" className="s1-enlace-cabecera">Comenzar <Icono nombre="flecha" /></Enlace>
          </nav>
        </header>
        <main id="s1-contenido" ref={contenido} className="s1-contenido">
          <Routes>
            <Route index element={<Portada />} />
            <Route path="identidad" element={<Identidad />} />
            <Route path="primer-uso" element={<PrimerUso />} />
            <Route path="hoy" element={<Hoy />} />
            <Route path="sesion" element={<Sesion />} />
            <Route path="comida" element={<Comida />} />
            <Route path="avance" element={<Avance />} />
            <Route path="*" element={<Navigate to={`${BASE}${consulta}`} replace />} />
          </Routes>
        </main>
        <footer className="s1-pie"><MarcaSenda variante={simbolo} /><p>Un paso a la vez. A tu manera.</p><small>Prototipo de diseño · No genera ni guarda planes reales.</small></footer>
      </div>
    </div>
  </Diseno.Provider>
}

function Portada() {
  return <>
    <section className="s1-hero">
      <div className="s1-hero-texto">
        <p className="s1-ceja"><span className="s1-linea" /> ENTRENAMIENTO + ALIMENTACIÓN</p>
        <h1 tabIndex={-1}>Tu siguiente paso.<br /><em>Tu propia senda.</em></h1>
        <p className="s1-entradilla">Menos dudas sobre qué hacer hoy. Una guía para entrenar, organizar tus comidas y construir constancia, paso a paso.</p>
        <BotonEnlace a="primer-uso">Prueba el recorrido</BotonEnlace>
        <p className="s1-micro">Explora sin registrarte · Muestra con datos ficticios</p>
        <div className="s1-nota-local"><span className="s1-nota-icono"><Icono nombre="sol" /></span><p>Pensado para tu día a día.<br /><strong>Desde El Progreso, Guatemala.</strong></p></div>
      </div>
      <div className="s1-hero-arte">
        <span className="s1-arte-rotulo">CADA PASO CUENTA</span>
        <PaisajeSenda />
        <div className="s1-tarjeta-flotante"><span className="s1-icono-caja"><Icono nombre="check" /></span><div><strong>El progreso empieza con un paso.</strong><span>Encuentra el tuyo hoy.</span></div></div>
        <span className="s1-arte-pie">01 — EMPIEZA DONDE ESTÁS</span>
      </div>
    </section>
    <section className="s1-seccion s1-pasos">
      <div className="s1-titulo-seccion"><p className="s1-ceja">UN CAMINO MÁS CLARO</p><h2>De «¿por dónde empiezo?»<br />a «sé qué sigue».</h2></div>
      <div className="s1-pasos-rejilla">
        {[
          ['01', 'Cuéntanos sobre ti', 'En la aplicación, tu perfil ayuda a preparar tu plan. Aquí solo probarás el recorrido.'],
          ['02', 'Encuentra tu siguiente paso', 'Entrenamiento y alimentación en un inicio que te ayuda a decidir qué hacer hoy.'],
          ['03', 'Haz visible tu constancia', 'Registra tus sesiones y consulta cómo vas avanzando, sin compararte con otras personas.'],
        ].map(([n, titulo, texto]) => <article key={n}><span className="s1-numero">{n}</span><h3>{titulo}</h3><p>{texto}</p></article>)}
      </div>
    </section>
    <section className="s1-cierre"><div><p className="s1-ceja">A TU RITMO</p><h2>No necesitas tenerlo todo resuelto<br />para dar el primer paso.</h2></div><BotonEnlace a="hoy" secundario>Ver un día de ejemplo</BotonEnlace></section>
    <p className="s1-aclaracion">La aplicación actual es gratuita. <Link to="/registro">Crear una cuenta real</Link> · <Link to="/acceso">Ya tengo cuenta</Link>. El perfil y la generación de planes reales se completan en la aplicación.</p>
  </>
}

function Identidad() {
  const { simbolo, cambiar } = useContext(Diseno)
  return <section className="s1-pagina">
    <p className="s1-ceja">ESTUDIO DE IDENTIDAD / SENDA</p>
    <h1 tabIndex={-1}>Un nombre. Tres formas de avanzar.</h1>
    <p className="s1-entradilla">Tres símbolos y dos modos de una misma identidad: A para el modo claro y B para el oscuro. «Camino» es la propuesta inicial de símbolo, pendiente de evaluación.</p>
    <div className="s1-simbolos">{SIMBOLOS.map((s) => <article className={`s1-panel s1-propuesta${simbolo === s.id ? ' s1-propuesta--activa' : ''}`} key={s.id}>
      <div className="s1-muestra-marca"><SimboloSenda variante={s.id} /></div>
      <h2>{s.nombre}</h2><p>{s.idea}</p><p><strong>A favor:</strong> {s.ventaja}</p><p><strong>Por evaluar:</strong> {s.limite}</p>
      <div className="s1-tamanos" aria-label="Pruebas monocromas a 24, 32 y 48 píxeles">{[24, 32, 48].map((t) => <span key={t}><SimboloSenda variante={s.id} width={t} height={t} /><small>{t} px</small></span>)}</div>
      <button type="button" className="s1-boton s1-boton--secundario" aria-pressed={simbolo === s.id} onClick={() => cambiar('simbolo', s.id)}>{simbolo === s.id ? 'En vista previa' : 'Probar este símbolo'}<Icono nombre={simbolo === s.id ? 'check' : 'flecha'} /></button>
    </article>)}</div>
    <div className="s1-comparacion">
      <article className="s1-panel"><p className="s1-ceja">MODO CLARO / A</p><h2>Tierra y camino</h2><div className="s1-paleta" aria-label="Crema, verde bosque, salvia y ocre">{['#f6f3eb', '#244b3b', '#d9e3d2', '#e8bd65'].map((c) => <span key={c} style={{ background: c }} />)}</div><p>Cercanía y calma. Fondo crema, verde bosque y acento ocre para los logros. Modo claro compartido por la portada y las pantallas del sistema.</p><button className="s1-boton s1-boton--secundario" onClick={() => cambiar('direccion', 'tierra')}>Usar modo claro<Icono nombre="flecha" /></button></article>
      <article className="s1-panel"><p className="s1-ceja">MODO OSCURO / B</p><h2>Pulso y contraste</h2><div className="s1-paleta" aria-label="Carbón, lima, gris verde y ámbar">{['#151e1b', '#c4ed95', '#26372f', '#e8bd65'].map((c) => <span key={c} style={{ background: c }} />)}</div><p>Superficies oscuras y acento lima para destacar la acción siguiente. Misma marca y componentes, con colores adaptados al modo oscuro del sistema.</p><button className="s1-boton s1-boton--secundario" onClick={() => cambiar('direccion', 'pulso')}>Usar modo oscuro<Icono nombre="flecha" /></button></article>
    </div>
    <div className="s1-panel s1-reglas"><div><p className="s1-ceja">LENGUAJE VISUAL</p><h2>Claro, cercano y con espacio.</h2><p>Geist para leer y actuar; cifras tabulares para series y tiempos. Ilustración vectorial de caminos y formas orgánicas. La marca se dibuja en un solo color.</p></div><div><h3>Movimiento con un propósito</h3><p>Confirmaciones de 160 ms y transiciones de hasta 240 ms. Sin reproducción automática. Se respeta la preferencia de movimiento reducido del dispositivo.</p><h3>Aplicación del símbolo</h3><p>Área libre: un cuarto de su ancho. Mínimo propuesto: 24 px. El icono instalado se prueba en una muestra; su sustitución definitiva queda tras la selección.</p></div></div>
    <div className="s1-icono-instalado" aria-label="Muestra conceptual del icono instalado"><span><SimboloSenda variante={simbolo} /></span><div><strong>Senda</strong><p>Muestra del icono · No modifica la instalación actual.</p></div></div>
    <BotonEnlace a="">Probar la identidad en la portada</BotonEnlace>
  </section>
}

function PrimerUso() {
  const { preferencias, setPreferencias } = useContext(Diseno)
  const [paso, setPaso] = useState(0)
  const titulo = useRef(null)
  useEffect(() => { titulo.current?.focus({ preventScroll: true }) }, [paso])
  const pasos = [
    { clave: 'objetivo', titulo: '¿Qué te gustaría construir?', apoyo: 'Elige lo que más conecta contigo hoy.', opciones: ['Crear constancia', 'Organizar mi día', 'Retomar el entrenamiento'] },
    { clave: 'experiencia', titulo: 'Cada comienzo es distinto.', apoyo: '¿Cómo describirías tu experiencia entrenando?', opciones: ['Estoy empezando', 'Ya tengo experiencia'] },
    { clave: 'dias', titulo: 'Hazle un espacio a tu ritmo.', apoyo: '¿Cuántos días te gustaría reservar para entrenar?', opciones: ['2 días', '3 días', '4 días'] },
  ]
  const actual = pasos[paso]
  return <section className="s1-primer-uso s1-pagina">
    <div className="s1-progreso-pasos" aria-label={`Paso ${paso + 1} de 3`}>{pasos.map((p, i) => <span key={p.clave} className={i <= paso ? 's1-paso-activo' : ''} />)}</div>
    <p className="s1-ceja">CONOZCAMOS TU RITMO / {paso + 1} DE 3</p>
    <h1 tabIndex={-1} ref={titulo}>{actual.titulo}</h1><p className="s1-entradilla">{actual.apoyo}</p>
    <fieldset className="s1-opciones"><legend className="s1-solo-lector">{actual.apoyo}</legend>{actual.opciones.map((opcion) => <label className={preferencias[actual.clave] === opcion ? 's1-opcion--activa' : ''} key={opcion}><input type="radio" name={actual.clave} value={opcion} checked={preferencias[actual.clave] === opcion} onChange={() => setPreferencias({ ...preferencias, [actual.clave]: opcion })} /><span>{opcion}</span></label>)}</fieldset>
    <div className="s1-acciones">{paso > 0 && <button className="s1-texto-boton" onClick={() => setPaso(paso - 1)}><Icono nombre="atras" /> Atrás</button>}{paso < 2 ? <button className="s1-boton" onClick={() => setPaso(paso + 1)}>Continuar<Icono nombre="flecha" /></button> : <BotonEnlace a="hoy">Explorar mi día de ejemplo</BotonEnlace>}</div>
    <p className="s1-aviso">Estás probando una bienvenida. Tus elecciones solo se usan en esta muestra y se borran al recargar; no calculan un plan. El perfil biométrico y las restricciones de salud se completan en la aplicación real.</p>
  </section>
}

function NavegacionDia({ actual }) {
  return <nav className="s1-nav-dia" aria-label="Secciones del día de ejemplo">{[['hoy', 'Hoy', 'hoy'], ['sesion', 'Entrenar', 'entrenar'], ['comida', 'Comer', 'comer'], ['avance', 'Mi avance', 'avance']].map(([a, texto, icono]) => <Enlace a={a} key={a} aria-current={actual === a ? 'page' : undefined}><Icono nombre={icono} /><span>{texto}</span></Enlace>)}</nav>
}

function Hoy() {
  const { preferencias, completada } = useContext(Diseno)
  return <section className="s1-pagina s1-dia">
    <div className="s1-saludo"><div><p className="s1-ceja">TU DÍA, PASO A PASO</p><h1 tabIndex={-1}>Hoy es un buen comienzo.</h1><p>{preferencias.objetivo} · {preferencias.dias} para ti</p></div><span className="s1-insignia-demo">Día de ejemplo</span></div>
    <NavegacionDia actual="hoy" />
    <div className="s1-dia-rejilla">
      <article className="s1-entreno-destacado"><p className="s1-ceja">TU SIGUIENTE PASO</p><span className="s1-icono-grande"><Icono nombre={completada ? 'check' : 'entrenar'} /></span><h2>{completada ? 'Un paso más en tu senda.' : 'Un momento para moverte.'}</h2><p>{completada ? 'Terminaste el ejercicio de muestra. Puedes ver tu avance o volver a probar el registro.' : 'Explora cómo consultar un ejercicio y marcar tus series con una sola acción.'}</p><div className="s1-datos-cortos"><span><Icono nombre="reloj" /> A tu ritmo</span><span>1 ejercicio de muestra</span></div><BotonEnlace a={completada ? 'avance' : 'sesion'}>{completada ? 'Ver mi avance de ejemplo' : 'Probar sesión de entrenamiento'}</BotonEnlace></article>
      <div className="s1-pila"><article className="s1-panel s1-comida-tarjeta"><div className="s1-fila"><p className="s1-ceja">UNA IDEA PARA COMER</p><Icono nombre="comer" /></div><div className="s1-plato" aria-hidden="true"><span /><span /><span /></div><h2>Ingredientes conocidos.<br />Una comida sencilla.</h2><p>Pollo, arroz y vegetales · Ejemplo editorial</p><Enlace a="comida" className="s1-enlace-flecha">Explorar comida de ejemplo<Icono nombre="flecha" /></Enlace></article><article className="s1-panel s1-logro"><span className="s1-logro-sol"><Icono nombre="sol" /></span><div><h3>La constancia también se construye.</h3><p>{completada ? '3 de 3 pasos en la muestra.' : '2 de 3 pasos en la muestra.'} <Enlace a="avance">Ver próximo logro</Enlace></p></div></article></div>
    </div>
    <ResumenSemana />
    <p className="s1-aviso">Toda la actividad, las comidas y los logros de este recorrido son ficticios. No se ha creado una rutina personalizada.</p>
  </section>
}

function ResumenSemana() {
  const { completada } = useContext(Diseno)
  const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
  return <section className="s1-panel s1-semana"><div><p className="s1-ceja">TU SEMANA DE EJEMPLO</p><h3>Cada pequeño paso suma.</h3><p>{completada ? '3' : '2'} de 3 días marcados en esta muestra</p></div><div className="s1-dias">{['L', 'M', 'X', 'J', 'V', 'S', 'D'].map((d, i) => {
    const hecho = i === 0 || i === 2 || (i === 4 && completada)
    return <span key={i} role="img" aria-label={`${dias[i]}: ${hecho ? 'completado en la muestra' : 'sin registro en la muestra'}`}><span className={hecho ? 's1-dia-hecho' : ''}>{hecho ? <Icono nombre="check" /> : '·'}</span><small aria-hidden="true">{d}</small></span>
  })}</div></section>
}

function Sesion() {
  const { completada, setCompletada } = useContext(Diseno)
  const [series, setSeries] = useState(completada ? 3 : 0)
  const [descansoHasta, setDescansoHasta] = useState(null)
  const [segundos, setSegundos] = useState(0)
  const [tecnica, setTecnica] = useState(false)
  const [guardada, setGuardada] = useState(completada)
  const terminadas = series === 3
  useEffect(() => {
    if (!descansoHasta) return undefined
    function actualizar() {
      const restante = Math.max(0, Math.ceil((descansoHasta - Date.now()) / 1000))
      setSegundos(restante)
      if (!restante) setDescansoHasta(null)
    }
    actualizar()
    const temporizador = window.setInterval(actualizar, 250)
    return () => window.clearInterval(temporizador)
  }, [descansoHasta])
  function marcar() {
    setSeries((s) => s + 1)
    if (series < 2) { setSegundos(60); setDescansoHasta(Date.now() + 60_000) }
  }
  function reiniciar() { setSeries(0); setDescansoHasta(null); setSegundos(0); setGuardada(false); setCompletada(false) }
  return <section className="s1-pagina s1-sesion">
    <Enlace a="hoy" className="s1-enlace-flecha"><Icono nombre="atras" /> Volver a mi día</Enlace>
    <div className="s1-saludo"><div><p className="s1-ceja">SESIÓN DE EJEMPLO / 01</p><h1 tabIndex={-1}>Un paso. Una serie.</h1></div><span className="s1-insignia-demo">{series} / 3 series</span></div>
    <div className="s1-sesion-rejilla"><div className="s1-panel s1-ejercicio"><div className="s1-fila"><p className="s1-ceja">EJERCICIO DE MUESTRA</p><Icono nombre="entrenar" /></div><div className="s1-ilustracion-equipo" aria-label="Ilustración conceptual de una mancuerna"><svg viewBox="0 0 320 180" aria-hidden="true" fill="none"><ellipse cx="160" cy="151" rx="100" ry="8" fill="currentColor" opacity=".08" /><g transform="rotate(-25 160 90)" stroke="currentColor" strokeWidth="12" strokeLinecap="round"><path d="M111 90h98M92 61v58m19-69v80m98-80v80m19-69v58" /></g><circle cx="257" cy="37" r="16" stroke="currentColor" strokeWidth="2" strokeDasharray="3 5" /></svg></div><h2>Remo con mancuerna</h2><p>Registro ilustrativo · 3 series de 8 repeticiones</p><button className="s1-texto-boton" aria-expanded={tecnica} aria-controls="s1-tecnica" onClick={() => setTecnica(!tecnica)}>{tecnica ? 'Cerrar ficha de ejemplo' : 'Consultar ficha de ejemplo'} <Icono nombre="flecha" /></button>{tecnica && <div id="s1-tecnica" className="s1-aviso"><strong>Espacio previsto para la explicación visual.</strong><p>La ficha incluirá colocación, fases y errores frecuentes. La demostración técnica revisada y sus controles de reproducción corresponden a la fase 3; esta ilustración representa el equipo.</p></div>}</div>
      <div className="s1-panel s1-registro-series"><p className="s1-ceja">CONCÉNTRATE EN UNA SERIE</p><h2>{guardada ? '¡Ejemplo completado!' : terminadas ? 'Ya marcaste tus tres series.' : `Vamos con la serie ${series + 1}.`}</h2><p>Valores ficticios para probar el registro. No son una carga recomendada.</p><table><caption className="s1-solo-lector">Series de ejemplo</caption><thead><tr><th scope="col">Serie</th><th scope="col">Carga</th><th scope="col">Reps</th><th scope="col">Estado</th></tr></thead><tbody>{[1, 2, 3].map((n) => <tr key={n} className={n <= series ? 's1-serie-hecha' : ''}><th scope="row">{n}</th><td>10 kg</td><td>8</td><td>{n <= series ? <><Icono nombre="check" /><span className="s1-solo-lector">Completada</span></> : 'Pendiente'}</td></tr>)}</tbody></table>
      <div className="s1-estado-sesion" role="status">{guardada ? 'Ejercicio marcado en esta muestra. No se envió al servidor.' : descansoHasta ? 'Serie marcada. Descanso de ejemplo en curso.' : series ? `${series} de 3 series marcadas.` : 'Cuando quieras, prueba a marcar la primera serie.'}</div>
      {descansoHasta && <div className="s1-descanso"><span><Icono nombre="reloj" /><strong aria-label={`${segundos} segundos de descanso`}>{Math.floor(segundos / 60)}:{String(segundos % 60).padStart(2, '0')}</strong><small>Descanso de ejemplo</small></span><button className="s1-texto-boton" onClick={() => { setDescansoHasta(null); setSegundos(0) }}>Omitir descanso</button></div>}
      {!terminadas && <button className="s1-boton" disabled={Boolean(descansoHasta)} onClick={marcar}>Marcar serie {series + 1}<Icono nombre="check" /></button>}
      {terminadas && !guardada && <button className="s1-boton" onClick={() => { setCompletada(true); setGuardada(true) }}>Finalizar ejemplo<Icono nombre="check" /></button>}
      {guardada && <BotonEnlace a="avance">Ver mi avance de ejemplo</BotonEnlace>}
      {series > 0 && <button className="s1-texto-boton" onClick={reiniciar}>Reiniciar ejercicio de muestra</button>}
      </div></div>
    <p className="s1-aviso">La muestra conserva las series mientras estás en esta pantalla. Al finalizar, el inicio refleja el ejemplo completado hasta recargar. No registra actividad en tu cuenta.</p>
  </section>
}

function Comida() {
  return <section className="s1-pagina s1-dia"><p className="s1-ceja">ALIMENTACIÓN / EJEMPLO EDITORIAL</p><h1 tabIndex={-1}>Una comida que reconoces.</h1><NavegacionDia actual="comida" /><div className="s1-comida-detalle s1-panel"><div className="s1-plato s1-plato--grande" aria-hidden="true"><span /><span /><span /></div><div><h2>Pollo, arroz y vegetales</h2><p>Una combinación ilustrativa con ingredientes conocidos. El círculo de color es una ilustración conceptual, no una fotografía del plato.</p><ul><li>Pollo</li><li>Arroz</li><li>Vegetales de temporada</li></ul><p className="s1-aviso">No representa una porción personalizada ni una receta validada. Las porciones y costos reales se consultan en el plan de la aplicación. Recetas y sustituciones corresponden a la fase 4.</p><BotonEnlace a="hoy" secundario>Volver a mi día</BotonEnlace></div></div></section>
}

function Avance() {
  const { completada } = useContext(Diseno)
  return <section className="s1-pagina s1-dia"><p className="s1-ceja">MI AVANCE / EJEMPLO</p><h1 tabIndex={-1}>Mira lo que vas construyendo.</h1><NavegacionDia actual="avance" /><ResumenSemana /><div className="s1-panel s1-avance-logro"><span className="s1-logro-sol"><Icono nombre="sol" /></span><p className="s1-ceja">{completada ? 'LOGRO DE MUESTRA ALCANZADO' : 'TU PRÓXIMO LOGRO DE MUESTRA'}</p><h2>Tres pequeños pasos.</h2><p>{completada ? 'Has probado el recorrido de registro completo. Así podría verse una confirmación de constancia.' : 'Termina el ejercicio de ejemplo para ver cómo cambia tu resumen.'}</p><progress max="3" value={completada ? 3 : 2} aria-label="Pasos de ejemplo completados" /><p>{completada ? '3' : '2'} de 3 pasos · Datos ficticios</p><BotonEnlace a={completada ? 'hoy' : 'sesion'}>{completada ? 'Volver a mi día' : 'Probar el registro de series'}</BotonEnlace></div><p className="s1-aviso">Este logro muestra una dirección de diseño. No modifica los puntos, niveles ni reglas de «Mi senda» de la aplicación actual.</p></section>
}
