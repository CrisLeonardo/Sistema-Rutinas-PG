/**
 * Pantalla de reportes gráficos de evolución (historia HU-10).
 *
 * Presenta tres cosas: la evolución del peso en el tiempo, la adherencia y las
 * sesiones cumplidas, y la comparación entre el plan inicial y el vigente. Los
 * agregados llegan calculados del servidor, de modo que esta pantalla solo
 * dibuja.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import GraficaBarras from '../componentes/GraficaBarras.jsx'
import GraficaLineas from '../componentes/GraficaLineas.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioProgreso } from '../servicios/api.js'

const SESIONES_MAXIMAS = 7

function fechaLegible(valor) {
  if (!valor) return '—'
  return new Date(valor).toLocaleDateString('es-GT', { dateStyle: 'long' })
}

function conSigno(valor, unidad) {
  if (valor === null || valor === undefined) return '—'
  return `${valor > 0 ? '+' : ''}${valor} ${unidad}`
}

export default function Reportes() {
  const { token } = useSesion()

  const [reporte, setReporte] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      setReporte(await servicioProgreso.consultarReporte(token))
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
    return <p className="texto-ayuda">Cargando su evolución…</p>
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    )
  }

  const puntos = reporte?.puntos ?? []
  const comparacion = reporte?.comparacion_planes

  const puntosPeso = puntos.map((punto) => ({ etiqueta: punto.fecha, valor: punto.peso_kg }))
  const puntosSesiones = puntos.map((punto) => ({
    etiqueta: punto.fecha,
    valor: punto.sesiones_cumplidas,
  }))
  const puntosAdherencia = puntos
    .filter((punto) => punto.adherencia_nutricional !== null)
    .map((punto) => ({ etiqueta: punto.fecha, valor: punto.adherencia_nutricional }))
  const puntosCintura = puntos
    .filter((punto) => punto.perimetro_cintura_cm !== null)
    .map((punto) => ({ etiqueta: punto.fecha, valor: punto.perimetro_cintura_cm }))

  return (
    <div className="row g-4">
      <div className="col-12 d-flex flex-column flex-sm-row justify-content-between gap-3">
        <div>
          <h1 className="h3 mb-1">Mi evolución</h1>
          <p className="texto-ayuda mb-0">
            Lo que ha cambiado desde que empezó, semana a semana.
          </p>
        </div>
        <Link to="/progreso" className="btn btn-principal control-tactil align-self-start">
          Registrar mi avance
        </Link>
      </div>

      {puntos.length === 0 && (
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body text-center p-4">
              <h2 className="h5">Todavía no ha registrado ningún avance</h2>
              <p className="texto-ayuda mb-0">
                Sus gráficas aparecerán aquí en cuanto registre su primera semana.
              </p>
            </div>
          </div>
        </div>
      )}

      {puntos.length > 0 && (
        <>
          <div className="col-12">
            <div className="card shadow-sm">
              <div className="card-body">
                <div className="row g-3 text-center text-sm-start">
                  <div className="col-6 col-sm-3">
                    <div className="texto-ayuda">Peso inicial</div>
                    <div className="h4 mb-0">{reporte.peso_inicial} kg</div>
                  </div>
                  <div className="col-6 col-sm-3">
                    <div className="texto-ayuda">Peso actual</div>
                    <div className="h4 mb-0">{reporte.peso_actual} kg</div>
                  </div>
                  <div className="col-6 col-sm-3">
                    <div className="texto-ayuda">Cambio total</div>
                    <div
                      className={`h4 mb-0 ${
                        reporte.cambio_total_kg === null
                          ? ''
                          : reporte.cambio_total_kg < 0
                            ? 'text-success'
                            : 'text-danger'
                      }`}
                    >
                      {conSigno(reporte.cambio_total_kg, 'kg')}
                    </div>
                  </div>
                  <div className="col-6 col-sm-3">
                    <div className="texto-ayuda">Semanas registradas</div>
                    <div className="h4 mb-0">{reporte.semanas_registradas}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="col-12 col-lg-6">
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <h2 className="h5 card-title">Evolución de su peso</h2>
                <GraficaLineas
                  puntos={puntosPeso}
                  etiquetaValor="kg"
                  decimales={1}
                  descripcion="Peso corporal registrado en cada semana, en kilogramos."
                />
              </div>
            </div>
          </div>

          <div className="col-12 col-lg-6">
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <h2 className="h5 card-title">Sesiones que completó</h2>
                <GraficaBarras
                  puntos={puntosSesiones}
                  maximoFijo={SESIONES_MAXIMAS}
                  etiquetaValor="sesiones"
                  descripcion={`Total acumulado: ${reporte.sesiones_totales} sesiones de entrenamiento.`}
                />
              </div>
            </div>
          </div>

          {puntosAdherencia.length > 0 && (
            <div className="col-12 col-lg-6">
              <div className="card shadow-sm h-100">
                <div className="card-body">
                  <h2 className="h5 card-title">Qué tanto siguió su plan</h2>
                  <GraficaBarras
                    puntos={puntosAdherencia}
                    maximoFijo={100}
                    etiquetaValor="%"
                    color="var(--color-principal)"
                    descripcion={`Promedio: ${reporte.adherencia_promedio} % de cumplimiento.`}
                  />
                </div>
              </div>
            </div>
          )}

          {puntosCintura.length > 0 && (
            <div className="col-12 col-lg-6">
              <div className="card shadow-sm h-100">
                <div className="card-body">
                  <h2 className="h5 card-title">Perímetro de cintura</h2>
                  <GraficaLineas
                    puntos={puntosCintura}
                    etiquetaValor="cm"
                    decimales={0}
                    color="#0369a1"
                    descripcion="La cintura suele bajar antes que el peso de la báscula."
                  />
                </div>
              </div>
            </div>
          )}

          {comparacion && (
            <div className="col-12">
              <div className="card shadow-sm">
                <div className="card-body">
                  <h2 className="h5 card-title">Su plan inicial frente al de ahora</h2>
                  {comparacion.hubo_cambio ? (
                    <p className="texto-ayuda">
                      Su plan se recalculó conforme cambiaron sus medidas. Así quedó.
                    </p>
                  ) : (
                    <p className="texto-ayuda">
                      Su plan todavía no ha cambiado: sigue vigente el que se generó el{' '}
                      {fechaLegible(comparacion.fecha_inicial)}.
                    </p>
                  )}

                  <div className="contenedor-tabla">
                    <table className="table table-sm align-middle mb-0">
                      <thead>
                        <tr>
                          <th scope="col">Dato</th>
                          <th scope="col" className="text-end">
                            Plan inicial
                          </th>
                          <th scope="col" className="text-end">
                            Plan vigente
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <th scope="row" className="fw-normal">
                            Energía diaria
                          </th>
                          <td className="text-end">
                            {Math.round(comparacion.calorias_inicial)} kcal
                          </td>
                          <td className="text-end fw-semibold">
                            {Math.round(comparacion.calorias_vigente)} kcal
                          </td>
                        </tr>
                        <tr>
                          <th scope="row" className="fw-normal">
                            Proteína
                          </th>
                          <td className="text-end">{Math.round(comparacion.proteina_inicial)} g</td>
                          <td className="text-end fw-semibold">
                            {Math.round(comparacion.proteina_vigente)} g
                          </td>
                        </tr>
                        <tr>
                          <th scope="row" className="fw-normal">
                            Carbohidrato
                          </th>
                          <td className="text-end">
                            {Math.round(comparacion.carbohidrato_inicial)} g
                          </td>
                          <td className="text-end fw-semibold">
                            {Math.round(comparacion.carbohidrato_vigente)} g
                          </td>
                        </tr>
                        <tr>
                          <th scope="row" className="fw-normal">
                            Grasa
                          </th>
                          <td className="text-end">{Math.round(comparacion.grasa_inicial)} g</td>
                          <td className="text-end fw-semibold">
                            {Math.round(comparacion.grasa_vigente)} g
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  {comparacion.hubo_cambio && (
                    <p className="mt-3 mb-0">
                      Diferencia de energía:{' '}
                      <span className="fw-semibold">
                        {conSigno(Math.round(comparacion.diferencia_calorias), 'kcal al día')}
                      </span>
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
