/**
 * Bitácora e historial de entrenamiento.
 *
 * Reúne lo que el registro de cargas hace posible y que antes no existía: la
 * constancia semanal, la evolución de la carga en cada ejercicio y las marcas
 * personales. Es la pantalla que devuelve algo a cambio del esfuerzo de
 * registrar, y sin ella la bitácora sería un formulario que no sirve para nada.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import GraficaLineas from '../componentes/GraficaLineas.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioEntrenamiento } from '../servicios/api.js'

function fechaCorta(valor) {
  if (!valor) return '—'
  return new Date(`${valor}T12:00:00`).toLocaleDateString('es-GT', {
    day: 'numeric',
    month: 'long',
  })
}

export default function HistorialEntrenamiento() {
  const { token } = useSesion()

  const [resumen, setResumen] = useState(null)
  const [sesiones, setSesiones] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [ejercicioAbierto, setEjercicioAbierto] = useState(null)
  const [evolucion, setEvolucion] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      const [datosResumen, datosSesiones] = await Promise.all([
        servicioEntrenamiento.consultarResumen(token),
        servicioEntrenamiento.consultarBitacora(token),
      ])
      setResumen(datosResumen)
      setSesiones(datosSesiones)
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

  const abrirEjercicio = async (ejercicioId) => {
    if (ejercicioAbierto === ejercicioId) {
      setEjercicioAbierto(null)
      setEvolucion(null)
      return
    }
    setEjercicioAbierto(ejercicioId)
    setEvolucion(null)
    try {
      setEvolucion(await servicioEntrenamiento.consultarEjercicio(ejercicioId, token))
    } catch (fallo) {
      setError(fallo.message)
    }
  }

  if (cargando) {
    return <p className="texto-ayuda">Cargando su bitácora…</p>
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    )
  }

  if (!resumen?.sesiones_totales) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center p-4">
          <h1 className="h5">Todavía no ha registrado ningún entrenamiento</h1>
          <p className="texto-ayuda">
            Cuando registre una sesión, el sistema empezará a llevarle la cuenta de sus
            cargas y le dirá cuándo subir de peso en cada ejercicio.
          </p>
          <Link to="/rutina" className="btn btn-principal control-tactil">
            Ir a mi rutina
          </Link>
        </div>
      </div>
    )
  }

  const cambio = resumen.cambio_volumen_porcentaje

  return (
    <div className="row g-4">
      <div className="col-12">
        <h1 className="h3 mb-1">Mi bitácora</h1>
        <p className="texto-ayuda mb-0">
          Lo que ha levantado, sesión por sesión, y cómo ha ido subiendo.
        </p>
      </div>

      <div className="col-12">
        <div className="card shadow-sm">
          <div className="card-body">
            <div className="row g-3 text-center text-sm-start">
              <div className="col-6 col-sm-3">
                <div className="texto-ayuda">Racha</div>
                <div className="h4 mb-0">
                  {resumen.racha_semanas}{' '}
                  <span className="texto-ayuda">
                    {resumen.racha_semanas === 1 ? 'semana' : 'semanas'}
                  </span>
                </div>
              </div>
              <div className="col-6 col-sm-3">
                <div className="texto-ayuda">Esta semana</div>
                <div className="h4 mb-0">
                  {resumen.sesiones_esta_semana}{' '}
                  <span className="texto-ayuda">
                    {resumen.sesiones_esta_semana === 1 ? 'sesión' : 'sesiones'}
                  </span>
                </div>
              </div>
              <div className="col-6 col-sm-3">
                <div className="texto-ayuda">Volumen semanal</div>
                <div className="h4 mb-0">
                  {Math.round(resumen.volumen_esta_semana_kg).toLocaleString('es-GT')} kg
                </div>
              </div>
              <div className="col-6 col-sm-3">
                <div className="texto-ayuda">Sesiones en total</div>
                <div className="h4 mb-0">{resumen.sesiones_totales}</div>
              </div>
            </div>
            {cambio !== null && cambio !== undefined && (
              <p className="texto-ayuda mt-3 mb-0">
                Su volumen de esta semana va {cambio > 0 ? 'un ' : ''}
                <strong>
                  {cambio > 0 ? '+' : ''}
                  {cambio} %
                </strong>{' '}
                respecto de la semana pasada. El volumen es la suma del peso por las
                repeticiones: sube cuando carga más o cuando hace más series.
              </p>
            )}
          </div>
        </div>
      </div>

      {resumen.marcas.length > 0 && (
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body">
              <h2 className="h5 card-title">Sus marcas</h2>
              <p className="texto-ayuda">
                El peso más alto que ha movido en cada ejercicio. Toque uno para ver cómo
                ha ido cambiando.
              </p>
              <ul className="list-group list-group-flush">
                {resumen.marcas.map((marca) => (
                  <li key={marca.ejercicio_id} className="list-group-item px-0">
                    <button
                      type="button"
                      className="boton-plano w-100 text-start control-tactil"
                      onClick={() => abrirEjercicio(marca.ejercicio_id)}
                      aria-expanded={ejercicioAbierto === marca.ejercicio_id}
                    >
                      <div className="d-flex justify-content-between align-items-start gap-3">
                        <div>
                          <div className="fw-semibold">{marca.nombre}</div>
                          <div className="texto-ayuda">
                            {fechaCorta(marca.fecha)} ·{' '}
                            {marca.repeticion_maxima_estimada_kg &&
                              `equivale a ${marca.repeticion_maxima_estimada_kg} kg a una repetición`}
                          </div>
                        </div>
                        <div className="text-end flex-shrink-0">
                          <div className="fw-semibold">{marca.carga_maxima_kg} kg</div>
                          <div className="texto-ayuda">
                            × {marca.repeticiones_en_la_maxima}
                          </div>
                        </div>
                      </div>
                    </button>

                    {ejercicioAbierto === marca.ejercicio_id && (
                      <div className="mt-3">
                        {evolucion ? (
                          <>
                            <GraficaLineas
                              puntos={evolucion.puntos.map((punto) => ({
                                fecha: `${punto.fecha}T12:00:00`,
                                valor: punto.carga_maxima_kg ?? 0,
                              }))}
                              etiquetaValor="kg"
                              decimales={1}
                              descripcion={`Evolución de la carga en ${evolucion.nombre}`}
                            />
                            <p className="texto-ayuda mb-0">
                              {evolucion.sesiones_registradas} sesiones registradas
                              {evolucion.cambio_carga_kg !== null &&
                                ` · ${evolucion.cambio_carga_kg > 0 ? '+' : ''}${evolucion.cambio_carga_kg} kg desde la primera`}
                            </p>
                          </>
                        ) : (
                          <p className="texto-ayuda mb-0">Cargando…</p>
                        )}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className="col-12">
        <div className="card shadow-sm">
          <div className="card-body">
            <h2 className="h5 card-title">Sesiones registradas</h2>
            <ul className="list-group list-group-flush">
              {sesiones.map((sesion) => (
                <li key={sesion.id} className="list-group-item px-0">
                  <div className="d-flex justify-content-between align-items-start gap-3">
                    <div>
                      <div className="fw-semibold">
                        {sesion.nombre_grupo ?? 'Entrenamiento libre'}
                      </div>
                      <div className="texto-ayuda">
                        {fechaCorta(sesion.fecha)} · {sesion.series_totales} series ·{' '}
                        {sesion.repeticiones_totales} repeticiones
                        {sesion.duracion_minutos && ` · ${sesion.duracion_minutos} min`}
                      </div>
                      {sesion.notas && <div className="texto-ayuda">«{sesion.notas}»</div>}
                    </div>
                    <div className="text-end flex-shrink-0">
                      <div className="fw-semibold">
                        {Math.round(sesion.volumen_kg).toLocaleString('es-GT')} kg
                      </div>
                      <div className="texto-ayuda">volumen</div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
