/**
 * Pantalla de consulta del plan nutricional (historia HU-06).
 *
 * Cada cifra técnica va acompañada de una explicación en lenguaje sencillo, tal
 * como exige el requerimiento no funcional 4.5.3, y todo plan muestra el aviso
 * de consulta profesional de la regla del negocio *e*.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPlan } from '../servicios/api.js'

const COLORES_MACRONUTRIENTE = {
  Proteína: 'var(--color-principal)',
  Carbohidrato: 'var(--color-acento)',
  Grasa: '#0369a1',
}

function fechaLegible(valor) {
  if (!valor) return '—'
  return new Date(valor).toLocaleString('es-GT', { dateStyle: 'long', timeStyle: 'short' })
}

function entero(valor) {
  return Math.round(valor).toLocaleString('es-GT')
}

export default function PlanNutricional() {
  const { token } = useSesion()

  const [plan, setPlan] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [generando, setGenerando] = useState(false)
  const [error, setError] = useState(null)
  const [sinPerfil, setSinPerfil] = useState(false)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      setPlan(await servicioPlan.consultarVigente(token))
      setError(null)
    } catch (fallo) {
      // Que todavía no exista un plan no es un error: es el estado inicial.
      if (fallo instanceof ErrorApi && fallo.codigo === 404) {
        setPlan(null)
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

  const generar = async () => {
    setGenerando(true)
    setError(null)
    setSinPerfil(false)
    try {
      setPlan(await servicioPlan.generar(token))
    } catch (fallo) {
      // El servidor responde 409 cuando el perfil biométrico está incompleto
      // (apartado 4.8.3): en ese caso se ofrece el camino para completarlo.
      if (fallo instanceof ErrorApi && fallo.codigo === 409) setSinPerfil(true)
      setError(fallo.message)
    } finally {
      setGenerando(false)
    }
  }

  if (cargando) {
    return <p className="texto-ayuda">Cargando su plan…</p>
  }

  return (
    <div className="row g-4">
      <div className="col-12 d-flex flex-column flex-sm-row justify-content-between gap-3">
        <div>
          <h1 className="h3 mb-1">Mi plan de alimentación</h1>
          <p className="texto-ayuda mb-0">
            Calculado a partir de sus medidas con un modelo de red neuronal, y
            comparado con dos fórmulas médicas de referencia.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-principal control-tactil align-self-start"
          onClick={generar}
          disabled={generando}
        >
          {generando ? 'Calculando…' : plan ? 'Volver a calcular' : 'Generar mi plan'}
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

      {!plan && !error && (
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body text-center p-4">
              <h2 className="h5">Todavía no ha generado su plan</h2>
              <p className="texto-ayuda mb-0">
                Con sus medidas ya registradas, el cálculo toma unos segundos.
              </p>
            </div>
          </div>
        </div>
      )}

      {plan && (
        <>
          <div className="col-12 col-lg-5">
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <h2 className="h5 card-title">Su energía diaria</h2>
                <p className="cifra-principal mb-0">{entero(plan.calorias_objetivo)}</p>
                <p className="texto-ayuda">kilocalorías al día</p>
                <p className="texto-ayuda">{plan.explicacion_objetivo}</p>

                <dl className="row mb-0 border-top pt-3">
                  <dt className="col-7">Gasto de energía en reposo</dt>
                  <dd className="col-5 text-end">{entero(plan.tasa_metabolica_basal)} kcal</dd>

                  <dt className="col-7">Gasto total con su actividad</dt>
                  <dd className="col-5 text-end">{entero(plan.gasto_energetico_total)} kcal</dd>

                  <dt className="col-7">Agua sugerida</dt>
                  <dd className="col-5 text-end mb-0">
                    {(plan.agua_ml / 1000).toFixed(1)} litros
                  </dd>
                </dl>
                <p className="texto-ayuda mt-3 mb-0">
                  El gasto en reposo es la energía que su cuerpo consume sin hacer nada;
                  el gasto total le suma su actividad diaria.
                </p>
              </div>
            </div>
          </div>

          <div className="col-12 col-lg-7">
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <h2 className="h5 card-title">Cómo repartir esa energía</h2>
                <p className="texto-ayuda">
                  Son las cantidades diarias de cada tipo de alimento, en gramos.
                </p>

                <div className="barra-macronutrientes" role="img" aria-label="Reparto de macronutrientes">
                  {plan.macronutrientes.map((macro) => (
                    <div
                      key={macro.nombre}
                      className="segmento-macronutriente"
                      style={{
                        width: `${macro.porcentaje}%`,
                        backgroundColor: COLORES_MACRONUTRIENTE[macro.nombre],
                      }}
                      title={`${macro.nombre}: ${macro.porcentaje} %`}
                    />
                  ))}
                </div>

                <ul className="list-group list-group-flush">
                  {plan.macronutrientes.map((macro) => (
                    <li key={macro.nombre} className="list-group-item px-0">
                      <div className="d-flex justify-content-between align-items-start gap-3">
                        <div className="fw-semibold">
                          <span
                            className="punto-color"
                            style={{ backgroundColor: COLORES_MACRONUTRIENTE[macro.nombre] }}
                          />
                          {macro.nombre}
                        </div>
                        <div className="text-end flex-shrink-0">
                          <div className="fw-semibold">{macro.gramos} g</div>
                          <div className="texto-ayuda">
                            {macro.porcentaje} % · {entero(macro.kilocalorias)} kcal
                          </div>
                        </div>
                      </div>
                      <div className="texto-ayuda">{macro.explicacion}</div>
                    </li>
                  ))}
                </ul>

                <p className="texto-ayuda mt-3 mb-0">
                  Los tres suman {entero(plan.energia_de_los_macronutrientes)} kcal, que es
                  exactamente su energía diaria.
                </p>
              </div>
            </div>
          </div>

          <div className="col-12">
            <div className="card shadow-sm">
              <div className="card-body">
                <h2 className="h5 card-title">Cómo se comprobó este cálculo</h2>
                <p className="texto-ayuda">
                  El plan lo calculó{' '}
                  {plan.origen_calculo === 'red_neuronal'
                    ? 'el modelo de red neuronal del sistema'
                    : 'la fórmula de referencia del sistema'}
                  , y se comparó con dos fórmulas usadas en nutrición clínica.
                </p>
                <div className="contenedor-tabla">
                  <table className="table table-sm align-middle mb-0">
                    <tbody>
                      <tr>
                        <th scope="row" className="fw-normal">
                          Fórmula de Mifflin-St Jeor
                        </th>
                        <td className="text-end">{entero(plan.referencia_mifflin)} kcal</td>
                      </tr>
                      <tr>
                        <th scope="row" className="fw-normal">
                          Fórmula de Harris-Benedict
                        </th>
                        <td className="text-end">
                          {entero(plan.referencia_harris_benedict)} kcal
                        </td>
                      </tr>
                      <tr>
                        <th scope="row">Diferencia con su plan</th>
                        <td className="text-end fw-semibold">
                          {plan.margen_error_porcentaje.toFixed(2)} %
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="mt-3 mb-0">
                  <span
                    className={`badge ${
                      plan.dentro_del_margen_admitido ? 'bg-success' : 'bg-danger'
                    }`}
                  >
                    {plan.dentro_del_margen_admitido
                      ? 'Dentro del margen admitido del 5 %'
                      : 'Fuera del margen admitido del 5 %'}
                  </span>
                </p>
              </div>
            </div>
          </div>

          <div className="col-12">
            <div className="alert alert-secondary mb-0" role="note">
              <strong>Importante.</strong> {plan.aviso_profesional}
            </div>
          </div>

          <div className="col-12">
            <p className="texto-ayuda mb-0">
              Plan generado el {fechaLegible(plan.fecha_generacion)} · Si actualiza sus
              medidas, vuelva a calcularlo para que se ajuste a su peso actual.
            </p>
          </div>
        </>
      )}
    </div>
  )
}
