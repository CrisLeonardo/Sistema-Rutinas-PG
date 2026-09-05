/**
 * Cambio de contraseña.
 *
 * Vivía dentro de la pantalla de ajustes, compitiendo por el espacio con los
 * datos de la cuenta. Es una tarea con principio y final, no un ajuste que se
 * consulta: tiene pantalla propia y se llega a ella desde «Más».
 *
 * Las reglas y los mensajes son los mismos que verifica el servidor. Se
 * comprueban aquí solo para no hacer viajar una petición que ya se sabe que va
 * a fallar.
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import CabeceraPantalla from '../componentes/CabeceraPantalla.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioAcceso } from '../servicios/api.js'

const LONGITUD_MINIMA = 8

export default function CambioContrasena() {
  const { token, renovarSesion } = useSesion()
  const navegar = useNavigate()

  const [formulario, setFormulario] = useState({
    contrasena_actual: '',
    contrasena_nueva: '',
    confirmacion: '',
  })
  const [error, setError] = useState(null)
  const [exito, setExito] = useState(false)
  const [enviando, setEnviando] = useState(false)
  const [visible, setVisible] = useState(false)

  const actualizar = (evento) => {
    const { name, value } = evento.target
    setFormulario((anterior) => ({ ...anterior, [name]: value }))
    setError(null)
    setExito(false)
  }

  /** Reproduce en la interfaz las reglas que el servidor vuelve a verificar. */
  const validar = () => {
    const { contrasena_nueva: nueva, confirmacion } = formulario
    if (nueva.length < LONGITUD_MINIMA) {
      return `La contraseña nueva debe tener al menos ${LONGITUD_MINIMA} caracteres.`
    }
    if (!/[a-zA-ZáéíóúñÁÉÍÓÚÑ]/.test(nueva)) {
      return 'La contraseña debe incluir al menos una letra.'
    }
    if (!/\d/.test(nueva)) {
      return 'La contraseña debe incluir al menos un número.'
    }
    if (nueva !== confirmacion) {
      return 'La confirmación no coincide con la contraseña nueva.'
    }
    if (nueva === formulario.contrasena_actual) {
      return 'La contraseña nueva debe ser distinta de la actual.'
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

    setEnviando(true)
    setError(null)
    try {
      const respuesta = await servicioAcceso.cambiarContrasena(
        {
          contrasena_actual: formulario.contrasena_actual,
          contrasena_nueva: formulario.contrasena_nueva,
        },
        token,
      )
      // El servidor emite un token nuevo: sin adoptarlo, la sesión seguiría
      // atada al token con que el usuario entró antes del cambio.
      renovarSesion(respuesta)
      setFormulario({ contrasena_actual: '', contrasena_nueva: '', confirmacion: '' })
      setExito(true)
    } catch (fallo) {
      setError(fallo.message)
    } finally {
      setEnviando(false)
    }
  }

  const nueva = formulario.contrasena_nueva
  const cumpleRegla =
    nueva.length >= LONGITUD_MINIMA &&
    /[a-zA-ZáéíóúñÁÉÍÓÚÑ]/.test(nueva) &&
    /\d/.test(nueva)

  return (
    <div className="pila-5">
      <CabeceraPantalla titulo="Cambiar la contraseña" hacia="/mas" />

      <p className="cuerpo">
        Se le pide la contraseña actual aunque ya tenga la sesión abierta: así, un teléfono
        desatendido no basta para quedarse con su cuenta.
      </p>

      {exito && (
        <p className="aviso aviso--ok" role="status">
          Su contraseña se cambió. Úsela la próxima vez que inicie sesión.
        </p>
      )}

      {error && (
        <p className="aviso aviso--peligro" role="alert">
          {error}
        </p>
      )}

      <form onSubmit={enviar} noValidate className="pila-5">
        <div className="pila-3">
          <label className="campo">
            <span className="campo__etiqueta">Contraseña actual</span>
            <input
              name="contrasena_actual"
              type="password"
              className="campo__control"
              value={formulario.contrasena_actual}
              onChange={actualizar}
              autoComplete="current-password"
              required
            />
          </label>

          <div className="campo">
            <label className="campo__etiqueta" htmlFor="contrasena_nueva">
              Contraseña nueva
            </label>
            <span className="campo__envoltura">
              <input
                id="contrasena_nueva"
                name="contrasena_nueva"
                type={visible ? 'text' : 'password'}
                className="campo__control"
                value={formulario.contrasena_nueva}
                onChange={actualizar}
                autoComplete="new-password"
                required
              />
              <button
                type="button"
                className="campo__accion"
                onClick={() => setVisible((anterior) => !anterior)}
                aria-label="Mostrar la contraseña"
                aria-pressed={visible}
              >
                {visible ? 'Ocultar' : 'Ver'}
              </button>
            </span>
            <span className={`pista${cumpleRegla ? ' pista--cumplida' : ''}`}>
              <span className="pista__punto" />
              Al menos {LONGITUD_MINIMA} caracteres, con una letra y un número.
            </span>
          </div>

          <label className="campo">
            <span className="campo__etiqueta">Repita la contraseña nueva</span>
            <input
              name="confirmacion"
              type={visible ? 'text' : 'password'}
              className="campo__control"
              value={formulario.confirmacion}
              onChange={actualizar}
              autoComplete="new-password"
              required
            />
          </label>
        </div>

        <button type="submit" className="boton boton--principal" disabled={enviando}>
          {enviando ? 'Guardando…' : 'Cambiar mi contraseña'}
        </button>

        {exito && (
          <button type="button" className="boton boton--secundario" onClick={() => navegar('/mas')}>
            Volver
          </button>
        )}
      </form>
    </div>
  )
}
