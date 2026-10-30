import { useEffect, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { CambiarTema, NombreSenda } from '../componentes/MarcaProducto.jsx'
import { Icono, PaisajeSenda } from '../prototipo/MarcaSenda.jsx'
import { CORREO_CONTACTO, PAGINAS_PUBLICAS, PREGUNTAS } from './contenido.js'

function Accion({ children, to = '/registro', secundaria = false }) {
  return <Link className={`s1-boton${secundaria ? ' s1-boton--secundario' : ''}`} to={to}>{children}<Icono nombre="flecha" /></Link>
}

export default function SitioPublico() {
  const { pathname } = useLocation()
  const ruta = pathname.replace(/\/+$/, '') || '/'
  const { autenticado } = useSesion()
  const main = useRef(null)
  const pagina = PAGINAS_PUBLICAS[ruta] || PAGINAS_PUBLICAS['/']
  useEffect(() => {
    document.title = pagina.titulo
    const descripcion = document.querySelector('meta[name="description"]')
    if (descripcion) descripcion.content = pagina.descripcion
    const robots = document.querySelector('meta[name="robots"]')
    if (robots) robots.content = 'index, follow'
    main.current?.querySelector('h1')?.focus({ preventScroll: true })
    window.scrollTo({ top: 0, behavior: 'instant' })
    return () => {
      document.title = 'Senda · Mi cuenta'
      if (descripcion) descripcion.content = 'Accede a tu cuenta de Senda para consultar tus planes y tu avance.'
      if (robots) robots.content = 'noindex, nofollow'
    }
  }, [pathname, pagina])
  return <div className="fase1 sitio-publico">
    <a href="#contenido-publico" className="s1-saltar">Saltar al contenido</a>
    <div className="s1-lienzo">
      <header className="s1-cabecera publico-cabecera">
        <Link to="/" aria-label="Senda, inicio"><NombreSenda /></Link>
        <nav aria-label="Navegación pública"><Link to="/como-funciona">Cómo funciona</Link><Link to="/ayuda">Ayuda</Link><CambiarTema /><Link to={autenticado ? '/panel' : '/acceso'} className="s1-enlace-cabecera">{autenticado ? 'Mi día' : 'Entrar'}<Icono nombre="flecha" /></Link></nav>
      </header>
      <main id="contenido-publico" className="s1-contenido" ref={main}>
        {ruta === '/' ? <Portada autenticado={autenticado} /> : <Pagina ruta={ruta} />}
      </main>
      <footer className="s1-pie publico-pie"><Link to="/" aria-label="Senda, inicio"><NombreSenda /></Link><p>Un paso a la vez. A tu manera.</p><nav aria-label="Información del proyecto">{[['/como-funciona', 'Cómo funciona'], ['/ejercicios', 'Entrenamiento'], ['/alimentacion', 'Alimentación'], ['/comunidad', 'Mi senda'], ['/preguntas-frecuentes', 'Preguntas frecuentes'], ['/privacidad', 'Privacidad'], ['/terminos', 'Condiciones'], ['/sobre-el-proyecto', 'El proyecto'], ['/ayuda', 'Ayuda']].map(([to, texto]) => <Link key={to} to={to}>{texto}</Link>)}</nav></footer>
    </div>
  </div>
}

function Portada({ autenticado }) {
  return <>
    <section className="s1-hero"><div className="s1-hero-texto"><p className="s1-ceja"><span className="s1-linea" /> ENTRENAMIENTO + ALIMENTACIÓN</p><h1 tabIndex={-1}>Tu siguiente paso.<br /><em>Tu propia senda.</em></h1><p className="s1-entradilla">Menos dudas sobre qué hacer hoy. Una guía para entrenar, organizar tus comidas y construir constancia, paso a paso.</p><Accion to={autenticado ? '/panel' : '/registro'}>{autenticado ? 'Ir a mi día' : 'Crear cuenta gratis'}</Accion><Link to="/como-funciona" className="publico-accion-secundaria">Ver cómo funciona <Icono nombre="flecha" /></Link><p className="s1-micro">Para personas adultas · Sin tarjeta de pago</p><div className="s1-nota-local"><span className="s1-nota-icono"><Icono nombre="sol" /></span><p>Pensado para tu día a día.<br /><strong>Desde El Progreso, Guatemala.</strong></p></div></div><div className="s1-hero-arte"><span className="s1-arte-rotulo">CADA PASO CUENTA</span><PaisajeSenda /><div className="s1-tarjeta-flotante"><span className="s1-icono-caja"><Icono nombre="check" /></span><div><strong>El progreso empieza con un paso.</strong><span>Encuentra el tuyo hoy.</span></div></div><span className="s1-arte-pie">EMPIEZA DONDE ESTÁS</span></div></section>
    <Pasos />
    <section className="s1-seccion"><div className="s1-titulo-seccion"><p className="s1-ceja">CONOCE EL RECORRIDO</p><h2>Una muestra antes<br />de dar el primer paso.</h2></div><Demostracion /></section>
    <section className="s1-seccion"><p className="s1-ceja">LO QUE NECESITAS SABER</p><h2 className="publico-titulo">Preguntas antes de empezar.</h2><Preguntas /></section>
    <section className="s1-cierre"><div><p className="s1-ceja">A TU RITMO</p><h2>Tu constancia empieza<br />con una acción pequeña.</h2></div><Accion to={autenticado ? '/panel' : '/registro'}>{autenticado ? 'Abrir mi día' : 'Crear mi cuenta'}</Accion></section>
    <p className="s1-aclaracion">Senda ofrece orientación general y no sustituye la atención profesional. Consulta el <Link to="/terminos">alcance del servicio</Link> y cómo se usan <Link to="/privacidad">tus datos</Link>.</p>
  </>
}

function Pasos() {
  return <section className="s1-seccion s1-pasos"><div className="s1-titulo-seccion"><p className="s1-ceja">UN CAMINO MÁS CLARO</p><h2>De «¿por dónde empiezo?»<br />a «sé qué sigue».</h2></div><div className="s1-pasos-rejilla publico-cuatro-pasos">{[
    ['01', 'Crea tu cuenta', 'Guarda el acceso con tu correo y una contraseña propia.'],
    ['02', 'Completa tu perfil', 'Registra tus medidas, actividad, objetivos y antecedentes de salud.'],
    ['03', 'Genera tu plan', 'Consulta alimentación y entrenamiento en el mismo lugar.'],
    ['04', 'Haz visible tu constancia', 'Anota tus series y tu avance semanal para dar continuidad a tu recorrido.'],
  ].map(([n, titulo, texto]) => <article key={n}><span className="s1-numero">{n}</span><h3>{titulo}</h3><p>{texto}</p></article>)}</div></section>
}

function Demostracion() {
  const [series, setSeries] = useState(0)
  return <div className="publico-demo"><article className="s1-panel"><p className="s1-ceja">ENTRENAMIENTO / DATOS FICTICIOS</p><h3>Un ejercicio. Una serie a la vez.</h3><p>Remo con mancuerna · 3 series de ejemplo</p><div className="publico-series" aria-label={`${series} de 3 series marcadas en la muestra`}>{[1, 2, 3].map(n => <span key={n}>{n <= series ? <Icono nombre="check" /> : n}<small>{n <= series ? 'Marcada' : 'Pendiente'}</small></span>)}</div><button className="s1-boton" type="button" onClick={() => setSeries(series === 3 ? 0 : series + 1)}>{series === 3 ? 'Reiniciar muestra' : 'Probar registro de una serie'}<Icono nombre={series === 3 ? 'flecha' : 'check'} /></button><p className="publico-confirmacion" role="status">{series ? `${series} de 3 series marcadas solo en esta muestra.` : 'Prueba el registro sin crear una cuenta.'}</p><details><summary>Cómo leer esta vista</summary><p>El número indica la serie. La marca confirma el registro. En tu cuenta, la sesión muestra también repeticiones, carga y descanso. Esta vista explica los controles; no evalúa tu postura ni muestra una demostración técnica revisada.</p></details></article><article className="s1-panel"><p className="s1-ceja">ALIMENTACIÓN / EJEMPLO EDITORIAL</p><div className="s1-plato" aria-hidden="true"><span /><span /><span /></div><h3>Pollo, arroz y vegetales</h3><p>Una idea con ingredientes conocidos. En tu cuenta, el menú muestra las porciones del plan y permite consultar la lista de compras.</p><p className="s1-aviso">La ilustración es conceptual. Este ejemplo no indica porciones, costo ni un plan personalizado.</p><Link to="/alimentacion" className="s1-enlace-flecha">Conocer alimentación<Icono nombre="flecha" /></Link></article></div>
}

function Preguntas() {
  return <div className="publico-preguntas">{PREGUNTAS.map(([pregunta, respuesta]) => <details key={pregunta}><summary>{pregunta}</summary><p>{respuesta}</p></details>)}</div>
}

function Contacto() {
  return <div className="s1-panel"><h2>Contacto y soporte</h2><p>Escribe a <a href={`mailto:${CORREO_CONTACTO}`}>{CORREO_CONTACTO}</a>. Para reportar un problema, indica la pantalla y lo que ocurrió; evita incluir contraseñas o datos de salud.</p></div>
}

function Pagina({ ruta }) {
  const titulos = {
    '/como-funciona': 'Un recorrido sencillo, a tu ritmo.', '/ejercicios': 'Entrena con un siguiente paso claro.',
    '/alimentacion': 'Organiza lo que vas a comer.', '/comunidad': 'Primero, tu propia constancia.',
    '/preguntas-frecuentes': 'Resuelve tus dudas antes de empezar.', '/sobre-el-proyecto': 'Una senda que empieza cerca.',
    '/privacidad': 'Tus datos, con un propósito claro.', '/terminos': 'Qué puedes esperar de Senda.', '/ayuda': 'Encuentra cómo seguir.',
  }
  return <section className="s1-pagina publico-pagina"><p className="s1-ceja">SENDA / {PAGINAS_PUBLICAS[ruta]?.titulo.split(' · ')[0]}</p><h1 tabIndex={-1}>{titulos[ruta]}</h1>
    {ruta === '/como-funciona' && <><Pasos /><div className="s1-panel"><h2>Antes de empezar</h2><p>Necesitas tener 18 años cumplidos o más y una conexión a internet. Completa el perfil con información correcta: algunas condiciones de salud quedan fuera del alcance del sistema y requieren orientación profesional.</p><Accion>Crear cuenta</Accion></div></>}
    {ruta === '/ejercicios' && <><p className="s1-entradilla">La rutina organiza tus días y ejercicios. Durante el entrenamiento puedes registrar las series, usar el cronómetro y consultar tu historial. Las sugerencias de carga dependen de tus registros previos.</p><div className="s1-panel"><h2>Entiende cada movimiento</h2><p>La biblioteca reúne los ejercicios del catálogo y un piloto de diez fichas visuales con preparación, fases y errores frecuentes. Las ilustraciones del piloto están pendientes de revisión técnica.</p><Accion to="/entrenar/biblioteca">Consultar la biblioteca</Accion></div><Demostracion /></>}
    {ruta === '/alimentacion' && <><div className="publico-texto"><h2>Plan, menú y compras</h2><p>El plan reúne el objetivo energético y sus macronutrientes. El menú permite consultar los alimentos y porciones calculados; la lista de compras agrupa lo necesario para la semana.</p><h2>Información para decidir</h2><p>Los precios del catálogo son estimaciones, no una cotización de tu mercado. El piloto de alimentación permite guardar restricciones, preparar siete días con recetas y recalcular cambios y compras. Las 18 recetas están pendientes de revisión profesional. El filtro excluye ingredientes declarados, pero no certifica ausencia de trazas ni contacto cruzado. Si tu restricción no figura en la lista, la propuesta se detiene para solicitar valoración profesional.</p></div><Accion>Crear cuenta</Accion></>}
    {ruta === '/comunidad' && <div className="s1-panel"><h2>Tu avance es personal</h2><p>Senda ya cuenta con puntos, niveles e insignias personales. Tu recorrido se basa en tus propios registros. Puedes consultar tus puntos, niveles e insignias en Mi senda. Los retos con amigos y los grupos están pospuestos; actualmente el seguimiento es individual.</p><Accion to="/avance/senda">Ver Mi senda</Accion></div>}
    {ruta === '/preguntas-frecuentes' && <Preguntas />}
    {ruta === '/sobre-el-proyecto' && <div className="publico-texto"><h2>Desde El Progreso, Jutiapa</h2><p>Senda nace del Proyecto de Graduación de Leonardo Zepeda, Universidad Mariano Gálvez de Guatemala. Busca reunir planes de alimentación, rutinas y seguimiento con atención al contexto local.</p><h2>Un proyecto en evolución</h2><p>La experiencia se mejora por etapas. El catálogo inicial y sus costos requieren actualización de campo. La disponibilidad de una función no demuestra por sí sola resultados de adherencia ni beneficios clínicos.</p><Contacto /></div>}
    {ruta === '/privacidad' && <div className="publico-texto"><h2>Información que utiliza el sistema</h2><p>Tu cuenta registra nombre, correo y una contraseña almacenada mediante un resumen criptográfico. Al completar tu perfil, aportas medidas, edad, actividad, objetivos, lesiones y condiciones relevantes. El sistema guarda planes, sesiones y avances para darles continuidad. Si usas alimentación práctica, guarda por separado tus preferencias, alergias e intolerancias declaradas, alimentos excluidos y la semana calculada; se utilizan para filtrar ingredientes y recalcular comidas y compras. Estos datos personales no se publican ni se comparten entre cuentas.</p><h2>Seguimiento individual</h2><p>Tus puntos e insignias se consultan en tu propia cuenta. Los grupos y retos con amigos están pospuestos y no están disponibles en la entrega actual.</p><h2>Acceso y uso</h2><p>Las consultas personales se filtran por la cuenta autenticada. Las pantallas de administración no permiten consultar el perfil biométrico de otras personas. Quienes operan la infraestructura tienen responsabilidades técnicas sobre la base de datos y los respaldos; no se debe interpretar la interfaz como una garantía de anonimato frente al operador.</p><h2>Datos en el dispositivo</h2><p>El tema y otras preferencias se guardan en el navegador. La sesión usa el almacenamiento de la pestaña y los borradores de entrenamiento pueden guardarse localmente. Cierra sesión al usar un dispositivo compartido. Las fuentes y algunos iconos se cargan desde proveedores externos; el navegador realiza conexiones a esos servicios.</p><h2>Recuperación y consultas</h2><p>Si solicitas recuperar el acceso, el proveedor de correo configurado procesa tu dirección y el mensaje. El enlace tiene vencimiento y un solo uso; el sistema conserva su hash. No envíes contraseñas por correo. Para consultar el manejo o la eliminación de tus datos, utiliza el canal de contacto publicado por el proyecto.</p><Contacto /></div>}
    {ruta === '/terminos' && <div className="publico-texto"><h2>Alcance del servicio</h2><p>Senda ofrece orientación general de alimentación y entrenamiento para personas de 18 años cumplidos o más. No diagnostica, trata enfermedades ni sustituye la valoración de profesionales. No observa ni corrige tu postura real.</p><h2>Cuenta y uso responsable</h2><p>Registra información correcta, usa una contraseña propia y no compartas tu acceso. Revisa las advertencias del plan. Ante necesidades de salud fuera del alcance del sistema, busca orientación profesional.</p><h2>Gratuidad y disponibilidad</h2><p>Los servicios actuales son gratuitos. La disponibilidad depende de la conexión y de los servicios que utiliza el proyecto; puede haber esperas o interrupciones. No se garantizan resultados físicos, costos de compra ni progreso en un plazo determinado.</p><h2>Ejemplos y funciones futuras</h2><p>Las muestras públicas son ficticias y no constituyen tu plan. Los retos sociales y demostraciones técnicas que todavía no están disponibles se identifican como tales. Las recetas del piloto y su ajuste de porciones están pendientes de revisión profesional; no se consideran validadas por haber sido calculadas. Estas condiciones describen la entrega actual y pueden actualizarse junto con el servicio.</p><Contacto /></div>}
    {ruta === '/ayuda' && <><div className="publico-demo"><article className="s1-panel"><h2>No puedo entrar</h2><p>Comprueba tu correo y contraseña. Si el servidor está iniciando, espera el mensaje del formulario antes de volver a intentarlo.</p><Accion to="/acceso">Ir al acceso</Accion></article><article className="s1-panel"><h2>Olvidé mi contraseña</h2><p>Solicita un enlace al correo de tu cuenta. El formulario indica si el servicio de envío está disponible.</p><Accion to="/recuperar-acceso" secundaria>Recuperar acceso</Accion></article></div><Contacto /></>}
  </section>
}
