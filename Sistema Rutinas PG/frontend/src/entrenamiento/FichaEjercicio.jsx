import { lazy, Suspense } from 'react'
import LimiteRecurso from '../componentes/LimiteRecurso.jsx'
import { animacionPublicable, fichaPara, GRUPOS } from './fichas.mjs'

const Demostracion = lazy(() => import('./DemostracionEjercicio.jsx'))

export default function FichaEjercicio({ ejercicio, revision = false }) {
  const ficha = fichaPara(ejercicio)
  if (!ficha) return <div className="pila-4"><p className="rotulo">{GRUPOS[ejercicio.grupo_muscular] ?? ejercicio.grupo_muscular} · {ejercicio.equipamiento}</p><p className="cuerpo">{ejercicio.descripcion || 'Todavía no hay indicaciones registradas para este ejercicio.'}</p><p className="aviso">Este ejercicio aún no tiene una ficha visual vinculada. Pide que te expliquen la técnica antes de realizarlo.</p></div>
  return <article className="guia-ficha pila-5">
    <div className="guia-meta"><span>{GRUPOS[ficha.grupo_muscular]}</span><span>{ficha.equipamiento}</span><span>{ficha.vista}</span></div>
    <p className="guia-objetivo">{ficha.objetivo}</p>
    {ficha.esIsometrico && ejercicio.repeticiones_min > 0 && ejercicio.duracion_segundos_min == null && <p className="aviso aviso--aviso">La plancha es un sostén. Este plan, anterior a la duración en segundos, la expresa en repeticiones; vuelve a calcular tu plan para obtener la duración revisada. Esas cifras no se convierten automáticamente en segundos.</p>}
    <p className="guia-estado">{animacionPublicable(ficha) ? `${ficha.esIsometrico ? 'Posición esquemática' : 'Guía esquemática animada'} · revisión técnica: ${ficha.validacion.responsable}, ${ficha.validacion.fecha}` : revision ? 'Piloto de revisión · demostración pendiente de validar' : 'Guía esquemática animada · pendiente de revisión técnica'}</p>
    <LimiteRecurso key={ficha.clave} respaldo={<p className="aviso">No se pudo cargar la ilustración. Puedes seguir leyendo las fases.</p>}><Suspense fallback={<p role="status">Cargando ilustración; las indicaciones están disponibles debajo.</p>}><Demostracion key={ficha.clave} ficha={ficha} permitirReproducir /></Suspense></LimiteRecurso>
    <section><h3 className="titulo-tarjeta">Antes de empezar</h3><p>{ficha.inicio}</p><dl className="guia-datos"><div><dt>Equipo y apoyos</dt><dd>{ficha.material}</dd></div><div><dt>Preparación técnica</dt><dd>{ficha.dificultad}</dd></div></dl></section>
    <section><h3 className="titulo-tarjeta">Paso a paso</h3><ol className="guia-pasos">{ficha.fases.map(([titulo, texto]) => <li key={titulo}><strong>{titulo}</strong><p>{texto}</p></li>)}</ol></section>
    <div className="guia-dos-columnas"><section><h3 className="titulo-tarjeta">Qué cuidar</h3><ul>{ficha.claves.map(t => <li key={t}>{t}</li>)}</ul></section><section><h3 className="titulo-tarjeta">Errores frecuentes</h3><ul>{ficha.errores.map(t => <li key={t}>{t}</li>)}</ul></section></div>
    <details className="guia-detalles"><summary>Variantes y otras opciones</summary><h3 className="rotulo">Variantes para comentar</h3><ul>{ficha.variantes.map(t => <li key={t}>{t}</li>)}</ul><h3 className="rotulo">Otras opciones para revisar</h3><ul>{ficha.alternativas.map(t => <li key={t}>{t}</li>)}</ul><p className="apoyo">Son referencias generales. Tu rutina mantiene sus ejercicios, series y cargas. Una sustitución requiere comprobar equipo, nivel, lesiones y volumen con quien te guía.</p></details>
    <p className="nota-al-pie">La ilustración simplifica un movimiento en 2D y no observa ni corrige tu postura. Si aparece dolor, detén el ejercicio y consulta a una persona capacitada.</p>
    <details className="guia-detalles"><summary>Fuente y revisión de la ficha</summary><p>Redacción propia basada en <a href={ficha.fuente.url} target="_blank" rel="noopener noreferrer">{ficha.fuente.nombre} ↗</a>. Consulta: {ficha.preparadaEl}.</p><p>Versión {ficha.version} · {ficha.autoria}.</p><p>{ficha.licencia}</p><p>Validación técnica: {animacionPublicable(ficha) ? `${ficha.validacion.responsable}, ${ficha.validacion.fecha}` : 'pendiente; aún no hay una revisión técnica registrada.'}</p></details>
  </article>
}
