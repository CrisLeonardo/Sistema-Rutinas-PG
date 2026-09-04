/**
 * Panel principal del usuario autenticado.
 *
 * Responde a la única pregunta con que alguien abre la aplicación: qué me toca
 * hoy. Antes esta pantalla listaba los módulos del sistema con el número de su
 * iteración y el código de sus historias de usuario —«Historias HU-09 y HU-10 ·
 * Iteración 5»—, que es información del proyecto y no del usuario: quien entrena
 * en el gimnasio no sabe qué es una historia de usuario ni tiene por qué saberlo.
 *
 * El orden de las tarjetas sigue el del día: primero lo que falta por hacer,
 * después lo que toca comer y entrenar, y al final el resumen de la cuenta.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { OBJETIVOS, etiquetaDe } from '../datos/catalogos.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import {
  ErrorApi,
  servicioEntrenamiento,
  servicioPlan,
  servicioProgreso,
  servicioRutina,
} from '../servicios/api.js'

/** Día de la semana con lunes como 1, que es como el sistema numera las sesiones. */
function diaDeLaSemana() {
  const dia = new Date().getDay()
  return dia === 0 ? 7 : dia
}

function saludo() {
  const hora = new Date().getHours()
  if (hora < 12) return 'Buenos días'
  if (hora < 19) return 'Buenas tardes'
  return 'Buenas noches'
}

function fechaLegible(valor) {
  if (!valor) return 'Sin registro'
  return new Date(valor).toLocaleDateString('es-GT', { dateStyle: 'long' })
}

function entero(valor) {
  return Math.round(valor).toLocaleString('es-GT')
}

/** Recupera un recurso tratando el 404 como «todavía no existe», que no es un error. */
async function opcional(promesa) {
  try {
    return await promesa
  } catch (fallo) {
    if (fallo instanceof ErrorApi && (fallo.codigo === 404 || fallo.codigo === 409)) {
      return null
    }
    throw fallo
  }
}

export default function Panel() {
  const { usuario, token } = useSesion()

  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      // Las cuatro consultas salen a la vez: en serie, sobre una conexión móvil,
      // el panel tardaría el cuádruple en dibujarse.
      const [plan, rutina, menu, reporte, entrenamiento] = await Promise.all([
        opcional(servicioPlan.consultarVigente(token)),
        opcional(servicioRutina.consultarVigente(token)),
        opcional(servicioPlan.consultarMenu(token)),
        opcional(servicioProgreso.consultarReporte(token)),
        opcional(servicioEntrenamiento.consultarResumen(token)),
      ])
      setDatos({ plan, rutina, menu, reporte, entrenamiento })
      setError(null)
    } catch (fallo) {
      setError(fallo.message)
    } finally {
      setCargando(false)
    }
  }, [token])

  useEffect(() => {
    cargar()
  }, [cargar])

  if (cargando) {
    return (
      <div className="row g-4" aria-busy="true">
        <div className="col-12">
          <div className="marcador-carga marcador-titulo" />
        </div>
        {[1, 2, 3].map((indice) => (
          <div className="col-12 col-lg-4" key={indice}>
            <div className="marcador-carga marcador-tarjeta" />
          </div>
        ))}
        <span className="visually-hidden">Cargando su panel…</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
        <div className="mt-2">
          <button type="button" className="btn btn-sm btn-principal" onClick={cargar}>
            Reintentar
          </button>
        </div>
      </div>
    )
  }

  const { plan, rutina, menu, reporte, entrenamiento } = datos
  const hoy = diaDeLaSemana()
  const sesionDeHoy = rutina?.sesiones?.find((sesion) => sesion.dia === hoy) ?? null
  const primerNombre = usuario?.nombre?.split(' ')[0] ?? ''

  return (
    <div className="row g-4">
      <div className="col-12">
        <h1 className="h3 mb-1">
          {saludo()}, {primerNombre}
        </h1>
        <p className="texto-ayuda mb-0">
          {new Date().toLocaleDateString('es-GT', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
          })}
        </p>
      </div>

      {!plan && <SinPlan />}

      {plan?.advertencias_de_salud?.length > 0 && (
        <div className="col-12">
          <div className="alert alert-warning mb-0" role="alert">
            <strong>Antes de continuar.</strong>
            <ul className="mb-0 mt-2 ps-3">
              {plan.advertencias_de_salud.map((aviso) => (
                <li key={aviso}>{aviso}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {plan && (
        <>
          <div className="col-12 col-lg-4">
            <TarjetaHoyComer plan={plan} menu={menu} />
          </div>
          <div className="col-12 col-lg-4">
            <TarjetaHoyEntrenar
              sesion={sesionDeHoy}
              rutina={rutina}
              entrenamiento={entrenamiento}
            />
          </div>
          <div className="col-12 col-lg-4">
            <TarjetaAvance reporte={reporte} />
          </div>
        </>
      )}

      <div className="col-12">
        <div className="card shadow-sm">
          <div className="card-body">
            <h2 className="h6 texto-ayuda text-uppercase mb-3">Su cuenta</h2>
            <div className="d-flex flex-wrap gap-3 justify-content-between align-items-center">
              <div>
                <div className="fw-semibold">{usuario?.nombre}</div>
                <div className="texto-ayuda text-break">{usuario?.correo}</div>
                <div className="texto-ayuda">
                  Miembro desde {fechaLegible(usuario?.fecha_registro)}
                </div>
              </div>
              <Link to="/cuenta" className="btn btn-outline-secondary control-tactil">
                Ajustes de la cuenta
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

/** Estado inicial: sin plan no hay nada que mostrar, solo un camino que seguir. */
function SinPlan() {
  return (
    <div className="col-12">
      <div className="card shadow-sm borde-destacado">
        <div className="card-body p-4">
          <h2 className="h5 card-title">Empecemos por sus medidas</h2>
          <p className="texto-ayuda">
            Con su peso, su estatura y su objetivo, el sistema calcula cuánta energía
            necesita al día y arma su rutina. Toma menos de dos minutos y puede
            cambiarlo cuando quiera.
          </p>
          <div className="d-flex flex-column flex-sm-row gap-2">
            <Link to="/perfil-biometrico" className="btn btn-principal control-tactil">
              Registrar mis medidas
            </Link>
            <Link
              to="/plan-nutricional"
              className="btn btn-outline-secondary control-tactil"
            >
              Ya las registré: generar mi plan
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

function TarjetaHoyComer({ plan, menu }) {
  return (
    <div className="card shadow-sm h-100">
      <div className="card-body d-flex flex-column">
        <h2 className="h6 texto-ayuda text-uppercase">Hoy debe comer</h2>
        <p className="cifra-panel mb-0">{entero(plan.calorias_objetivo)}</p>
        <p className="texto-ayuda mb-3">kilocalorías</p>

        <div className="d-flex gap-3 flex-wrap mb-3">
          {plan.macronutrientes.map((macro) => (
            <div key={macro.nombre}>
              <div className="fw-semibold">{macro.gramos} g</div>
              <div className="texto-ayuda">{macro.nombre}</div>
            </div>
          ))}
        </div>

        {menu && (
          <p className="texto-ayuda mb-3">
            Su menú de hoy cuesta cerca de{' '}
            <strong>Q{menu.costo_diario_quetzales.toFixed(2)}</strong>, unos{' '}
            Q{entero(menu.costo_mensual_quetzales)} al mes.
          </p>
        )}

        <div className="mt-auto d-grid gap-2">
          <Link to="/menu" className="btn btn-principal control-tactil">
            Ver qué comer hoy
          </Link>
          <Link to="/compras" className="btn btn-outline-secondary control-tactil">
            Lista de compras
          </Link>
        </div>
      </div>
    </div>
  )
}

function TarjetaHoyEntrenar({ sesion, rutina, entrenamiento }) {
  const racha = entrenamiento?.racha_semanas ?? 0
  const estaSemana = entrenamiento?.sesiones_esta_semana ?? 0

  return (
    <div className="card shadow-sm h-100">
      <div className="card-body d-flex flex-column">
        <h2 className="h6 texto-ayuda text-uppercase">Hoy le toca entrenar</h2>

        {sesion ? (
          <>
            <p className="cifra-panel mb-0">{sesion.nombre_grupo}</p>
            <p className="texto-ayuda mb-3">
              {sesion.ejercicios.length} ejercicios · {sesion.series_totales} series ·
              unos {sesion.duracion_estimada_minutos} minutos
            </p>
            <ul className="list-unstyled texto-ayuda mb-3">
              {sesion.ejercicios.slice(0, 3).map((ejercicio) => (
                <li key={ejercicio.ejercicio_id}>
                  {ejercicio.nombre} — {ejercicio.series}×{ejercicio.repeticiones_min}–
                  {ejercicio.repeticiones_max}
                </li>
              ))}
              {sesion.ejercicios.length > 3 && (
                <li>y {sesion.ejercicios.length - 3} más…</li>
              )}
            </ul>
          </>
        ) : (
          <>
            <p className="cifra-panel mb-0">Descanso</p>
            <p className="texto-ayuda mb-3">
              {rutina
                ? 'Hoy no le toca sesión. El descanso es parte del programa: es cuando el músculo se repara.'
                : 'Todavía no tiene rutina armada.'}
            </p>
          </>
        )}

        {entrenamiento?.sesiones_totales > 0 && (
          <p className="texto-ayuda mb-3">
            Lleva <strong>{racha}</strong> {racha === 1 ? 'semana' : 'semanas'} seguidas
            entrenando · {estaSemana} {estaSemana === 1 ? 'sesión' : 'sesiones'} esta
            semana.
          </p>
        )}

        <div className="mt-auto d-grid gap-2">
          {sesion ? (
            <>
              <Link to={`/entrenar/${sesion.id}`} className="btn btn-principal control-tactil">
                Entrenar ahora
              </Link>
              <Link to="/rutina" className="btn btn-outline-secondary control-tactil">
                Ver la semana completa
              </Link>
            </>
          ) : (
            <Link to="/rutina" className="btn btn-outline-secondary control-tactil">
              Ver mi rutina de la semana
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}

function TarjetaAvance({ reporte }) {
  const tieneRegistros = reporte?.puntos?.length > 0
  const cambio = reporte?.cambio_total_kg

  return (
    <div className="card shadow-sm h-100">
      <div className="card-body d-flex flex-column">
        <h2 className="h6 texto-ayuda text-uppercase">Su avance</h2>

        {tieneRegistros ? (
          <>
            <p className="cifra-panel mb-0">
              {cambio === null || cambio === undefined
                ? `${reporte.peso_actual} kg`
                : `${cambio > 0 ? '+' : ''}${cambio} kg`}
            </p>
            <p className="texto-ayuda mb-3">
              {cambio === null || cambio === undefined
                ? 'peso registrado'
                : 'desde su primer registro'}
            </p>
            <dl className="row texto-ayuda mb-3">
              <dt className="col-8 fw-normal">Semanas registradas</dt>
              <dd className="col-4 text-end">{reporte.semanas_registradas}</dd>
              <dt className="col-8 fw-normal">Sesiones cumplidas</dt>
              <dd className="col-4 text-end">{reporte.sesiones_totales}</dd>
              {reporte.adherencia_promedio !== null && (
                <>
                  <dt className="col-8 fw-normal mb-0">Cumplimiento del plan</dt>
                  <dd className="col-4 text-end mb-0">{reporte.adherencia_promedio} %</dd>
                </>
              )}
            </dl>
          </>
        ) : (
          <>
            <p className="cifra-panel mb-0">—</p>
            <p className="texto-ayuda mb-3">
              Registre su peso cada semana. Con eso el sistema sabe si su plan está
              funcionando y lo reajusta cuando hace falta.
            </p>
          </>
        )}

        <div className="mt-auto d-grid gap-2">
          <Link to="/progreso" className="btn btn-principal control-tactil">
            Registrar mi avance
          </Link>
          {tieneRegistros && (
            <Link to="/reportes" className="btn btn-outline-secondary control-tactil">
              Ver mi evolución
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}
