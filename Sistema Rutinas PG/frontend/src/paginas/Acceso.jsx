import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'

/**
 * Pantalla de inicio de sesión (historia HU-02).
 *
 * Dos campos y una acción. Nada de tarjeta con sombra sobre fondo gris: la
 * pantalla entera es el formulario, centrada verticalmente, con la marca arriba
 * para saber dónde se está antes de escribir nada.
 *
 * Lleva un aviso que aparece cuando la verificación se alarga. El despliegue
 * gratuito duerme el servicio tras un rato sin tráfico, y el primer acceso del
 * día paga el arranque: sin el aviso, el botón se queda en «Verificando…» y no
 * hay forma de distinguir un servidor que despierta de una aplicación colgada.
 */

/** Segundos tras los cuales la espera deja de parecer normal y se explica. */
const SEGUNDOS_PARA_AVISAR = 6
export default function Acceso() {
  const { iniciarSesion, expiroPorInactividad } = useSesion()
  const navegar = useNavigate()

  const [formulario, setFormulario] = useState({ correo: '', contrasena: '' })
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [visible, setVisible] = useState(false)
  const [tardando, setTardando] = useState(false)

  useEffect(() => {
    if (!enviando) {
      setTardando(false)
      return undefined
    }
    const reloj = setTimeout(() => setTardando(true), SEGUNDOS_PARA_AVISAR * 1000)
    return () => clearTimeout(reloj)
  }, [enviando])

  const actualizar = (evento) => {
    const { name, value } = evento.target
    setFormulario((anterior) => ({ ...anterior, [name]: value }))
  }

  const enviar = async (evento) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      await iniciarSesion({
        correo: formulario.correo.trim(),
        contrasena: formulario.contrasena,
      })
      navegar('/panel', { replace: true })
    } catch (fallo) {
      setError(fallo.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="entrada">
      <div className="pila-5">
        <img src="/pwa-192x192.png" alt="" className="marca" />
        <h1 className="titulo-grande">Entrar</h1>
        <p className="apoyo">Ingrese con la cuenta que registró para consultar sus planes.</p>
      </div>

      {expiroPorInactividad && (
        <p className="aviso aviso--aviso" role="alert">
          Su sesión se cerró automáticamente por inactividad.
        </p>
      )}

      {error && (
        <p className="aviso aviso--peligro" role="alert">
          {error}
        </p>
      )}

      {enviando && tardando && (
        <p className="aviso aviso--neutro" role="status">
          El servidor está iniciando. El primer acceso tras un rato sin uso puede
          tardar hasta medio minuto.
        </p>
      )}

      <form onSubmit={enviar} noValidate className="pila-5">
        <div className="pila-3">
          <label className="campo">
            <span className="campo__etiqueta">Correo electrónico</span>
            <input
              name="correo"
              type="email"
              className="campo__control"
              value={formulario.correo}
              onChange={actualizar}
              autoComplete="email"
              required
            />
          </label>

          <div className="campo">
            <label className="campo__etiqueta" htmlFor="contrasena">
              Contraseña
            </label>
            <span className="campo__envoltura">
              <input
                id="contrasena"
                name="contrasena"
                type={visible ? 'text' : 'password'}
                className="campo__control"
                value={formulario.contrasena}
                onChange={actualizar}
                autoComplete="current-password"
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
          </div>
        </div>

        <button type="submit" className="boton boton--principal" disabled={enviando}>
          {enviando ? 'Verificando…' : 'Entrar'}
        </button>
      </form>

      <p className="apoyo centrado">
        ¿Aún no tiene cuenta? <Link to="/registro">Regístrese</Link>
      </p>
    </div>
  )
}
