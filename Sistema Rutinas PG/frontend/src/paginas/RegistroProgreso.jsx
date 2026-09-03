/**
 * Pantalla de registro del avance semanal (historia HU-09).
 *
 * El formulario es corto a propósito: se llena cada semana, de modo que pedir
 * mucho lo convertiría en una carga y el usuario dejaría de registrar. Solo el
 * peso es obligatorio.
 *
 * Tras guardar, la pantalla explica qué hizo el sistema con el plan, para que el
 * reajuste no ocurra en silencio.
 */

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPerfil, servicioProgreso } from '../servicios/api.js'

const PESO_MINIMO = 30
const PESO_MAXIMO = 250
const PERIMETRO_MINIMO = 40
const PERIMETRO_MAXIMO = 200

function hoyEnTextoLocal() {
  const ahora = new Date()
  const desplazamiento = ahora.getTimezoneOffset() * 60_000
  return new Date(ahora.getTime() - desplazamiento).toISOString().slice(0, 10)
}

export default function RegistroProgreso() {
  const { token } = useSesion()
  const navegar = useNavigate()

  const [formulario, setFormulario] = useState({
    peso_kg: '',
    perimetro_cintura_cm: '',
    sesiones_cumplidas: '0',
    adherencia_nutricional: '80',
    fecha_registro: hoyEnTextoLocal(),
  })
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [resultado, setResultado] = useState(null)
  const [sinPlan, setSinPlan] = useState(false)

  // Se precarga el peso de la última medición para que el usuario solo tenga
  // que corregirlo, en lugar de escribirlo desde cero cada semana.
  useEffect(() => {
    let vigente = true
    servicioPerfil
      .consultarVigente(token)
      .then((perfil) => {
        if (vigente) {
          setFormulario((anterior) => ({ ...anterior, peso_kg: String(perfil.peso_kg) }))
        }
      })
      .catch(() => {
        // Sin perfil previo el campo queda vacío.
      })
    return () => {
      vigente = false
    }
  }, [token])

  const actualizar = (evento) => {
    const { name, value } = evento.target
    setFormulario((anterior) => ({ ...anterior, [name]: value }))
    setError(null)
  }

  /** Reproduce en la interfaz las reglas que el servidor vuelve a verificar. */
  const validar = () => {
    const peso = Number(formulario.peso_kg)
    if (!formulario.peso_kg || peso < PESO_MINIMO || peso > PESO_MAXIMO) {
      return `El peso debe estar entre ${PESO_MINIMO} y ${PESO_MAXIMO} kilogramos.`
    }
    if (formulario.perimetro_cintura_cm) {
      const perimetro = Number(formulario.perimetro_cintura_cm)
      if (perimetro < PERIMETRO_MINIMO || perimetro > PERIMETRO_MAXIMO) {
        return `El perímetro de cintura debe estar entre ${PERIMETRO_MINIMO} y ${PERIMETRO_MAXIMO} centímetros.`
      }
    }
    if (formulario.fecha_registro > hoyEnTextoLocal()) {
      return 'La fecha del registro no puede ser posterior a la fecha de hoy.'
    }
    return null
  }

  const enviar = async (evento) => {
    evento.preventDefault()
    const problema = validar()
    if (problema) {
      setError(problema)
      return
    }

    setError(null)
    setEnviando(true)
    setSinPlan(false)
    try {
      const respuesta = await servicioProgreso.registrar(
        {
          peso_kg: Number(formulario.peso_kg),
          perimetro_cintura_cm: formulario.perimetro_cintura_cm
            ? Number(formulario.perimetro_cintura_cm)
            : null,
          sesiones_cumplidas: Number(formulario.sesiones_cumplidas),
          adherencia_nutricional: Number(formulario.adherencia_nutricional),
          fecha_registro: formulario.fecha_registro,
        },
        token,
      )
      setResultado(respuesta.reajuste)
    } catch (fallo) {
      // El servidor responde 409 cuando todavía no hay plan sobre el que ajustar.
      if (fallo instanceof ErrorApi && fallo.codigo === 409) setSinPlan(true)
      setError(fallo.message)
    } finally {
      setEnviando(false)
    }
  }

  if (resultado) {
    return (
      <div className="d-flex justify-content-center">
        <div className="card shadow-sm tarjeta-formulario">
          <div className="card-body p-4">
            <h1 className="h4 mb-3">Avance registrado</h1>

            <div
              className={`alert ${resultado.reajusto_el_plan ? 'alert-success' : 'alert-secondary'}`}
              role="status"
            >
              <div className="fw-semibold mb-1">
                {resultado.reajusto_el_plan
                  ? 'Su plan se actualizó'
                  : 'Su plan sigue igual'}
              </div>
              {resultado.motivo}
            </div>

            <p>{resultado.recomendacion}</p>

            {resultado.ritmo_semanal_kg !== null && (
              <dl className="row small border-top pt-3">
                <dt className="col-7">Cambio desde el registro anterior</dt>
                <dd className="col-5 text-end">
                  {resultado.cambio_peso_kg > 0 ? '+' : ''}
                  {resultado.cambio_peso_kg} kg
                </dd>
                <dt className="col-7">Ritmo por semana</dt>
                <dd className="col-5 text-end mb-0">
                  {resultado.ritmo_semanal_kg > 0 ? '+' : ''}
                  {resultado.ritmo_semanal_kg} kg
                </dd>
              </dl>
            )}

            <div className="d-grid gap-2 mt-4">
              <Link to="/reportes" className="btn btn-principal btn-lg control-tactil">
                Ver mi evolución
              </Link>
              {resultado.reajusto_el_plan && (
                <Link
                  to="/plan-nutricional"
                  className="btn btn-outline-secondary btn-lg control-tactil"
                >
                  Ver mi plan actualizado
                </Link>
              )}
              <button
                type="button"
                className="btn btn-link control-tactil"
                onClick={() => {
                  setResultado(null)
                  navegar('/progreso', { replace: true })
                }}
              >
                Registrar otro avance
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="d-flex justify-content-center">
      <div className="card shadow-sm tarjeta-formulario">
        <div className="card-body p-4">
          <h1 className="h4 mb-1">Registrar mi avance</h1>
          <p className="texto-ayuda mb-4">
            Anote cómo le fue esta semana. Con estos datos el sistema ajusta su plan a
            su ritmo real.
          </p>

          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
              {sinPlan && (
                <div className="mt-2">
                  <Link
                    to="/plan-nutricional"
                    className="btn btn-sm btn-principal control-tactil"
                  >
                    Generar mi plan
                  </Link>
                </div>
              )}
            </div>
          )}

          <form onSubmit={enviar} noValidate>
            <div className="mb-3">
              <label className="form-label" htmlFor="peso_kg">
                Peso de hoy, en kilogramos
              </label>
              <input
                id="peso_kg"
                name="peso_kg"
                type="number"
                inputMode="decimal"
                step="0.1"
                min={PESO_MINIMO}
                max={PESO_MAXIMO}
                className="form-control form-control-lg control-tactil"
                value={formulario.peso_kg}
                onChange={actualizar}
                required
              />
              <div className="form-text">
                Pésese siempre a la misma hora, de preferencia en ayunas.
              </div>
            </div>

            <div className="mb-3">
              <label className="form-label" htmlFor="perimetro_cintura_cm">
                Perímetro de cintura, en centímetros <span className="texto-ayuda">(opcional)</span>
              </label>
              <input
                id="perimetro_cintura_cm"
                name="perimetro_cintura_cm"
                type="number"
                inputMode="decimal"
                step="0.5"
                min={PERIMETRO_MINIMO}
                max={PERIMETRO_MAXIMO}
                className="form-control form-control-lg control-tactil"
                value={formulario.perimetro_cintura_cm}
                onChange={actualizar}
              />
              <div className="form-text">
                Mida a la altura del ombligo, sin apretar la cinta.
              </div>
            </div>

            <div className="mb-3">
              <label className="form-label" htmlFor="sesiones_cumplidas">
                Sesiones de entrenamiento que completó
              </label>
              <select
                id="sesiones_cumplidas"
                name="sesiones_cumplidas"
                className="form-select form-select-lg control-tactil"
                value={formulario.sesiones_cumplidas}
                onChange={actualizar}
              >
                {[0, 1, 2, 3, 4, 5, 6, 7].map((cantidad) => (
                  <option key={cantidad} value={cantidad}>
                    {cantidad} {cantidad === 1 ? 'sesión' : 'sesiones'}
                  </option>
                ))}
              </select>
            </div>

            <div className="mb-3">
              <label className="form-label" htmlFor="adherencia_nutricional">
                ¿Qué tanto siguió su plan de comidas? {formulario.adherencia_nutricional} %
              </label>
              <input
                id="adherencia_nutricional"
                name="adherencia_nutricional"
                type="range"
                min="0"
                max="100"
                step="5"
                className="form-range"
                value={formulario.adherencia_nutricional}
                onChange={actualizar}
              />
              <div className="form-text">
                Sea honesto: el sistema usa este dato para saber si el plan está
                funcionando o si el problema fue el cumplimiento.
              </div>
            </div>

            <div className="mb-4">
              <label className="form-label" htmlFor="fecha_registro">
                Fecha del registro
              </label>
              <input
                id="fecha_registro"
                name="fecha_registro"
                type="date"
                max={hoyEnTextoLocal()}
                className="form-control form-control-lg control-tactil"
                value={formulario.fecha_registro}
                onChange={actualizar}
              />
            </div>

            <button
              type="submit"
              className="btn btn-principal btn-lg w-100 control-tactil"
              disabled={enviando}
            >
              {enviando ? 'Guardando…' : 'Guardar mi avance'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
