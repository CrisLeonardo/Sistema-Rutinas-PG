/**
 * Pantalla de captura del perfil biométrico (historia HU-04).
 *
 * El formulario se divide en tres pasos cortos, conforme al requerimiento no
 * funcional 4.5.3. Las validaciones que se aplican aquí son un apoyo a la
 * experiencia de uso: el servidor las vuelve a verificar en su totalidad, según
 * exige el apartado 4.8.3.
 */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  NIVELES_ACTIVIDAD,
  NIVELES_EXPERIENCIA,
  OBJETIVOS,
  RANGOS,
  SEXOS,
  etiquetaDe,
} from '../datos/catalogos.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPerfil } from '../servicios/api.js'

const PASOS = [
  { numero: 1, titulo: 'Sus medidas', ayuda: 'Datos con los que se calcula su gasto energético.' },
  { numero: 2, titulo: 'Su actividad', ayuda: 'Cuánto se mueve durante la semana y qué busca lograr.' },
  { numero: 3, titulo: 'Su entrenamiento', ayuda: 'Con esto se ajusta el volumen de la rutina.' },
]

const FORMULARIO_INICIAL = {
  peso_kg: '',
  estatura_cm: '',
  edad: '',
  sexo: '',
  nivel_actividad: '',
  objetivo: '',
  nivel_experiencia: 'principiante',
  dias_entrenamiento_semana: '3',
}

/** Traduce el índice de masa corporal a una lectura sencilla, igual que el servidor. */
function clasificarIndice(indice) {
  if (indice < 18.5) return 'Peso por debajo de lo normal'
  if (indice < 25) return 'Peso normal'
  if (indice < 30) return 'Sobrepeso'
  return 'Obesidad'
}

/** Calcula el índice mientras el usuario escribe, para dar retroalimentación inmediata. */
function calcularIndice(peso, estatura) {
  const kilogramos = Number(peso)
  const metros = Number(estatura) / 100
  if (!kilogramos || !metros) return null
  return Math.round((kilogramos / metros ** 2) * 100) / 100
}

export default function PerfilBiometrico() {
  const { token } = useSesion()
  const navegar = useNavigate()

  const [formulario, setFormulario] = useState(FORMULARIO_INICIAL)
  const [paso, setPaso] = useState(1)
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [cargando, setCargando] = useState(true)
  const [teniaPerfil, setTeniaPerfil] = useState(false)

  // Precarga la última medición para que actualizar los datos no obligue a
  // escribirlo todo de nuevo. Aun así, al guardar se crea un registro nuevo y el
  // anterior se conserva (historia HU-05).
  useEffect(() => {
    let vigente = true
    servicioPerfil
      .consultarVigente(token)
      .then((perfil) => {
        if (!vigente) return
        setTeniaPerfil(true)
        setFormulario({
          peso_kg: String(perfil.peso_kg),
          estatura_cm: String(perfil.estatura_cm),
          edad: String(perfil.edad),
          sexo: perfil.sexo,
          nivel_actividad: perfil.nivel_actividad,
          objetivo: perfil.objetivo,
          nivel_experiencia: perfil.nivel_experiencia,
          dias_entrenamiento_semana: String(perfil.dias_entrenamiento_semana),
        })
      })
      .catch(() => {
        // Sin perfil previo se conserva el formulario vacío.
      })
      .finally(() => {
        if (vigente) setCargando(false)
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
  const validarPaso = (numero) => {
    if (numero === 1) {
      const peso = Number(formulario.peso_kg)
      const estatura = Number(formulario.estatura_cm)
      const edad = Number(formulario.edad)

      if (!formulario.peso_kg || peso < RANGOS.pesoMinimo || peso > RANGOS.pesoMaximo) {
        return `El peso debe estar entre ${RANGOS.pesoMinimo} y ${RANGOS.pesoMaximo} kilogramos.`
      }
      if (
        !formulario.estatura_cm ||
        estatura < RANGOS.estaturaMinima ||
        estatura > RANGOS.estaturaMaxima
      ) {
        return `La estatura debe estar entre ${RANGOS.estaturaMinima} y ${RANGOS.estaturaMaxima} centímetros.`
      }
      if (!formulario.edad || edad < RANGOS.edadMinima) {
        return 'El sistema solo genera planes para personas mayores de dieciocho años.'
      }
      if (edad > RANGOS.edadMaxima) {
        return `La edad no puede superar los ${RANGOS.edadMaxima} años.`
      }
      if (!formulario.sexo) {
        return 'Indique su sexo; las fórmulas de referencia lo requieren.'
      }
    }

    if (numero === 2) {
      if (!formulario.nivel_actividad) return 'Seleccione su nivel de actividad física.'
      if (!formulario.objetivo) return 'Seleccione el objetivo que desea alcanzar.'
    }

    if (numero === 3) {
      const dias = Number(formulario.dias_entrenamiento_semana)
      if (!formulario.nivel_experiencia) return 'Seleccione su nivel de experiencia.'
      if (dias < RANGOS.diasMinimos || dias > RANGOS.diasMaximos) {
        return `Los días de entrenamiento deben estar entre ${RANGOS.diasMinimos} y ${RANGOS.diasMaximos} por semana.`
      }
    }

    return null
  }

  const avanzar = () => {
    const problema = validarPaso(paso)
    if (problema) {
      setError(problema)
      return
    }
    setError(null)
    setPaso((actual) => Math.min(actual + 1, PASOS.length))
  }

  const retroceder = () => {
    setError(null)
    setPaso((actual) => Math.max(actual - 1, 1))
  }

  const enviar = async (evento) => {
    evento.preventDefault()
    for (const numero of [1, 2, 3]) {
      const problema = validarPaso(numero)
      if (problema) {
        setPaso(numero)
        setError(problema)
        return
      }
    }

    setError(null)
    setEnviando(true)
    try {
      await servicioPerfil.registrar(
        {
          peso_kg: Number(formulario.peso_kg),
          estatura_cm: Number(formulario.estatura_cm),
          edad: Number(formulario.edad),
          sexo: formulario.sexo,
          nivel_actividad: formulario.nivel_actividad,
          objetivo: formulario.objetivo,
          nivel_experiencia: formulario.nivel_experiencia,
          dias_entrenamiento_semana: Number(formulario.dias_entrenamiento_semana),
        },
        token,
      )
      navegar('/historial-medidas', { replace: true })
    } catch (fallo) {
      setError(fallo instanceof ErrorApi ? fallo.message : 'No fue posible guardar sus medidas.')
    } finally {
      setEnviando(false)
    }
  }

  const indice = calcularIndice(formulario.peso_kg, formulario.estatura_cm)

  if (cargando) {
    return <p className="texto-ayuda">Cargando sus datos…</p>
  }

  return (
    <div className="d-flex justify-content-center">
      <div className="card shadow-sm tarjeta-formulario">
        <div className="card-body p-4">
          <h1 className="h4 mb-1">
            {teniaPerfil ? 'Actualizar mis medidas' : 'Mi perfil biométrico'}
          </h1>
          <p className="texto-ayuda">
            {teniaPerfil
              ? 'Sus medidas anteriores se conservan; esta actualización se agrega a su historial.'
              : 'Con estos datos el sistema calcula su requerimiento de energía y su rutina.'}
          </p>

          <ol className="lista-pasos" aria-label="Avance del formulario">
            {PASOS.map((definicion) => (
              <li
                key={definicion.numero}
                className={`paso ${definicion.numero === paso ? 'paso-activo' : ''} ${
                  definicion.numero < paso ? 'paso-completo' : ''
                }`}
              >
                <span className="paso-numero">{definicion.numero}</span>
                <span className="paso-titulo">{definicion.titulo}</span>
              </li>
            ))}
          </ol>

          <p className="texto-ayuda">{PASOS[paso - 1].ayuda}</p>

          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={enviar} noValidate>
            {paso === 1 && (
              <>
                <div className="mb-3">
                  <label className="form-label" htmlFor="peso_kg">
                    Peso, en kilogramos
                  </label>
                  <input
                    id="peso_kg"
                    name="peso_kg"
                    type="number"
                    inputMode="decimal"
                    step="0.1"
                    min={RANGOS.pesoMinimo}
                    max={RANGOS.pesoMaximo}
                    className="form-control form-control-lg control-tactil"
                    value={formulario.peso_kg}
                    onChange={actualizar}
                    required
                  />
                  <div className="form-text">
                    Entre {RANGOS.pesoMinimo} y {RANGOS.pesoMaximo} kilogramos.
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label" htmlFor="estatura_cm">
                    Estatura, en centímetros
                  </label>
                  <input
                    id="estatura_cm"
                    name="estatura_cm"
                    type="number"
                    inputMode="decimal"
                    step="0.5"
                    min={RANGOS.estaturaMinima}
                    max={RANGOS.estaturaMaxima}
                    className="form-control form-control-lg control-tactil"
                    value={formulario.estatura_cm}
                    onChange={actualizar}
                    required
                  />
                  <div className="form-text">
                    Por ejemplo, 1.70 metros se escribe como 170.
                  </div>
                </div>

                <div className="mb-3">
                  <label className="form-label" htmlFor="edad">
                    Edad, en años cumplidos
                  </label>
                  <input
                    id="edad"
                    name="edad"
                    type="number"
                    inputMode="numeric"
                    step="1"
                    min={RANGOS.edadMinima}
                    max={RANGOS.edadMaxima}
                    className="form-control form-control-lg control-tactil"
                    value={formulario.edad}
                    onChange={actualizar}
                    required
                  />
                  <div className="form-text">
                    El sistema atiende únicamente a personas mayores de edad.
                  </div>
                </div>

                <fieldset className="mb-3">
                  <legend className="form-label">Sexo</legend>
                  {SEXOS.map((opcion) => (
                    <div className="form-check opcion-tactil" key={opcion.valor}>
                      <input
                        className="form-check-input"
                        type="radio"
                        name="sexo"
                        id={`sexo-${opcion.valor}`}
                        value={opcion.valor}
                        checked={formulario.sexo === opcion.valor}
                        onChange={actualizar}
                      />
                      <label className="form-check-label" htmlFor={`sexo-${opcion.valor}`}>
                        {opcion.etiqueta}
                      </label>
                    </div>
                  ))}
                  <div className="form-text">
                    Las fórmulas de Mifflin-St Jeor y Harris-Benedict lo utilizan para
                    calcular su gasto de energía en reposo.
                  </div>
                </fieldset>

                {indice !== null && (
                  <div className="alert alert-light border" role="status">
                    <div className="fw-semibold">Índice de masa corporal: {indice}</div>
                    <div className="texto-ayuda mb-0">
                      {clasificarIndice(indice)}. Es una referencia general, no un
                      diagnóstico médico.
                    </div>
                  </div>
                )}
              </>
            )}

            {paso === 2 && (
              <>
                <fieldset className="mb-4">
                  <legend className="form-label">¿Qué tan activo es en su día a día?</legend>
                  {NIVELES_ACTIVIDAD.map((opcion) => (
                    <div className="form-check opcion-tactil" key={opcion.valor}>
                      <input
                        className="form-check-input"
                        type="radio"
                        name="nivel_actividad"
                        id={`actividad-${opcion.valor}`}
                        value={opcion.valor}
                        checked={formulario.nivel_actividad === opcion.valor}
                        onChange={actualizar}
                      />
                      <label className="form-check-label" htmlFor={`actividad-${opcion.valor}`}>
                        <span className="fw-semibold">{opcion.etiqueta}</span>
                        <span className="d-block texto-ayuda">{opcion.detalle}</span>
                      </label>
                    </div>
                  ))}
                </fieldset>

                <fieldset className="mb-3">
                  <legend className="form-label">¿Qué desea lograr?</legend>
                  {OBJETIVOS.map((opcion) => (
                    <div className="form-check opcion-tactil" key={opcion.valor}>
                      <input
                        className="form-check-input"
                        type="radio"
                        name="objetivo"
                        id={`objetivo-${opcion.valor}`}
                        value={opcion.valor}
                        checked={formulario.objetivo === opcion.valor}
                        onChange={actualizar}
                      />
                      <label className="form-check-label" htmlFor={`objetivo-${opcion.valor}`}>
                        <span className="fw-semibold">{opcion.etiqueta}</span>
                        <span className="d-block texto-ayuda">{opcion.detalle}</span>
                      </label>
                    </div>
                  ))}
                </fieldset>
              </>
            )}

            {paso === 3 && (
              <>
                <fieldset className="mb-4">
                  <legend className="form-label">¿Cuánta experiencia tiene entrenando?</legend>
                  {NIVELES_EXPERIENCIA.map((opcion) => (
                    <div className="form-check opcion-tactil" key={opcion.valor}>
                      <input
                        className="form-check-input"
                        type="radio"
                        name="nivel_experiencia"
                        id={`experiencia-${opcion.valor}`}
                        value={opcion.valor}
                        checked={formulario.nivel_experiencia === opcion.valor}
                        onChange={actualizar}
                      />
                      <label className="form-check-label" htmlFor={`experiencia-${opcion.valor}`}>
                        <span className="fw-semibold">{opcion.etiqueta}</span>
                        <span className="d-block texto-ayuda">{opcion.detalle}</span>
                      </label>
                    </div>
                  ))}
                </fieldset>

                <div className="mb-4">
                  <label className="form-label" htmlFor="dias_entrenamiento_semana">
                    Días que puede entrenar por semana
                  </label>
                  <select
                    id="dias_entrenamiento_semana"
                    name="dias_entrenamiento_semana"
                    className="form-select form-select-lg control-tactil"
                    value={formulario.dias_entrenamiento_semana}
                    onChange={actualizar}
                  >
                    {[1, 2, 3, 4, 5, 6, 7].map((dias) => (
                      <option key={dias} value={dias}>
                        {dias} {dias === 1 ? 'día' : 'días'}
                      </option>
                    ))}
                  </select>
                  <div className="form-text">
                    Su rutina tendrá exactamente esta cantidad de sesiones.
                  </div>
                </div>

                <div className="card bg-light border-0 mb-4">
                  <div className="card-body">
                    <h2 className="h6">Resumen de lo que va a guardar</h2>
                    <dl className="row mb-0 small">
                      <dt className="col-6">Peso</dt>
                      <dd className="col-6">{formulario.peso_kg} kg</dd>
                      <dt className="col-6">Estatura</dt>
                      <dd className="col-6">{formulario.estatura_cm} cm</dd>
                      <dt className="col-6">Edad</dt>
                      <dd className="col-6">{formulario.edad} años</dd>
                      <dt className="col-6">Sexo</dt>
                      <dd className="col-6">{etiquetaDe(SEXOS, formulario.sexo)}</dd>
                      <dt className="col-6">Actividad</dt>
                      <dd className="col-6">
                        {etiquetaDe(NIVELES_ACTIVIDAD, formulario.nivel_actividad)}
                      </dd>
                      <dt className="col-6">Objetivo</dt>
                      <dd className="col-6">{etiquetaDe(OBJETIVOS, formulario.objetivo)}</dd>
                      <dt className="col-6">Índice de masa corporal</dt>
                      <dd className="col-6 mb-0">{indice ?? '—'}</dd>
                    </dl>
                  </div>
                </div>
              </>
            )}

            <div className="d-flex gap-2">
              {paso > 1 && (
                <button
                  type="button"
                  className="btn btn-outline-secondary btn-lg control-tactil flex-fill"
                  onClick={retroceder}
                >
                  Atrás
                </button>
              )}
              {paso < PASOS.length ? (
                <button
                  type="button"
                  className="btn btn-principal btn-lg control-tactil flex-fill"
                  onClick={avanzar}
                >
                  Continuar
                </button>
              ) : (
                <button
                  type="submit"
                  className="btn btn-principal btn-lg control-tactil flex-fill"
                  disabled={enviando}
                >
                  {enviando ? 'Guardando…' : 'Guardar mis medidas'}
                </button>
              )}
            </div>
          </form>

          <p className="texto-ayuda mt-4 mb-0">
            Sus datos biométricos son privados: nadie más, ni el administrador del
            sistema, puede consultarlos.
          </p>
        </div>
      </div>
    </div>
  )
}
