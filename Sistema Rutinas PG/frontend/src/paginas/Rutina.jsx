/**
 * Pantalla de consulta de la rutina semanal (historia HU-07).
 *
 * Muestra, para cada sesión, el ejercicio, las series, las repeticiones y las
 * repeticiones en reserva. La sigla técnica no aparece sola: cada cifra lleva su
 * explicación, conforme al requerimiento no funcional 4.5.3.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPlan, servicioRutina } from '../servicios/api.js'

const ETIQUETAS_NIVEL = {
  principiante: 'Principiante',
  intermedio: 'Intermedio',
  avanzado: 'Avanzado',
}

export default function Rutina() {
  const { token } = useSesion()

  const [rutina, setRutina] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [generando, setGenerando] = useState(false)
  const [error, setError] = useState(null)
  const [sinPerfil, setSinPerfil] = useState(false)
  const [sesionAbierta, setSesionAbierta] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      const obtenida = await servicioRutina.consultarVigente(token)
      setRutina(obtenida)
      setSesionAbierta(obtenida.sesiones[0]?.id ?? null)
      setError(null)
    } catch (fallo) {
      // No tener rutina todavía es el estado inicial, no un error.
      if (fallo instanceof ErrorApi && fallo.codigo === 404) {
        setRutina(null)
      } else {
        setError(fallo.message)
      }
    } finally {
      setCargando(false)
    }
  }, [token])

  useEffect(() => {
    cargar()
  }, [cargar])

  // La rutina se produce junto con el plan: generar uno produce la otra.
  const generar = async () => {
    setGenerando(true)
    setError(null)
    setSinPerfil(false)
    try {
      await servicioPlan.generar(token)
      await cargar()
    } catch (fallo) {
      if (fallo instanceof ErrorApi && fallo.codigo === 409) setSinPerfil(true)
      setError(fallo.message)
    } finally {
      setGenerando(false)
    }
  }

  if (cargando) {
    return <p className="texto-ayuda">Cargando su rutina…</p>
  }

  return (
    <div className="row g-4">
      <div className="col-12 d-flex flex-column flex-sm-row justify-content-between gap-3">
        <div>
          <h1 className="h3 mb-1">Mi rutina de la semana</h1>
          <p className="texto-ayuda mb-0">
            Armada con los ejercicios disponibles en el gimnasio y repartida para que
            cada músculo alcance a recuperarse entre sesiones.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-principal control-tactil align-self-start"
          onClick={generar}
          disabled={generando}
        >
          {generando ? 'Armando…' : rutina ? 'Volver a armar' : 'Generar mi rutina'}
        </button>
      </div>

      {error && (
        <div className="col-12">
          <div className="alert alert-warning" role="alert">
            {error}
            {sinPerfil && (
              <div className="mt-2">
                <Link to="/perfil-biometrico" className="btn btn-sm btn-principal control-tactil">
                  Registrar mis medidas
                </Link>
              </div>
            )}
          </div>
        </div>
      )}

      {!rutina && !error && (
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body text-center p-4">
              <h2 className="h5">Todavía no tiene rutina</h2>
              <p className="texto-ayuda mb-0">
                Su rutina se arma junto con su plan de alimentación.
              </p>
            </div>
          </div>
        </div>
      )}

      {rutina && (
        <>
          <div className="col-12">
            <div className="card shadow-sm">
              <div className="card-body">
                <div className="row g-3 text-center text-sm-start">
                  <div className="col-6 col-sm-3">
                    <div className="texto-ayuda">Sesiones por semana</div>
                    <div className="h4 mb-0">{rutina.dias_entrenamiento_semana}</div>
                  </div>
                  <div className="col-6 col-sm-3">
                    <div className="texto-ayuda">Series en la semana</div>
                    <div className="h4 mb-0">{rutina.series_totales}</div>
                  </div>
                  <div className="col-6 col-sm-3">
                    <div className="texto-ayuda">Series por músculo</div>
                    <div className="h4 mb-0">{Math.round(rutina.series_objetivo_por_grupo)}</div>
                  </div>
                  <div className="col-6 col-sm-3">
                    <div className="texto-ayuda">Su nivel</div>
                    <div className="h4 mb-0">
                      {ETIQUETAS_NIVEL[rutina.nivel_experiencia] ?? rutina.nivel_experiencia}
                    </div>
                  </div>
                </div>
                {rutina.cumple_separacion_de_grupos && (
                  <p className="mt-3 mb-0">
                    <span className="badge bg-success">
                      Ningún músculo se entrena dos días seguidos
                    </span>
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="col-12">
            <div className="accordion" id="acordeon-rutina">
              {rutina.sesiones.map((sesion) => {
                const abierta = sesionAbierta === sesion.id
                return (
                  <div className="accordion-item" key={sesion.id}>
                    <h2 className="accordion-header">
                      <button
                        className={`accordion-button control-tactil ${abierta ? '' : 'collapsed'}`}
                        type="button"
                        aria-expanded={abierta}
                        onClick={() => setSesionAbierta(abierta ? null : sesion.id)}
                      >
                        <span className="d-flex flex-column flex-sm-row gap-1 gap-sm-3 w-100 pe-3">
                          <span className="fw-semibold">{sesion.nombre_dia}</span>
                          <span className="texto-ayuda">
                            {sesion.nombre_grupo} · {sesion.ejercicios.length} ejercicios ·{' '}
                            {sesion.duracion_estimada_minutos} min
                          </span>
                        </span>
                      </button>
                    </h2>
                    <div className={`accordion-collapse collapse ${abierta ? 'show' : ''}`}>
                      <div className="accordion-body p-0">
                        <ul className="list-group list-group-flush">
                          {sesion.ejercicios.map((ejercicio) => (
                            <li key={ejercicio.ejercicio_id} className="list-group-item">
                              <div className="d-flex justify-content-between align-items-start gap-3">
                                <div>
                                  <div className="fw-semibold">
                                    {ejercicio.orden}. {ejercicio.nombre}
                                  </div>
                                  <div className="texto-ayuda">{ejercicio.equipamiento}</div>
                                </div>
                                <div className="text-end flex-shrink-0">
                                  <div className="fw-semibold">{ejercicio.series} series</div>
                                  <div className="texto-ayuda">
                                    {ejercicio.repeticiones_min}–{ejercicio.repeticiones_max} reps
                                  </div>
                                </div>
                              </div>
                              {ejercicio.descripcion && (
                                <div className="texto-ayuda mt-2">{ejercicio.descripcion}</div>
                              )}
                              <div className="texto-ayuda mt-1">
                                {ejercicio.explicacion_reserva} Descanse{' '}
                                {Math.round(ejercicio.descanso_segundos / 60 * 10) / 10} minutos
                                entre series.
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          <div className="col-12 col-lg-6">
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <h2 className="h5 card-title">Series por músculo en la semana</h2>
                <p className="texto-ayuda">
                  Es el trabajo que recibe cada grupo muscular sumando todas las sesiones.
                </p>
                <ul className="list-group list-group-flush">
                  {Object.entries(rutina.series_efectivas_por_grupo).map(([grupo, series]) => (
                    <li
                      key={grupo}
                      className="list-group-item d-flex justify-content-between px-0"
                    >
                      <span>{grupo}</span>
                      <span className="fw-semibold">{series} series</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="col-12 col-lg-6">
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <h2 className="h5 card-title">Cómo progresar</h2>
                <p className="mb-0">{rutina.explicacion_progresion}</p>
              </div>
            </div>
          </div>

          <div className="col-12">
            <div className="alert alert-secondary mb-0" role="note">
              <strong>Importante.</strong> {rutina.aviso_tecnica}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
