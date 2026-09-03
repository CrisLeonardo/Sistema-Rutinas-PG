/**
 * Pantalla del historial biométrico (historia HU-05).
 *
 * Muestra la evolución de las medidas de la cuenta en sesión, de la medición más
 * reciente a la más antigua. El servidor filtra por el titular de la sesión, de
 * modo que no existe forma de consultar medidas ajenas (regla del negocio *f*).
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import {
  NIVELES_ACTIVIDAD,
  NIVELES_EXPERIENCIA,
  OBJETIVOS,
  SEXOS,
  etiquetaDe,
} from '../datos/catalogos.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioPerfil } from '../servicios/api.js'

function fechaLegible(valor) {
  if (!valor) return '—'
  return new Date(valor).toLocaleString('es-GT', { dateStyle: 'long', timeStyle: 'short' })
}

/** Diferencia de peso frente a la medición anterior, para leer la evolución de un vistazo. */
function describirCambio(actual, anterior) {
  if (anterior === undefined) return { texto: 'Primera medición', clase: 'text-secondary' }
  const diferencia = Math.round((actual - anterior) * 100) / 100
  if (diferencia === 0) return { texto: 'Sin cambio', clase: 'text-secondary' }
  const signo = diferencia > 0 ? '+' : '−'
  return {
    texto: `${signo}${Math.abs(diferencia).toFixed(2)} kg`,
    clase: diferencia > 0 ? 'text-danger' : 'text-success',
  }
}

export default function HistorialMedidas() {
  const { token } = useSesion()

  const [historial, setHistorial] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      setHistorial(await servicioPerfil.consultarHistorial(token))
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

  const vigente = historial[0] ?? null

  return (
    <div className="row g-4">
      <div className="col-12 d-flex flex-column flex-sm-row justify-content-between gap-3">
        <div>
          <h1 className="h3 mb-1">Mi historial de medidas</h1>
          <p className="texto-ayuda mb-0">
            Cada vez que actualiza sus datos se agrega una medición nueva; las
            anteriores no se borran.
          </p>
        </div>
        <Link to="/perfil-biometrico" className="btn btn-principal control-tactil align-self-start">
          Actualizar mis medidas
        </Link>
      </div>

      {error && (
        <div className="col-12">
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        </div>
      )}

      {cargando && (
        <div className="col-12">
          <p className="texto-ayuda">Cargando su historial…</p>
        </div>
      )}

      {!cargando && historial.length === 0 && !error && (
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body text-center p-4">
              <h2 className="h5">Todavía no ha registrado sus medidas</h2>
              <p className="texto-ayuda">
                Complete su perfil biométrico para que el sistema pueda calcular su plan.
              </p>
              <Link to="/perfil-biometrico" className="btn btn-principal control-tactil">
                Registrar mis medidas
              </Link>
            </div>
          </div>
        </div>
      )}

      {vigente && (
        <div className="col-12 col-lg-5">
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <h2 className="h5 card-title">Medición vigente</h2>
              <p className="texto-ayuda">Es la que el sistema usa para generar sus planes.</p>
              <dl className="row mb-0">
                <dt className="col-6">Peso</dt>
                <dd className="col-6">{vigente.peso_kg} kg</dd>

                <dt className="col-6">Estatura</dt>
                <dd className="col-6">{vigente.estatura_cm} cm</dd>

                <dt className="col-6">Edad</dt>
                <dd className="col-6">{vigente.edad} años</dd>

                <dt className="col-6">Sexo</dt>
                <dd className="col-6">{etiquetaDe(SEXOS, vigente.sexo)}</dd>

                <dt className="col-6">Actividad</dt>
                <dd className="col-6">{etiquetaDe(NIVELES_ACTIVIDAD, vigente.nivel_actividad)}</dd>

                <dt className="col-6">Objetivo</dt>
                <dd className="col-6">{etiquetaDe(OBJETIVOS, vigente.objetivo)}</dd>

                <dt className="col-6">Experiencia</dt>
                <dd className="col-6">
                  {etiquetaDe(NIVELES_EXPERIENCIA, vigente.nivel_experiencia)}
                </dd>

                <dt className="col-6">Días por semana</dt>
                <dd className="col-6">{vigente.dias_entrenamiento_semana}</dd>

                <dt className="col-6">Índice de masa corporal</dt>
                <dd className="col-6 mb-0">
                  {vigente.indice_masa_corporal}
                  <span className="d-block texto-ayuda">
                    {vigente.clasificacion_masa_corporal}
                  </span>
                </dd>
              </dl>
              <p className="texto-ayuda mt-3 mb-0">
                El índice de masa corporal es una referencia general. Ante cualquier
                condición de salud, consulte a un profesional.
              </p>
            </div>
          </div>
        </div>
      )}

      {historial.length > 0 && (
        <div className="col-12 col-lg-7">
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <h2 className="h5 card-title">Evolución de mis medidas</h2>
              <p className="texto-ayuda">
                {historial.length}{' '}
                {historial.length === 1 ? 'medición registrada' : 'mediciones registradas'}.
              </p>
              <div className="contenedor-tabla">
                <table className="table table-sm align-middle tabla-cuentas mb-0">
                  <caption className="texto-ayuda">
                    Mediciones de la más reciente a la más antigua.
                  </caption>
                  <thead>
                    <tr>
                      <th scope="col">Fecha</th>
                      <th scope="col">Peso</th>
                      <th scope="col">Cambio</th>
                      <th scope="col">Índice</th>
                      <th scope="col">Objetivo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historial.map((medicion, posicion) => {
                      // El historial llega de la más reciente a la más antigua, de modo
                      // que la medición previa en el tiempo es la siguiente de la lista.
                      const previa = historial[posicion + 1]
                      const cambio = describirCambio(medicion.peso_kg, previa?.peso_kg)
                      return (
                        <tr key={medicion.id}>
                          <td>
                            {fechaLegible(medicion.fecha_registro)}
                            {posicion === 0 && (
                              <span className="badge bg-success ms-2">Vigente</span>
                            )}
                          </td>
                          <td>{medicion.peso_kg} kg</td>
                          <td className={cambio.clase}>{cambio.texto}</td>
                          <td>
                            {medicion.indice_masa_corporal}
                            <span className="d-block texto-ayuda">
                              {medicion.clasificacion_masa_corporal}
                            </span>
                          </td>
                          <td>{etiquetaDe(OBJETIVOS, medicion.objetivo)}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
