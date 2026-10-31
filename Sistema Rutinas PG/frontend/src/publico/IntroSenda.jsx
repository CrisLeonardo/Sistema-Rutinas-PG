import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'

export default function IntroSenda({ autenticado }) {
  const [error, setError] = useState(false)
  const [iniciado, setIniciado] = useState(false)
  const video = useRef(null)
  return <section className="s1-seccion publico-intro" id="intro-senda" aria-labelledby="intro-senda-titulo">
    <div className="publico-intro-cabecera">
      <div><p className="s1-ceja">CONOCE SENDA EN 30 SEGUNDOS</p><h2 id="intro-senda-titulo">Menos dudas.<br />Un siguiente paso más claro.</h2></div>
      <p>Entrenamiento, alimentación y seguimiento de tu avance en un mismo sistema. Dale play y descubre por dónde empezar.</p>
    </div>
    <div className="publico-intro-reproductor"><video
      ref={video}
      className="publico-intro-video"
      controls={iniciado}
      playsInline
      preload="none"
      width="1280"
      height="720"
      poster="/media/senda-intro-poster-v1.webp"
      aria-label="Conoce Senda: corto de 30 segundos con música y texto, sin narración"
      aria-describedby="intro-senda-contenido"
      onError={() => setError(true)}
      onPlay={() => setIniciado(true)}
    >
      <source src="/media/senda-intro-v1.mp4" type="video/mp4" />
      Tu navegador no puede reproducir este video. Puedes leer su contenido a continuación.
    </video>
    {!iniciado && !error && <button
      className="publico-intro-reproducir"
      type="button"
      onClick={() => video.current?.play().catch(() => setIniciado(true))}
    ><span className="solo-lectores">Reproducir el corto de Senda, 30 segundos</span></button>}
    </div>
    {error && <p role="status">El video no pudo cargarse. Puedes leer su contenido a continuación o <a href="/media/senda-intro-v1.mp4">abrir el archivo de video</a>.</p>}
    <div className="publico-intro-pie">
      <p>30 segundos · Música y texto · Se entiende sin sonido</p>
      <Link className="s1-enlace-flecha" to={autenticado ? '/panel' : '/registro'}>{autenticado ? 'Ir a mi día' : 'Dar mi primer paso'} <span aria-hidden="true">→</span></Link>
    </div>
    <details className="publico-intro-transcripcion" id="intro-senda-contenido">
      <summary>Leer el contenido del corto</summary>
      <p>Quieres empezar. ¿Por dónde? Senda es un sistema web que reúne entrenamiento, alimentación y tu progreso.</p>
      <p>Ten claro qué entrenar hoy: una rutina según tu perfil, con registro de series, carga y descansos. Organiza tus comidas: menú, porciones y compras en el mismo lugar. Cada paso cuenta: registra tu avance y consulta tus puntos, niveles e insignias personales.</p>
      <p>No tienes que hacerlo todo hoy. Solo dar el primer paso. Senda: crea tu cuenta gratis. Para personas adultas. Orientación general.</p>
      <p>Las pantallas del corto son esquemas ilustrativos de las funciones; no representan registros ni resultados de personas reales. La banda sonora es instrumental y no contiene voz.</p>
    </details>
  </section>
}
