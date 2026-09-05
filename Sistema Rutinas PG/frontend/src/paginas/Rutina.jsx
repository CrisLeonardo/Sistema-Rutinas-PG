/**
 * «Mi semana»: la rutina de la semana (historia HU-07).
 *
 * El acordeón desaparece. Abrir un día para leer sus ejercicios y volver a
 * cerrarlo era un trabajo que la pantalla imponía sin necesidad: lo que se
 * quiere saber al abrirla es qué toca hoy, y eso ahora está arriba, en una
 * tarjeta con el botón que empieza la sesión. El resto de la semana es una
 * lista de filas, y tocar una lleva a esa sesión.
 *
 * Las explicaciones largas —cómo progresa la carga, por qué faltan grupos
 * musculares, el aviso de técnica y el reparto de series— pasan a la hoja
 * «Cómo progresar»: siguen estando, pero no entre el usuario y su sesión.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import AvisoDeError from '../componentes/AvisoDeError.jsx'
import Hoja from '../componentes/Hoja.jsx'
import Icono from '../componentes/Icono.jsx'
import Pildoras from '../componentes/Pildoras.jsx'
import { PESTANAS_ENTRENAR } from '../datos/secciones.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPlan, servicioRutina } from '../servicios/api.js'

const ETIQUETAS_NIVEL = {
  principiante: 'principiante',
  intermedio: 'intermedio',
  avanzado: 'avanzado',
}

/** Abreviatura de cada día, con lunes como 1: es como el sistema los numera. */
const DIAS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

function diaDeHoy() {
  const dia = new Date().getDay()
  return dia === 0 ? 7 : dia
}

/** La sesión de hoy; si hoy toca descanso, la siguiente que venga. */
function sesionAlFrente(sesiones, hoy) {
  const deHoy = sesiones.find((sesion) => sesion.dia === hoy)
  if (deHoy) return { sesion: deHoy, esHoy: true }

  const siguiente =
    sesiones.find((sesion) => sesion.dia > hoy) ??
    // Si ya no queda ninguna esta semana, la próxima es la primera de la que viene.
    sesiones[0]
  return siguiente ? { sesion: siguiente, esHoy: false } : { sesion: null, esHoy: false }
}

export default function Rutina() {
  const { token } = useSesion()

  const [rutina, setRutina] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [generando, setGenerando] = useState(false)
  const [error, setError] = useState(null)
  const [sinPerfil, setSinPerfil] = useState(false)
  const [hojaAbierta, setHojaAbierta] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      setRutina(await servicioRutina.consultarVigente(token))
      setError(null)
    } catch (fallo) {
      // No tener rutina todavía es el estado inicial, no un error.
      if (fallo instanceof ErrorApi && fallo.codigo === 404) {
        setRutina(null)
        setError(null)
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
      setHojaAbierta(null)
      await cargar()
    } catch (fallo) {
      if (fallo instanceof ErrorApi && fallo.codigo === 409) setSinPerfil(true)
      setError(fallo.message)
    } finally {
      setGenerando(false)
    }
  }

  if (cargando) {
    return (
      <div className="pila" aria-busy="true">
        <div className="esqueleto esqueleto--titulo" />
        <div className="esqueleto esqueleto--tarjeta" />
        <div className="esqueleto esqueleto--fila" />
        <div className="esqueleto esqueleto--fila" />
        <span className="solo-lectores">Cargando su rutina…</span>
      </div>
    )
  }

  if (error && !rutina) {
    return (
      <div className="pila">
        <AvisoDeError mensaje={error} alReintentar={cargar} />
        {sinPerfil && (
          <Link to="/avance/medidas/editar" className="boton boton--principal">
            Registrar mis medidas
          </Link>
        )}
      </div>
    )
  }

  if (!rutina) {
    return (
      <div className="vacio">
        <h1 className="vacio__titulo">Todavía no tiene rutina</h1>
        <p className="cuerpo">Su rutina se arma junto con su plan de alimentación.</p>
        <button
          type="button"
          className="boton boton--principal"
          onClick={generar}
          disabled={generando}
        >
          {generando ? 'Armando…' : 'Generar mi rutina'}
        </button>
      </div>
    )
  }

  const hoy = diaDeHoy()
  const { sesion: alFrente, esHoy } = sesionAlFrente(rutina.sesiones, hoy)
  const resto = rutina.sesiones.length
  const nivel = ETIQUETAS_NIVEL[rutina.nivel_experiencia] ?? rutina.nivel_experiencia

  // Los siete días, menos el que ya está en la tarjeta de arriba.
  const semana = DIAS.map((abreviatura, indice) => {
    const dia = indice + 1
    return {
      dia,
      abreviatura,
      sesion: rutina.sesiones.find((sesion) => sesion.dia === dia) ?? null,
    }
  }).filter((fila) => fila.sesion?.id !== alFrente?.id)

  return (
    <div className="pila">
      <div className="pila-2">
        <h1 className="titulo-pantalla">Mi semana</h1>
        <p className="apoyo">
          {resto} {resto === 1 ? 'sesión' : 'sesiones'} · nivel {nivel}
        </p>
      </div>

      <Pildoras etiquetaGrupo="Secciones de entrenamiento" opciones={PESTANAS_ENTRENAR} />

      {alFrente && (
        <div className="tarjeta tarjeta--destacada tarjeta--densa">
          <div className="fila--entre">
            <span className="chip chip--acento">
              {esHoy ? 'HOY' : 'SIGUIENTE'} · {DIAS[alFrente.dia - 1].toUpperCase()}
            </span>
            <span className="apoyo mono">{alFrente.duracion_estimada_minutos} min</span>
          </div>
          <div className="pila-2">
            <p className="titulo-grupo">{alFrente.nombre_grupo}</p>
            <p className="apoyo mono">
              {alFrente.ejercicios.length} ejercicios · {alFrente.series_totales} series
            </p>
          </div>
          <Link to={`/entrenar/${alFrente.id}`} className="boton boton--principal">
            Entrenar esta sesión
          </Link>
        </div>
      )}

      <div className="lista">
        {semana.map((fila) => {
          if (!fila.sesion) {
            return (
              <div key={fila.dia} className="lista__fila lista__fila--tenue">
                <span className="lista__dia">{fila.abreviatura}</span>
                <span className="apoyo crece">Descanso</span>
              </div>
            )
          }
          return (
            <Link key={fila.dia} to={`/entrenar/${fila.sesion.id}`} className="lista__fila">
              <span className="lista__dia">{fila.abreviatura}</span>
              <span className="pila-2 crece">
                <span className="lista__etiqueta">{fila.sesion.nombre_grupo}</span>
                <span className="lista__detalle mono">
                  {fila.sesion.ejercicios.length} ejercicios ·{' '}
                  {fila.sesion.duracion_estimada_minutos} min
                </span>
              </span>
              <Icono nombre="arrow-right-01" tamano={17} className="lista__chevron" />
            </Link>
          )
        })}
      </div>

      {rutina.cumple_separacion_de_grupos && (
        <p className="aviso aviso--ok">Ningún músculo se entrena dos días seguidos.</p>
      )}

      {error && <AvisoDeError mensaje={error} />}

      <button type="button" className="boton-texto" onClick={() => setHojaAbierta('progresar')}>
        Cómo progresar
      </button>

      {hojaAbierta === 'progresar' && (
        <Hoja titulo="Cómo progresar" alCerrar={() => setHojaAbierta(null)}>
          <p className="cuerpo">{rutina.explicacion_progresion}</p>

          {rutina.explicacion_grupos_ausentes && (
            <div className="pila-2">
              <h3 className="rotulo">Por qué no aparecen todos los músculos</h3>
              <p className="cuerpo">{rutina.explicacion_grupos_ausentes}</p>
            </div>
          )}

          <div className="pila-2">
            <h3 className="rotulo">Series por músculo en la semana</h3>
            <div className="lista">
              {Object.entries(rutina.series_efectivas_por_grupo).map(([grupo, series]) => (
                <div key={grupo} className="lista__fila">
                  <span className="lista__etiqueta crece">{grupo}</span>
                  <span className="lista__valor">{series}</span>
                </div>
              ))}
            </div>
          </div>

          <p className="nota-al-pie">{rutina.aviso_tecnica}</p>

          <button
            type="button"
            className="boton boton--secundario"
            onClick={generar}
            disabled={generando}
          >
            {generando ? 'Armando…' : 'Volver a armar'}
          </button>
        </Hoja>
      )}
    </div>
  )
}
