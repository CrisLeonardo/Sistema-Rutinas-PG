/**
 * Bitácora y marcas.
 *
 * Reúne lo que el registro de cargas hace posible y que antes no existía: la
 * constancia semanal, la evolución de la carga en cada ejercicio y las marcas
 * personales. Es la pantalla que devuelve algo a cambio del esfuerzo de
 * registrar, y sin ella la bitácora sería un formulario que no sirve para nada.
 *
 * Se reparte en dos pestañas de la sección «Entrenar» porque son dos preguntas
 * distintas: «¿qué he hecho?» —las sesiones, en orden— y «¿cuánto he subido?»
 * —las marcas de cada ejercicio—. Antes ambas competían por la misma pantalla y
 * la segunda quedaba enterrada bajo la primera.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import AvisoDeError from '../componentes/AvisoDeError.jsx'
import GraficaLineas from '../componentes/GraficaLineas.jsx'
import Icono from '../componentes/Icono.jsx'
import Pildoras from '../componentes/Pildoras.jsx'
import { PESTANAS_ENTRENAR } from '../datos/secciones.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioEntrenamiento } from '../servicios/api.js'
import { conSigno, entero, fechaBreve } from '../utilidades/formatos.js'

export default function HistorialEntrenamiento({ vista = 'bitacora' }) {
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

  /** La primera marca se abre sola: la pantalla ya trae algo que enseñar. */
  const abrirEjercicio = useCallback(
    async (ejercicioId) => {
      setEjercicioAbierto(ejercicioId)
      setEvolucion(null)
      try {
        setEvolucion(await servicioEntrenamiento.consultarEjercicio(ejercicioId, token))
      } catch (fallo) {
        setError(fallo.message)
      }
    },
    [token],
  )

  const primeraMarca = resumen?.marcas?.[0]?.ejercicio_id ?? null

  useEffect(() => {
    if (primeraMarca !== null && ejercicioAbierto === null) abrirEjercicio(primeraMarca)
  }, [primeraMarca, ejercicioAbierto, abrirEjercicio])

  if (cargando) {
    return (
      <div className="pila" aria-busy="true">
        <div className="esqueleto esqueleto--titulo" />
        <div className="esqueleto esqueleto--fila" />
        <div className="esqueleto esqueleto--tarjeta" />
        <span className="solo-lectores">Cargando su bitácora…</span>
      </div>
    )
  }

  if (error && !resumen) return <AvisoDeError mensaje={error} alReintentar={cargar} />

  if (!resumen?.sesiones_totales) {
    return (
      <div className="vacio">
        <h1 className="vacio__titulo">Todavía no ha registrado ningún entrenamiento</h1>
        <p className="cuerpo">
          Cuando registre una sesión, el sistema empezará a llevarle la cuenta de sus cargas y
          le dirá cuándo subir de peso en cada ejercicio.
        </p>
        <Link to="/entrenar" className="boton boton--principal">
          Ir a mi rutina
        </Link>
      </div>
    )
  }

  const esMarcas = vista === 'marcas'

  return (
    <div className="pila">
      <div className="pila-2">
        <h1 className="titulo-pantalla">{esMarcas ? 'Mis marcas' : 'Mi bitácora'}</h1>
        <p className="apoyo">
          {esMarcas
            ? 'El peso más alto que ha movido en cada ejercicio.'
            : 'Lo que ha levantado y cómo ha subido'}
        </p>
      </div>

      <Pildoras etiquetaGrupo="Secciones de entrenamiento" opciones={PESTANAS_ENTRENAR} />

      {esMarcas ? (
        <Marcas
          marcas={resumen.marcas}
          abierto={ejercicioAbierto}
          evolucion={evolucion}
          alAbrir={abrirEjercicio}
        />
      ) : (
        <>
          <Cifras resumen={resumen} />
          {resumen.marcas.length > 0 && (
            <MarcaAbierta marca={resumen.marcas[0]} evolucion={evolucion} />
          )}
          <Sesiones sesiones={sesiones} />
        </>
      )}
    </div>
  )
}

function Cifras({ resumen }) {
  const cambio = resumen.cambio_volumen_porcentaje

  return (
    <div className="cifras">
      <div className="cifras__columna">
        <span className="cifras__valor">{resumen.racha_semanas}</span>
        <span className="cifras__rotulo">
          {resumen.racha_semanas === 1 ? 'semana de racha' : 'semanas de racha'}
        </span>
      </div>
      <div className="cifras__columna">
        <span className="cifras__valor">{entero(resumen.volumen_esta_semana_kg)}</span>
        <span className="cifras__rotulo">kg esta semana</span>
      </div>
      <div className="cifras__columna">
        <span
          className={`cifras__valor ${
            cambio === null || cambio === undefined
              ? ''
              : cambio >= 0
                ? 'tinta-ok'
                : 'tinta-peligro'
          }`}
        >
          {cambio === null || cambio === undefined ? '—' : `${conSigno(cambio, 0)} %`}
        </span>
        <span className="cifras__rotulo">vs. semana pasada</span>
      </div>
    </div>
  )
}

/** La evolución de la marca más reciente, abierta sin que haya que pedirla. */
function MarcaAbierta({ marca, evolucion }) {
  return (
    <div className="tarjeta tarjeta--densa">
      <div className="tarjeta__cabecera">
        <span className="rotulo">{marca.nombre}</span>
        {evolucion?.cambio_carga_kg !== null && evolucion?.cambio_carga_kg !== undefined && (
          <span className="apoyo mono tinta-ok">{conSigno(evolucion.cambio_carga_kg, 1)} kg</span>
        )}
      </div>
      {evolucion ? (
        <GraficaLineas
          puntos={evolucion.puntos.map((punto) => ({
            etiqueta: `${punto.fecha}T12:00:00`,
            valor: punto.carga_maxima_kg ?? 0,
          }))}
          etiquetaValor="kg"
          descripcion={`Evolución de la carga en ${evolucion.nombre}`}
        />
      ) : (
        <div className="esqueleto esqueleto--grafica" />
      )}
    </div>
  )
}

function Sesiones({ sesiones }) {
  return (
    <div className="pila-3">
      <span className="rotulo">Sesiones registradas</span>
      <div className="lista">
        {sesiones.map((sesion) => (
          <div key={sesion.id} className="lista__fila">
            <span className="pila-2 crece">
              <span className="lista__etiqueta">
                {sesion.nombre_grupo ?? 'Entrenamiento libre'}
              </span>
              <span className="lista__detalle mono">
                {fechaBreve(`${sesion.fecha}T12:00:00`)} · {sesion.series_totales} series
                {sesion.duracion_minutos ? ` · ${sesion.duracion_minutos} min` : ''}
              </span>
              {sesion.notas && <span className="cita">«{sesion.notas}»</span>}
            </span>
            <span className="lista__valor">{entero(sesion.volumen_kg)} kg</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function Marcas({ marcas, abierto, evolucion, alAbrir }) {
  if (marcas.length === 0) {
    return (
      <div className="vacio">
        <h2 className="vacio__titulo">Todavía no tiene marcas</h2>
        <p className="cuerpo">
          En cuanto registre una sesión con peso, aquí aparecerá lo más alto que ha movido en
          cada ejercicio.
        </p>
      </div>
    )
  }

  return (
    <div className="pila-3">
      <p className="apoyo">Toque un ejercicio para ver cómo ha ido cambiando.</p>

      {marcas.map((marca) => {
        const estaAbierta = abierto === marca.ejercicio_id
        return (
          <div key={marca.ejercicio_id} className="tarjeta tarjeta--densa">
            <button
              type="button"
              className="fila fila--arriba boton-plano"
              onClick={() => alAbrir(marca.ejercicio_id)}
              aria-expanded={estaAbierta}
            >
              <span className="pila-2 crece">
                <span className="lista__titulo">{marca.nombre}</span>
                <span className="lista__detalle mono">
                  {fechaBreve(`${marca.fecha}T12:00:00`)} · {marca.repeticiones_en_la_maxima}{' '}
                  repeticiones
                  {marca.repeticion_maxima_estimada_kg
                    ? ` · equivale a ${marca.repeticion_maxima_estimada_kg} kg a una repetición`
                    : ''}
                </span>
              </span>
              <span className="cifra-pequena">{marca.carga_maxima_kg} kg</span>
              <Icono
                nombre={estaAbierta ? 'arrow-up-01' : 'arrow-down-01'}
                tamano={17}
                className="tinta-4"
              />
            </button>

            {estaAbierta &&
              (evolucion ? (
                <>
                  <GraficaLineas
                    puntos={evolucion.puntos.map((punto) => ({
                      etiqueta: `${punto.fecha}T12:00:00`,
                      valor: punto.carga_maxima_kg ?? 0,
                    }))}
                    etiquetaValor="kg"
                    descripcion={`Evolución de la carga en ${evolucion.nombre}`}
                  />
                  <p className="nota-al-pie">
                    {evolucion.sesiones_registradas} sesiones registradas
                    {evolucion.cambio_carga_kg !== null &&
                      ` · ${conSigno(evolucion.cambio_carga_kg, 1)} kg desde la primera`}
                  </p>
                </>
              ) : (
                <div className="esqueleto esqueleto--grafica" />
              ))}
          </div>
        )
      })}
    </div>
  )
}
