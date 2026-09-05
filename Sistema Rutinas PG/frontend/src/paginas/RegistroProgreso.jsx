/**
 * Anotar el avance de la semana (historia HU-09).
 *
 * El formulario es corto a propósito: se llena cada semana, de modo que pedir
 * mucho lo convertiría en una carga y el usuario dejaría de registrar. Solo el
 * peso es obligatorio.
 *
 * El campo de número deja paso a un control físico: la cifra grande y dos
 * botones de 52 px que suben y bajan de 0.1 en 0.1. El peso de una semana a
 * otra cambia por décimas, y corregir décimas con el teclado del teléfono —abrir
 * el teclado numérico, borrar, escribir— es más trabajo que dar cuatro toques.
 * La cifra sigue siendo un campo: al tocarla se puede escribir el valor entero.
 *
 * Tras guardar, la pantalla explica qué hizo el sistema con el plan, para que el
 * reajuste no ocurra en silencio.
 */

import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import AvisoDeError from '../componentes/AvisoDeError.jsx'
import Icono from '../componentes/Icono.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPerfil, servicioProgreso } from '../servicios/api.js'
import { conSigno, fechaLarga } from '../utilidades/formatos.js'

const PESO_MINIMO = 30
const PESO_MAXIMO = 250
const PERIMETRO_MINIMO = 40
const PERIMETRO_MAXIMO = 200
const PASO_KG = 0.1

/** Sesiones que se pueden reportar en una semana, como en el selector anterior. */
const SESIONES = [0, 1, 2, 3, 4, 5, 6, 7]

function hoyEnTextoLocal() {
  const ahora = new Date()
  const desplazamiento = ahora.getTimezoneOffset() * 60_000
  return new Date(ahora.getTime() - desplazamiento).toISOString().slice(0, 10)
}

/** Redondea a una décima: la suma de flotantes deja colas de decimales. */
function aDecimas(valor) {
  return Math.round(valor * 10) / 10
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
  const [anterior, setAnterior] = useState(null)
  const [cinturaVisible, setCinturaVisible] = useState(false)
  const [fechaVisible, setFechaVisible] = useState(false)

  const campoPeso = useRef(null)

  // Se precarga el peso de la última medición para que el usuario solo tenga
  // que corregirlo, en lugar de escribirlo desde cero cada semana.
  useEffect(() => {
    let vigente = true
    servicioPerfil
      .consultarVigente(token)
      .then((perfil) => {
        if (vigente) {
          setFormulario((valores) => ({ ...valores, peso_kg: String(perfil.peso_kg) }))
          setAnterior({ peso_kg: perfil.peso_kg, fecha: perfil.fecha_registro })
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
    setFormulario((valores) => ({ ...valores, [name]: value }))
    setError(null)
  }

  const ajustarPeso = (delta) => {
    setFormulario((valores) => {
      const actual = Number(valores.peso_kg) || 0
      const siguiente = Math.min(Math.max(aDecimas(actual + delta), PESO_MINIMO), PESO_MAXIMO)
      return { ...valores, peso_kg: siguiente.toFixed(1) }
    })
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
      window.scrollTo({ top: 0, behavior: 'smooth' })
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
      <AvanceRegistrado
        resultado={resultado}
        alRegistrarOtro={() => {
          setResultado(null)
          navegar('/avance', { replace: true })
        }}
      />
    )
  }

  const cambio =
    anterior && formulario.peso_kg !== ''
      ? aDecimas(Number(formulario.peso_kg) - anterior.peso_kg)
      : null

  return (
    <div className="pila-5">
      <div className="fila--entre">
        <div className="pila-2">
          <h1 className="titulo-pantalla">Su peso de hoy</h1>
          <p className="apoyo">Pésese siempre a la misma hora, de preferencia en ayunas.</p>
        </div>
        <button
          type="button"
          className="boton-texto"
          onClick={() => setFechaVisible((visible) => !visible)}
          aria-expanded={fechaVisible}
        >
          {formulario.fecha_registro === hoyEnTextoLocal()
            ? 'Hoy'
            : fechaLarga(`${formulario.fecha_registro}T12:00:00`)}
        </button>
      </div>

      {fechaVisible && (
        <label className="campo">
          <span className="campo__etiqueta">Fecha del registro</span>
          <input
            name="fecha_registro"
            type="date"
            max={hoyEnTextoLocal()}
            className="campo__control"
            value={formulario.fecha_registro}
            onChange={actualizar}
          />
        </label>
      )}

      {error && (
        <div className="pila-3">
          <AvisoDeError mensaje={error} />
          {sinPlan && (
            <Link to="/comer/plan" className="boton boton--secundario">
              Generar mi plan
            </Link>
          )}
        </div>
      )}

      <form onSubmit={enviar} noValidate className="pila-5">
        <div className="tarjeta tarjeta--protagonista control-peso">
          <div className="cifra-con-unidad">
            <input
              ref={campoPeso}
              name="peso_kg"
              type="number"
              inputMode="decimal"
              step={PASO_KG}
              min={PESO_MINIMO}
              max={PESO_MAXIMO}
              className="control-peso__cifra"
              value={formulario.peso_kg}
              onChange={actualizar}
              aria-label="Peso de hoy, en kilogramos"
              required
            />
            <span className="apoyo">kg</span>
          </div>

          <div className="control-peso__mandos">
            <button
              type="button"
              className="control-peso__boton"
              onClick={() => ajustarPeso(-PASO_KG)}
              aria-label="Bajar una décima de kilogramo"
            >
              −
            </button>
            <span className="control-peso__paso mono">{PASO_KG.toFixed(1)} kg</span>
            <button
              type="button"
              className="control-peso__boton"
              onClick={() => ajustarPeso(PASO_KG)}
              aria-label="Subir una décima de kilogramo"
            >
              +
            </button>
          </div>

          {cambio !== null && cambio !== 0 && (
            <span className={`chip ${cambio < 0 ? 'chip--ok' : 'chip--neutro'} mono`}>
              {conSigno(cambio, 1)} kg desde el {fechaLarga(anterior.fecha)}
            </span>
          )}
        </div>

        <div className="pila-3">
          <div className="fila--entre">
            <span className="lista__titulo">¿Qué tanto siguió su plan de comidas?</span>
            <span className="cifra-pequena tinta-acento">
              {formulario.adherencia_nutricional} %
            </span>
          </div>
          <input
            name="adherencia_nutricional"
            type="range"
            min="0"
            max="100"
            step="5"
            className="deslizador"
            value={formulario.adherencia_nutricional}
            onChange={actualizar}
            aria-label="Qué tanto siguió su plan de comidas"
          />
          <p className="campo__ayuda">
            Sea honesto: el sistema usa este dato para saber si el plan está funcionando o si
            el problema fue el cumplimiento.
          </p>
        </div>

        <div className="pila-3">
          <span className="lista__titulo">Sesiones de entrenamiento que completó</span>
          <div className="opciones-rejilla">
            {SESIONES.map((cantidad) => (
              <button
                key={cantidad}
                type="button"
                className={`opcion-boton mono${
                  Number(formulario.sesiones_cumplidas) === cantidad
                    ? ' opcion-boton--seleccionada'
                    : ''
                }`}
                onClick={() =>
                  setFormulario((valores) => ({
                    ...valores,
                    sesiones_cumplidas: String(cantidad),
                  }))
                }
                aria-pressed={Number(formulario.sesiones_cumplidas) === cantidad}
              >
                {cantidad}
              </button>
            ))}
          </div>
        </div>

        {cinturaVisible ? (
          <label className="campo">
            <span className="campo__etiqueta">Cintura, en centímetros</span>
            <input
              name="perimetro_cintura_cm"
              type="number"
              inputMode="decimal"
              step="0.5"
              min={PERIMETRO_MINIMO}
              max={PERIMETRO_MAXIMO}
              className="campo__control campo__control--numero"
              value={formulario.perimetro_cintura_cm}
              onChange={actualizar}
              autoFocus
            />
            <span className="campo__ayuda">Mida a la altura del ombligo, sin apretar la cinta.</span>
          </label>
        ) : (
          <button
            type="button"
            className="fila-punteada"
            onClick={() => setCinturaVisible(true)}
          >
            <span className="apoyo">Cintura, en centímetros</span>
            <span className="boton-texto">Agregar</span>
          </button>
        )}

        <button type="submit" className="boton boton--principal" disabled={enviando}>
          {enviando ? 'Guardando…' : 'Guardar mi avance'}
        </button>
      </form>
    </div>
  )
}

/** Resultado del reajuste: el plan no cambia en silencio. */
function AvanceRegistrado({ resultado, alRegistrarOtro }) {
  return (
    <div className="pila-5">
      <div className="resultado">
        <span className="resultado__circulo">
          <Icono nombre="tick-02" tamano={24} />
        </span>
        <h1 className="titulo-grande">Avance registrado</h1>
      </div>

      <p className={`aviso ${resultado.reajusto_el_plan ? 'aviso--ok' : 'aviso--neutro'}`} role="status">
        <strong>
          {resultado.reajusto_el_plan ? 'Su plan se actualizó' : 'Su plan sigue igual'}
        </strong>
        <br />
        {resultado.motivo}
      </p>

      <p className="cuerpo">{resultado.recomendacion}</p>

      {resultado.ritmo_semanal_kg !== null && (
        <div className="cifras">
          <div className="cifras__columna">
            <span className="cifras__valor">{conSigno(resultado.cambio_peso_kg, 1)} kg</span>
            <span className="cifras__rotulo">desde el registro anterior</span>
          </div>
          <div className="cifras__columna">
            <span className="cifras__valor">{conSigno(resultado.ritmo_semanal_kg, 2)} kg</span>
            <span className="cifras__rotulo">por semana</span>
          </div>
        </div>
      )}

      <div className="pila-3">
        <Link to="/avance/evolucion" className="boton boton--principal">
          Ver mi evolución
        </Link>
        {resultado.reajusto_el_plan && (
          <Link to="/comer/plan" className="boton boton--secundario">
            Ver mi plan actualizado
          </Link>
        )}
        <button type="button" className="boton-texto centrado" onClick={alRegistrarOtro}>
          Registrar otro avance
        </button>
      </div>
    </div>
  )
}
