import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'

/** Pantalla de inicio de sesión (historia HU-02). */
export default function Acceso() {
  const { iniciarSesion, expiroPorInactividad } = useSesion()
  const navegar = useNavigate()

  const [formulario, setFormulario] = useState({ correo: '', contrasena: '' })
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

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
    <div className="d-flex justify-content-center">
      <div className="card shadow-sm tarjeta-formulario">
        <div className="card-body p-4">
          <h1 className="h4 mb-1">Iniciar sesión</h1>
          <p className="texto-ayuda mb-4">
            Ingrese con la cuenta que registró para consultar sus planes.
          </p>

          {expiroPorInactividad && (
            <div className="alert alert-warning" role="alert">
              Su sesión se cerró automáticamente por inactividad.
            </div>
          )}

          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={enviar} noValidate>
            <div className="mb-3">
              <label className="form-label" htmlFor="correo">
                Correo electrónico
              </label>
              <input
                id="correo"
                name="correo"
                type="email"
                className="form-control form-control-lg control-tactil"
                value={formulario.correo}
                onChange={actualizar}
                autoComplete="email"
                required
              />
            </div>

            <div className="mb-4">
              <label className="form-label" htmlFor="contrasena">
                Contraseña
              </label>
              <input
                id="contrasena"
                name="contrasena"
                type="password"
                className="form-control form-control-lg control-tactil"
                value={formulario.contrasena}
                onChange={actualizar}
                autoComplete="current-password"
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-principal btn-lg w-100 control-tactil"
              disabled={enviando}
            >
              {enviando ? 'Verificando…' : 'Entrar'}
            </button>
          </form>

          <p className="text-center mt-4 mb-0">
            ¿Aún no tiene cuenta? <Link to="/registro">Regístrese aquí</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
