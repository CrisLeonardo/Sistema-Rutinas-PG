/**
 * Bitácora de una sesión de entrenamiento.
 *
 * Es la pantalla que se usa dentro del gimnasio, con el teléfono en la mano
 * entre serie y serie. De eso salen sus tres decisiones de diseño:
 *
 * 1. Todo viene precargado. La carga que el sistema sugiere y las repeticiones
 *    objetivo ya están escritas: confirmar una serie es un toque, no cuatro
 *    campos. Corregir sigue siendo posible, pero no es lo normal.
 * 2. Lo escrito se guarda en el dispositivo conforme se avanza. Un teléfono que
 *    se bloquea a mitad de la sesión no debe costarle al usuario el
 *    entrenamiento entero.
 * 3. El descanso se cronometra solo. Es parte de la dosis prescrita, y hasta
 *    ahora la pantalla lo declaraba en texto y confiaba en que alguien lo
 *    midiera.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import CronometroDescanso from '../componentes/CronometroDescanso.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioEntrenamiento } from '../servicios/api.js'

const ESFUERZOS = [
  { valor: 3, etiqueta: 'Suave', detalle: 'Terminé con mucho de sobra' },
  { valor: 6, etiqueta: 'Exigente', detalle: 'Costó, pero lo completé bien' },
  { valor: 8, etiqueta: 'Muy duro', detalle: 'Las últimas series me costaron mucho' },
  { valor: 10, etiqueta: 'Al límite', detalle: 'No habría podido con una serie más' },
]

const clave = (sesionId) => `rutinas.bitacora.${sesionId}`

/** Fecha en el formato en que se lee, no en el que viaja. */
function fechaCorta(valor) {
  if (!valor) return ''
  return new Date(`${valor}T12:00:00`).toLocaleDateString('es-GT', {
    day: 'numeric',
    month: 'long',
  })
}

/**
 * Resume lo que se hizo la última vez.
 *
 * Cinco series iguales se leen mejor como «5×12 con 45 kg» que repitiendo
 * «12×45 kg» cinco veces, que es lo que produce una lista literal.
 */
function resumirSeries(series) {
  if (series.length === 0) return ''

  const primera = series[0]
  const todasIguales = series.every(
    (serie) =>
      serie.repeticiones === primera.repeticiones && serie.peso_kg === primera.peso_kg,
  )

  if (todasIguales) {
    const carga = primera.peso_kg !== null ? ` con ${primera.peso_kg} kg` : ''
    return `${series.length}×${primera.repeticiones} repeticiones${carga}`
  }

  return series
    .map((serie) =>
      serie.peso_kg !== null
        ? `${serie.repeticiones}×${serie.peso_kg} kg`
        : `${serie.repeticiones} reps`,
    )
    .join(' · ')
}

/** Recupera el avance guardado en el dispositivo, si lo hay. */
function leerAvance(sesionId) {
  try {
    const guardado = localStorage.getItem(clave(sesionId))
    return guardado ? JSON.parse(guardado) : null
  } catch {
    return null
  }
}

function guardarAvance(sesionId, series) {
  try {
    localStorage.setItem(clave(sesionId), JSON.stringify({ fecha: Date.now(), series }))
  } catch {
    // Con el almacenamiento bloqueado la sesión sigue funcionando en memoria.
  }
}

function borrarAvance(sesionId) {
  try {
    localStorage.removeItem(clave(sesionId))
  } catch {
    // Nada que informar.
  }
}

/** Construye la cuadrícula inicial: una fila por serie prescrita, ya precargada. */
function filasIniciales(sesion) {
  const filas = {}
  sesion.ejercicios.forEach((ejercicio) => {
    const sugerida = ejercicio.recomendacion.carga_sugerida_kg
    const objetivo = ejercicio.recomendacion.repeticiones_objetivo
    filas[ejercicio.ejercicio_id] = Array.from({ length: ejercicio.series }, (_, indice) => {
      const previa = ejercicio.ultima_vez[indice]
      return {
        numero_serie: indice + 1,
        repeticiones: String(objetivo ?? ejercicio.repeticiones_min),
        peso_kg: sugerida !== null ? String(sugerida) : previa?.peso_kg != null ? String(previa.peso_kg) : '',
        hecha: false,
      }
    })
  })
  return filas
}

export default function BitacoraSesion() {
  const { sesionId } = useParams()
  const { token } = useSesion()
  const navegar = useNavigate()

  const [sesion, setSesion] = useState(null)
  const [filas, setFilas] = useState({})
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [guardando, setGuardando] = useState(false)
  const [resultado, setResultado] = useState(null)
  const [descanso, setDescanso] = useState(null)
  const [esfuerzo, setEsfuerzo] = useState(6)
  const [notas, setNotas] = useState('')

  const iniciada = useRef(Date.now())

  useEffect(() => {
    let vigente = true
    setCargando(true)
    servicioEntrenamiento
      .abrirSesion(sesionId, token)
      .then((datos) => {
        if (!vigente) return
        setSesion(datos)
        const avance = leerAvance(sesionId)
        setFilas(avance?.series ?? filasIniciales(datos))
        setError(null)
      })
      .catch((fallo) => {
        if (vigente) setError(fallo.message)
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })
    return () => {
      vigente = false
    }
  }, [sesionId, token])

  const actualizarFila = useCallback(
    (ejercicioId, indice, campo, valor) => {
      setFilas((anterior) => {
        const siguiente = {
          ...anterior,
          [ejercicioId]: anterior[ejercicioId].map((fila, posicion) =>
            posicion === indice ? { ...fila, [campo]: valor } : fila,
          ),
        }
        guardarAvance(sesionId, siguiente)
        return siguiente
      })
    },
    [sesionId],
  )

  const alternarHecha = useCallback(
    (ejercicio, indice) => {
      const fila = filas[ejercicio.ejercicio_id][indice]
      const seMarca = !fila.hecha
      actualizarFila(ejercicio.ejercicio_id, indice, 'hecha', seMarca)
      // El descanso arranca al confirmar, no al desmarcar, y no en la última
      // serie del último ejercicio: ahí ya no hay nada que esperar.
      const esUltima =
        ejercicio.orden === sesion.ejercicios.length &&
        indice === filas[ejercicio.ejercicio_id].length - 1
      if (seMarca && !esUltima) {
        setDescanso({ segundos: ejercicio.descanso_segundos, sello: Date.now() })
      }
    },
    [filas, actualizarFila, sesion],
  )

  const completadas = useMemo(
    () => Object.values(filas).flat().filter((fila) => fila.hecha).length,
    [filas],
  )
  const totales = useMemo(() => Object.values(filas).flat().length, [filas])

  const volumen = useMemo(
    () =>
      Object.values(filas)
        .flat()
        .filter((fila) => fila.hecha)
        .reduce(
          (suma, fila) => suma + (Number(fila.peso_kg) || 0) * (Number(fila.repeticiones) || 0),
          0,
        ),
    [filas],
  )

  const guardar = async () => {
    const series = Object.entries(filas).flatMap(([ejercicioId, delEjercicio]) =>
      delEjercicio
        .filter((fila) => fila.hecha)
        .map((fila) => ({
          ejercicio_id: Number(ejercicioId),
          numero_serie: fila.numero_serie,
          repeticiones: Number(fila.repeticiones) || 0,
          peso_kg: fila.peso_kg === '' ? null : Number(fila.peso_kg),
        })),
    )

    if (series.length === 0) {
      setError('Marque al menos una serie como hecha antes de guardar.')
      return
    }

    setGuardando(true)
    setError(null)
    try {
      const respuesta = await servicioEntrenamiento.registrarSesion(
        {
          sesion_id: sesion.sesion_id,
          duracion_minutos: Math.max(Math.round((Date.now() - iniciada.current) / 60000), 1),
          percepcion_esfuerzo: esfuerzo,
          notas: notas.trim() || null,
          series,
        },
        token,
      )
      borrarAvance(sesionId)
      setResultado(respuesta)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (fallo) {
      setError(fallo instanceof ErrorApi ? fallo.message : 'No se pudo guardar la sesión.')
    } finally {
      setGuardando(false)
    }
  }

  if (cargando) {
    return <p className="texto-ayuda">Preparando su sesión…</p>
  }

  if (error && !sesion) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
        <div className="mt-2">
          <Link to="/rutina" className="btn btn-sm btn-principal control-tactil">
            Volver a mi rutina
          </Link>
        </div>
      </div>
    )
  }

  if (resultado) {
    return <SesionGuardada resultado={resultado} alVolver={() => navegar('/rutina')} />
  }

  return (
    <div className="row g-4">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-start gap-3">
          <div>
            <h1 className="h3 mb-1">{sesion.nombre_grupo}</h1>
            <p className="texto-ayuda mb-0">
              {sesion.nombre_dia} · {sesion.ejercicios.length} ejercicios ·{' '}
              {sesion.duracion_estimada_minutos} minutos aproximados
            </p>
          </div>
          <Link
            to="/rutina"
            className="btn btn-outline-secondary btn-sm control-tactil flex-shrink-0"
          >
            Salir
          </Link>
        </div>
      </div>

      {sesion.ya_registrada_hoy && (
        <div className="col-12">
          <div className="alert alert-warning mb-0" role="alert">
            Ya registró esta sesión hoy. Si la guarda otra vez, el entrenamiento se contará
            dos veces y su progresión quedará distorsionada.
          </div>
        </div>
      )}

      <div className="col-12">
        <div className="marcador-sesion">
          <div>
            <span className="marcador-cifra">
              {completadas} <span className="texto-ayuda">de {totales}</span>
            </span>
            <span className="texto-ayuda d-block">series hechas</span>
          </div>
          <div className="text-end">
            <span className="marcador-cifra">{Math.round(volumen).toLocaleString('es-GT')}</span>
            <span className="texto-ayuda d-block">kg de volumen</span>
          </div>
        </div>
        <div
          className="progress mt-2"
          role="progressbar"
          aria-label="Avance de la sesión"
          aria-valuenow={completadas}
          aria-valuemin={0}
          aria-valuemax={totales}
        >
          <div
            className="progress-bar barra-avance"
            style={{ width: `${totales ? (completadas / totales) * 100 : 0}%` }}
          />
        </div>
      </div>

      {descanso && (
        <div className="col-12">
          <CronometroDescanso
            key={descanso.sello}
            segundos={descanso.segundos}
            alSaltar={() => setDescanso(null)}
          />
        </div>
      )}

      {sesion.ejercicios.map((ejercicio) => (
        <div className="col-12" key={ejercicio.ejercicio_id}>
          <BloqueEjercicio
            ejercicio={ejercicio}
            filas={filas[ejercicio.ejercicio_id] ?? []}
            alCambiar={(indice, campo, valor) =>
              actualizarFila(ejercicio.ejercicio_id, indice, campo, valor)
            }
            alMarcar={(indice) => alternarHecha(ejercicio, indice)}
          />
        </div>
      ))}

      <div className="col-12">
        <div className="card shadow-sm">
          <div className="card-body">
            <h2 className="h5 card-title">¿Cómo le resultó la sesión?</h2>
            <p className="texto-ayuda">
              Sirve para distinguir un estancamiento por cansancio de uno por falta de
              estímulo: piden respuestas opuestas.
            </p>
            <div className="d-flex flex-column gap-2">
              {ESFUERZOS.map((opcion) => (
                <div className="form-check opcion-tactil" key={opcion.valor}>
                  <input
                    className="form-check-input"
                    type="radio"
                    name="esfuerzo"
                    id={`esfuerzo-${opcion.valor}`}
                    checked={esfuerzo === opcion.valor}
                    onChange={() => setEsfuerzo(opcion.valor)}
                  />
                  <label className="form-check-label" htmlFor={`esfuerzo-${opcion.valor}`}>
                    <span className="fw-semibold">{opcion.etiqueta}</span>
                    <span className="texto-ayuda d-block">{opcion.detalle}</span>
                  </label>
                </div>
              ))}
            </div>

            <div className="mt-3">
              <label className="form-label" htmlFor="notas">
                Notas <span className="texto-ayuda">(opcional)</span>
              </label>
              <textarea
                id="notas"
                className="form-control"
                rows={2}
                maxLength={500}
                value={notas}
                onChange={(evento) => setNotas(evento.target.value)}
                placeholder="Por ejemplo: la máquina de pierna estaba ocupada, hice sentadilla."
              />
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="col-12">
          <div className="alert alert-danger mb-0" role="alert">
            {error}
          </div>
        </div>
      )}

      <div className="col-12">
        <button
          type="button"
          className="btn btn-principal btn-lg w-100 control-tactil"
          onClick={guardar}
          disabled={guardando || completadas === 0}
        >
          {guardando
            ? 'Guardando…'
            : `Terminar y guardar ${completadas} ${completadas === 1 ? 'serie' : 'series'}`}
        </button>
        <p className="texto-ayuda text-center mt-2 mb-0">
          Lo que va marcando se guarda en este teléfono: si se bloquea la pantalla, no
          pierde la sesión.
        </p>
      </div>
    </div>
  )
}

function BloqueEjercicio({ ejercicio, filas, alCambiar, alMarcar }) {
  const { recomendacion } = ejercicio
  const primeraVez = recomendacion.decision === 'primera_vez'

  return (
    <div className="card shadow-sm">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start gap-3">
          <div>
            <h2 className="h5 card-title mb-1">
              {ejercicio.orden}. {ejercicio.nombre}
            </h2>
            <p className="texto-ayuda mb-0">
              {ejercicio.prescripcion} · {ejercicio.equipamiento}
            </p>
          </div>
          {recomendacion.carga_sugerida_kg !== null && (
            <div className="text-end flex-shrink-0">
              <div className="carga-sugerida">{recomendacion.carga_sugerida_kg} kg</div>
              <div className="texto-ayuda">sugerido</div>
            </div>
          )}
        </div>

        <div className={`nota-progresion ${recomendacion.hay_incremento ? 'nota-sube' : ''}`}>
          {recomendacion.hay_incremento && (
            <span className="insignia-sube">Sube la carga</span>
          )}
          {recomendacion.explicacion}
        </div>

        {ejercicio.ultima_vez.length > 0 && (
          <p className="texto-ayuda mb-2">
            El {fechaCorta(ejercicio.fecha_ultima_vez)} hizo{' '}
            {resumirSeries(ejercicio.ultima_vez)}.
          </p>
        )}

        <div className="cuadricula-series">
          <div className="encabezado-serie texto-ayuda">Serie</div>
          <div className="encabezado-serie texto-ayuda">Repeticiones</div>
          <div className="encabezado-serie texto-ayuda">Peso (kg)</div>
          <div className="encabezado-serie texto-ayuda">Hecha</div>

          {filas.map((fila, indice) => (
            <Fragmento
              key={fila.numero_serie}
              fila={fila}
              indice={indice}
              ejercicio={ejercicio}
              primeraVez={primeraVez}
              alCambiar={alCambiar}
              alMarcar={alMarcar}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

function Fragmento({ fila, indice, ejercicio, primeraVez, alCambiar, alMarcar }) {
  const identificador = `${ejercicio.ejercicio_id}-${fila.numero_serie}`
  return (
    <>
      <div className={`numero-serie ${fila.hecha ? 'serie-hecha' : ''}`}>
        {fila.numero_serie}
      </div>
      <div>
        <label className="visually-hidden" htmlFor={`reps-${identificador}`}>
          Repeticiones de la serie {fila.numero_serie} de {ejercicio.nombre}
        </label>
        <input
          id={`reps-${identificador}`}
          type="number"
          inputMode="numeric"
          min="0"
          max="100"
          className="form-control control-tactil"
          value={fila.repeticiones}
          onChange={(evento) => alCambiar(indice, 'repeticiones', evento.target.value)}
        />
      </div>
      <div>
        <label className="visually-hidden" htmlFor={`peso-${identificador}`}>
          Peso de la serie {fila.numero_serie} de {ejercicio.nombre}
        </label>
        <input
          id={`peso-${identificador}`}
          type="number"
          inputMode="decimal"
          min="0"
          max="500"
          step="0.5"
          className="form-control control-tactil"
          value={fila.peso_kg}
          placeholder={primeraVez ? '—' : ''}
          onChange={(evento) => alCambiar(indice, 'peso_kg', evento.target.value)}
        />
      </div>
      <div>
        <button
          type="button"
          className={`btn control-tactil w-100 ${fila.hecha ? 'btn-principal' : 'btn-outline-secondary'}`}
          onClick={() => alMarcar(indice)}
          aria-pressed={fila.hecha}
          aria-label={`Marcar la serie ${fila.numero_serie} como hecha`}
        >
          {fila.hecha ? '✓' : '○'}
        </button>
      </div>
    </>
  )
}

function SesionGuardada({ resultado, alVolver }) {
  const suben = resultado.progresiones.filter((p) => p.hay_incremento)

  return (
    <div className="row g-4">
      <div className="col-12">
        <div className="card shadow-sm borde-destacado">
          <div className="card-body p-4">
            <h1 className="h4 card-title">Sesión guardada</h1>
            <p className="mb-3">{resultado.mensaje}</p>
            <div className="d-flex gap-4 flex-wrap">
              <div>
                <div className="cifra-panel">{resultado.sesion.series_totales}</div>
                <div className="texto-ayuda">series</div>
              </div>
              <div>
                <div className="cifra-panel">{resultado.sesion.repeticiones_totales}</div>
                <div className="texto-ayuda">repeticiones</div>
              </div>
              <div>
                <div className="cifra-panel">
                  {Math.round(resultado.sesion.volumen_kg).toLocaleString('es-GT')}
                </div>
                <div className="texto-ayuda">kg de volumen</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {suben.length > 0 && (
        <div className="col-12">
          <div className="card shadow-sm">
            <div className="card-body">
              <h2 className="h5 card-title">Para la próxima vez</h2>
              <ul className="list-group list-group-flush">
                {suben.map((progresion) => (
                  <li
                    key={`${progresion.carga_previa_kg}-${progresion.carga_sugerida_kg}-${progresion.explicacion.slice(0, 20)}`}
                    className="list-group-item px-0"
                  >
                    <div className="fw-semibold">
                      {progresion.carga_previa_kg} kg → {progresion.carga_sugerida_kg} kg
                    </div>
                    <div className="texto-ayuda">{progresion.explicacion}</div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className="col-12 d-flex flex-column flex-sm-row gap-2">
        <button type="button" className="btn btn-principal control-tactil" onClick={alVolver}>
          Volver a mi rutina
        </button>
        <Link to="/bitacora" className="btn btn-outline-secondary control-tactil">
          Ver mi bitácora
        </Link>
      </div>
    </div>
  )
}
