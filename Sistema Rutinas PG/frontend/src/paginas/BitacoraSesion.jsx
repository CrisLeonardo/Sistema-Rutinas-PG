/**
 * Bitácora de una sesión de entrenamiento.
 *
 * Es la pantalla que se usa dentro del gimnasio, con el teléfono en la mano
 * entre serie y serie. De eso salen sus decisiones de diseño:
 *
 * 1. Es modo enfoque: sin barra de navegación. Salir a otra pantalla en mitad
 *    de una serie es un accidente, no una intención; para irse está «Salir».
 * 2. Todo viene precargado. La carga que el sistema sugiere y las repeticiones
 *    objetivo ya están escritas: confirmar una serie es un toque, no cuatro
 *    campos. Corregir sigue siendo posible, pero no es lo normal.
 * 3. Lo escrito se guarda en el dispositivo conforme se avanza. Un teléfono que
 *    se bloquea a mitad de la sesión no debe costarle al usuario el
 *    entrenamiento entero.
 * 4. El descanso se cronometra solo. Es parte de la dosis prescrita, y hasta
 *    ahora la pantalla lo declaraba en texto y confiaba en que alguien lo
 *    midiera.
 * 5. La acción de cierre vive en un pie fijo. Al final de una sesión de cinco
 *    ejercicios, el botón de guardar quedaba a un desplazamiento de distancia.
 *
 * La pregunta del esfuerzo percibido y las notas se preguntan al terminar, en
 * una hoja: antes ocupaban una tarjeta entera en medio de los ejercicios, entre
 * el usuario y el botón de guardar.
 */

import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import AvisoDeError from '../componentes/AvisoDeError.jsx'
import CronometroDescanso from '../componentes/CronometroDescanso.jsx'
import Hoja from '../componentes/Hoja.jsx'
import LimiteRecurso from '../componentes/LimiteRecurso.jsx'
import Icono from '../componentes/Icono.jsx'
import RespuestaAccion from '../componentes/RespuestaAccion.jsx'
import ResultadoAccion from '../componentes/ResultadoAccion.jsx'
import RecompensaAccion from '../componentes/RecompensaAccion.jsx'
import { textoConfirmacionSerie } from '../interaccion/respuestas.mjs'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioEntrenamiento } from '../servicios/api.js'
import { entero, fechaLarga } from '../utilidades/formatos.js'

const ESFUERZOS = [
  { valor: 3, etiqueta: 'Suave', detalle: 'Terminé con mucho de sobra' },
  { valor: 6, etiqueta: 'Exigente', detalle: 'Costó, pero lo completé bien' },
  { valor: 8, etiqueta: 'Muy duro', detalle: 'Las últimas series me costaron mucho' },
  { valor: 10, etiqueta: 'Al límite', detalle: 'No habría podido con una serie más' },
]

const clave = (sesionId) => `rutinas.bitacora.v2.${sesionId}`
const FichaEjercicio = lazy(() => import('../entrenamiento/FichaEjercicio.jsx'))

/** Fecha en el formato en que se lee, no en el que viaja. */
function fechaCorta(valor) {
  if (!valor) return ''
  return fechaLarga(`${valor}T12:00:00`).replace(/ de \d{4}$/, '')
}

/**
 * Resume lo que se hizo la última vez.
 *
 * Cinco series iguales se leen mejor como «5×12 con 45 kg» que repitiendo
 * «12×45 kg» cinco veces, que es lo que produce una lista literal.
 */
function resumirSeries(series) {
  if (series.length === 0) return ''

  if (series.some(s => s.duracion_segundos != null)) return series.map(s => s.duracion_segundos != null ? `${s.duracion_segundos} s` : `${s.repeticiones} reps (registro anterior)`).join(" · ")
  const primera = series[0]
  const todasIguales = series.every(
    (serie) =>
      serie.repeticiones === primera.repeticiones && serie.peso_kg === primera.peso_kg,
  )

  if (todasIguales) {
    const carga = primera.peso_kg !== null ? ` con ${primera.peso_kg} kg` : ''
    return `${series.length}×${primera.repeticiones}${carga}`
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
    filas[ejercicio.ejercicio_id] = Array.from({ length: ejercicio.series }, (unused, indice) => {
      const previa = ejercicio.ultima_vez[indice]
      return {
        numero_serie: indice + 1,
        repeticiones: ejercicio.duracion_segundos_min != null ? "0" : String(objetivo ?? ejercicio.repeticiones_min),
        duracion_segundos: ejercicio.duracion_segundos_min != null ? String(ejercicio.duracion_segundos_min) : null,
        peso_kg:
          ejercicio.duracion_segundos_min != null ? '' : sugerida !== null
            ? String(sugerida)
            : previa?.peso_kg != null
              ? String(previa.peso_kg)
              : '',
        hecha: false,
      }
    })
  })
  return filas
}

export default function BitacoraSesion() {
  const { sesionId } = useParams()
  const { token } = useSesion()

  const [sesion, setSesion] = useState(null)
  const [filas, setFilas] = useState({})
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [guardando, setGuardando] = useState(false)
  const [resultado, setResultado] = useState(null)
  const [descanso, setDescanso] = useState(null)
  const [esfuerzo, setEsfuerzo] = useState(6)
  const [notas, setNotas] = useState('')
  const [hojaAbierta, setHojaAbierta] = useState(null)
  const [ejercicioGuia, setEjercicioGuia] = useState(null)
  const [confirmacion, setConfirmacion] = useState('')
  const cerrarGuia = useCallback(() => setEjercicioGuia(null), [])

  const iniciada = useRef(Date.now())
  const envioEnCurso = useRef(false)
  const cerrarEsfuerzo = useCallback(() => setHojaAbierta(null), [])

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
      setConfirmacion(textoConfirmacionSerie(ejercicio.nombre, indice + 1, seMarca))
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

  /** El ejercicio en curso es el primero al que le faltan series por confirmar. */
  const enCurso = useMemo(() => {
    if (!sesion) return 1
    const pendiente = sesion.ejercicios.findIndex((ejercicio) =>
      (filas[ejercicio.ejercicio_id] ?? []).some((fila) => !fila.hecha),
    )
    return pendiente === -1 ? sesion.ejercicios.length : pendiente + 1
  }, [sesion, filas])

  const guardar = async () => {
    if (envioEnCurso.current) return
    // El orden en que los ejercicios aparecen aquí es el mismo en que el
    // servidor devuelve sus progresiones: se guarda para poder ponerle nombre a
    // cada una en la pantalla de resultado, que es dato que la respuesta no trae.
    const ejerciciosEnOrden = []
    const series = Object.entries(filas).flatMap(([ejercicioId, delEjercicio]) => {
      const hechas = delEjercicio.filter((fila) => fila.hecha)
      if (hechas.length > 0) {
        const ejercicio = sesion.ejercicios.find(
          (candidato) => String(candidato.ejercicio_id) === ejercicioId,
        )
        ejerciciosEnOrden.push(ejercicio?.nombre ?? '')
      }
      return hechas.map((fila) => ({
        ejercicio_id: Number(ejercicioId),
        numero_serie: fila.numero_serie,
        repeticiones: Number(fila.repeticiones) || 0,
        duracion_segundos: fila.duracion_segundos == null ? null : Number(fila.duracion_segundos),
        peso_kg: fila.peso_kg === '' ? null : Number(fila.peso_kg),
      }))
    })

    if (series.length === 0) {
      setError('Marque al menos una serie como hecha antes de guardar.')
      setHojaAbierta(null)
      return
    }

    envioEnCurso.current = true
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
      setHojaAbierta(null)
      setDescanso(null)
      setResultado({ ...respuesta, nombres: ejerciciosEnOrden })
    } catch (fallo) {
      setError(fallo instanceof ErrorApi ? fallo.message : 'No se pudo guardar la sesión.')
    } finally {
      envioEnCurso.current = false
      setGuardando(false)
    }
  }

  if (cargando) {
    return (
      <div className="pila" aria-busy="true">
        <div className="esqueleto esqueleto--titulo" />
        <div className="esqueleto esqueleto--tarjeta" />
        <span className="solo-lectores">Preparando su sesión…</span>
      </div>
    )
  }

  if (error && !sesion) {
    return (
      <div className="pila">
        <AvisoDeError mensaje={error} />
        <Link to="/entrenar" className="boton boton--principal">
          Volver a mi semana
        </Link>
      </div>
    )
  }

  if (resultado) return <SesionGuardada resultado={resultado} />

  return (
    <div className="pila con-pie-fijo">
      <div className="fila--entre">
        <div className="pila-2">
          <h1 className="titulo-tarjeta">{sesion.nombre_grupo}</h1>
          <p className="apoyo mono">
            Ejercicio {enCurso} de {sesion.ejercicios.length}
          </p>
        </div>
        <Link to="/entrenar" className="boton boton--secundario boton--compacto">
          Salir
        </Link>
      </div>

      {sesion.ya_registrada_hoy && (
        <p className="aviso aviso--aviso" role="alert">
          Ya registró esta sesión hoy. Si la guarda otra vez, el entrenamiento se contará dos
          veces y su progresión quedará distorsionada.
        </p>
      )}

      <div className="pila-2">
        <div className="fila--entre">
          <span className="cifra-pequena">
            {completadas} <span className="tinta-4">de {totales} series</span>
          </span>
          <span className="cifra-pequena">
            {entero(volumen)} <span className="tinta-4">kg</span>
          </span>
        </div>
        <div
          className="progreso"
          role="progressbar"
          aria-label="Avance de la sesión"
          aria-valuenow={completadas}
          aria-valuemin={0}
          aria-valuemax={totales}
        >
          <div
            className="progreso__relleno"
            style={{ width: `${totales ? (completadas / totales) * 100 : 0}%` }}
          />
        </div>
      </div>

      {descanso && (
        <CronometroDescanso
          key={descanso.sello}
          segundos={descanso.segundos}
          alSaltar={() => setDescanso(null)}
        />
      )}
      {confirmacion && <RespuestaAccion mensaje={confirmacion} />}

      {sesion.ejercicios.map((ejercicio) => (
        <BloqueEjercicio
          key={ejercicio.ejercicio_id}
          ejercicio={ejercicio}
          alVerTecnica={() => setEjercicioGuia(ejercicio)}
          filas={filas[ejercicio.ejercicio_id] ?? []}
          alCambiar={(indice, campo, valor) =>
            actualizarFila(ejercicio.ejercicio_id, indice, campo, valor)
          }
          alMarcar={(indice) => alternarHecha(ejercicio, indice)}
        />
      ))}

      {error && <AvisoDeError mensaje={error} />}

      {ejercicioGuia && <Hoja titulo={ejercicioGuia.nombre} descripcion="Consulta la técnica sin salir de tu sesión." alCerrar={cerrarGuia}>
        <LimiteRecurso key={ejercicioGuia.ejercicio_id} respaldo={<div className="pila-3"><p>No se pudo cargar la ficha visual. La descripción del catálogo sigue disponible:</p><p>{ejercicioGuia.descripcion || 'Consulta la técnica con quien te guía antes de realizar el ejercicio.'}</p></div>}><Suspense fallback={<p role="status">Cargando ficha…</p>}><FichaEjercicio ejercicio={ejercicioGuia} /></Suspense></LimiteRecurso>
      </Hoja>}

      <div className="pie-fijo no-imprimir">
        <button
          type="button"
          className="boton boton--principal"
          onClick={() => setHojaAbierta('esfuerzo')}
          disabled={completadas === 0}
        >
          Terminar y guardar {completadas} {completadas === 1 ? 'serie' : 'series'}
        </button>
        <p className="nota-al-pie centrado">Se guarda en este teléfono mientras entrena</p>
      </div>

      {hojaAbierta === 'esfuerzo' && (
        <Hoja
          titulo="¿Cómo le resultó la sesión?"
          descripcion="Sirve para distinguir un estancamiento por cansancio de uno por falta de estímulo: piden respuestas opuestas."
          alCerrar={cerrarEsfuerzo}
        >
          {error && <AvisoDeError mensaje={error} />}
          <div className="pila-3" aria-busy={guardando}>
          <div className="lista">
            {ESFUERZOS.map((opcion) => (
              <button
                key={opcion.valor}
                type="button"
                className={`lista__fila${
                  esfuerzo === opcion.valor ? ' lista__fila--seleccionada' : ''
                }`}
                onClick={() => setEsfuerzo(opcion.valor)}
                disabled={guardando}
                aria-pressed={esfuerzo === opcion.valor}
              >
                <span className="pila-2 crece">
                  <span className="lista__titulo">{opcion.etiqueta}</span>
                  <span className="lista__detalle">{opcion.detalle}</span>
                </span>
                {esfuerzo === opcion.valor && (
                  <Icono nombre="tick-02" tamano={18} className="tinta-acento" />
                )}
              </button>
            ))}
          </div>

          <label className="campo">
            <span className="campo__etiqueta">Notas (opcional)</span>
            <textarea
              className="campo__control"
              rows={2}
              maxLength={500}
              value={notas}
              disabled={guardando}
              onChange={(evento) => setNotas(evento.target.value)}
              placeholder="Por ejemplo: la máquina de pierna estaba ocupada, hice sentadilla."
            />
          </label>

          <button
            type="button"
            className="boton boton--principal"
            onClick={guardar}
            disabled={guardando}
          >
            {guardando ? 'Guardando…' : 'Guardar la sesión'}
          </button>
          </div>
        </Hoja>
      )}
    </div>
  )
}

function BloqueEjercicio({ ejercicio, filas, alCambiar, alMarcar, alVerTecnica }) {
  const { recomendacion } = ejercicio
  const primeraVez = recomendacion.decision === 'primera_vez'

  return (
    <div className="tarjeta tarjeta--densa">
      <div className="fila--entre fila--arriba">
        <div className="pila-2">
          <h2 className="titulo-ejercicio">{ejercicio.nombre}</h2>
          <p className="lista__detalle mono">
            {ejercicio.equipamiento} · {ejercicio.prescripcion}
          </p>
        </div>
        {recomendacion.carga_sugerida_kg !== null && (
          <div className="pila-2 a-la-derecha">
            <span className="cifra-media tinta-acento">{recomendacion.carga_sugerida_kg}</span>
            <span className="cifras__rotulo">kg sugerido</span>
          </div>
        )}
      </div>

      <p className={`aviso ${recomendacion.hay_incremento ? 'aviso--ok' : 'aviso--neutro'}`}>
        {recomendacion.hay_incremento && <span className="insignia-sube">SUBE</span>}
        {recomendacion.explicacion}
      </p>

      <button type="button" className="boton-texto" onClick={alVerTecnica} aria-label={`Ver técnica de ${ejercicio.nombre}`}>Ver técnica paso a paso ↗</button>

      <div className="pila-2">
        <div className="series series__encabezado">
          <span />
          <span>{ejercicio.duracion_segundos_min != null ? "Segundos" : "Reps"}</span>
          <span>kg extra</span>
          <span />
        </div>

        {filas.map((fila, indice) => (
          <FilaDeSerie
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

      <p className="nota-al-pie">El peso es la carga adicional. Registre 0 kg si trabaja solo con su peso corporal.</p>

      {ejercicio.ultima_vez.length > 0 && (
        <p className="nota-al-pie">
          El {fechaCorta(ejercicio.fecha_ultima_vez)}: {resumirSeries(ejercicio.ultima_vez)}
        </p>
      )}
    </div>
  )
}

function FilaDeSerie({ fila, indice, ejercicio, primeraVez, alCambiar, alMarcar }) {
  const identificador = `${ejercicio.ejercicio_id}-${fila.numero_serie}`

  return (
    <div className="series" data-hecha={fila.hecha}>
      <span className={`series__numero${fila.hecha ? ' series__numero--hecha' : ''}`}>
        {fila.numero_serie}
      </span>

      <span>
        <label className="solo-lectores" htmlFor={`reps-${identificador}`}>
          {ejercicio.duracion_segundos_min != null ? "Segundos" : "Repeticiones"} de la serie {fila.numero_serie} de {ejercicio.nombre}
        </label>
        <input
          id={`reps-${identificador}`}
          type="number"
          inputMode="numeric"
          min="0"
          max={ejercicio.duracion_segundos_min != null ? 3600 : 100}
          className={`series__campo${fila.hecha ? ' series__campo--hecha' : ''}`}
          value={ejercicio.duracion_segundos_min != null ? fila.duracion_segundos : fila.repeticiones}
          onChange={(evento) => alCambiar(indice, ejercicio.duracion_segundos_min != null ? 'duracion_segundos' : 'repeticiones', evento.target.value)}
        />
      </span>

      <span>
        <label className="solo-lectores" htmlFor={`peso-${identificador}`}>
          Peso adicional en kg de la serie {fila.numero_serie} de {ejercicio.nombre}
        </label>
        <input
          disabled={ejercicio.duracion_segundos_min != null}
          id={`peso-${identificador}`}
          type="number"
          inputMode="decimal"
          min="0"
          max="500"
          step="0.5"
          className={`series__campo${fila.hecha ? ' series__campo--hecha' : ''}`}
          value={fila.peso_kg}
          placeholder={primeraVez ? '—' : ''}
          onChange={(evento) => alCambiar(indice, 'peso_kg', evento.target.value)}
        />
      </span>

      <button
        type="button"
        className={`series__confirmar${fila.hecha ? ' series__confirmar--hecha' : ''}`}
        onClick={() => alMarcar(indice)}
        aria-pressed={fila.hecha}
        aria-label={`${fila.hecha ? 'Desmarcar' : 'Marcar'} la serie ${fila.numero_serie} de ${ejercicio.nombre}${fila.hecha ? '' : ' como hecha'}`}
      >
        <Icono nombre="tick-02" tamano={19} />
      </button>
    </div>
  )
}

/**
 * Resultado de la sesión.
 *
 * El servidor devuelve las progresiones en el mismo orden en que los ejercicios
 * aparecieron en las series enviadas, pero sin el nombre de cada ejercicio. Se
 * emparejan aquí con los nombres que se guardaron al enviar; si por lo que sea
 * las dos listas no coinciden en largo, se muestra la progresión sin nombre en
 * vez de arriesgar a ponerle el de otro ejercicio.
 */
function SesionGuardada({ resultado }) {
  const suben = resultado.progresiones
    .map((progresion, indice) => ({
      ...progresion,
      nombre:
        resultado.nombres?.length === resultado.progresiones.length
          ? resultado.nombres[indice]
          : null,
    }))
    .filter((progresion) => progresion.hay_incremento)

  const { recompensa } = resultado

  return (
    <div className="pila-5">
      <ResultadoAccion titulo="Sesión guardada">
        <p className="cuerpo">{resultado.mensaje}</p>
      </ResultadoAccion>

      <RecompensaAccion recompensa={recompensa} />

      {resultado.sesion.duracion_total_segundos > 0 && <p className="apoyo">Sostenes registrados: {resultado.sesion.duracion_total_segundos} segundos.</p>}
      <div className="cifras">
        <div className="cifras__columna">
          <span className="cifras__valor">{resultado.sesion.series_totales}</span>
          <span className="cifras__rotulo">{resultado.sesion.series_totales === 1 ? 'serie' : 'series'}</span>
        </div>
        <div className="cifras__columna">
          <span className="cifras__valor">{resultado.sesion.repeticiones_totales}</span>
          <span className="cifras__rotulo">reps</span>
        </div>
        <div className="cifras__columna">
          <span className="cifras__valor">{entero(resultado.sesion.volumen_kg)}</span>
          <span className="cifras__rotulo">kg</span>
        </div>
      </div>

      {suben.length > 0 && (
        <div className="tarjeta tarjeta--densa">
          <span className="rotulo">Para la próxima vez</span>
          <div className="lista lista--desnuda">
            {suben.map((progresion, indice) => (
              <div key={`${progresion.carga_sugerida_kg}-${indice}`} className="lista__fila">
                <span className="cuerpo crece">
                  {progresion.nombre ?? progresion.explicacion}
                </span>
                <span className="lista__valor tinta-ok">
                  {progresion.carga_previa_kg} → {progresion.carga_sugerida_kg} kg
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="pila-3">
        <Link to="/entrenar" className="boton boton--principal">
          Volver a mi semana
        </Link>
        <Link to="/avance/senda" className="boton boton--secundario">
          Ver mi senda
        </Link>
      </div>
    </div>
  )
}
