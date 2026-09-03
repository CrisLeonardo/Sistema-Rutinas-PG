import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioAcceso } from '../servicios/api.js'

const LONGITUD_MINIMA = 8

/** Pantalla de registro de cuentas nuevas (historia HU-01). */
export default function Registro() {
  const { iniciarSesion } = useSesion()
  const navegar = useNavigate()

  const [formulario, setFormulario] = useState({
    nombre: '',
    correo: '',
    contrasena: '',
    confirmacion: '',
  })
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  const actualizar = (evento) => {
    const { name, value } = evento.target
    setFormulario((anterior) => ({ ...anterior, [name]: value }))
  }

  /** Reproduce en la interfaz las reglas que el servidor vuelve a verificar. */
  const validar = () => {
    if (formulario.nombre.trim().length < 2) {
      return 'Escriba su nombre completo.'
    }
    if (formulario.contrasena.length < LONGITUD_MINIMA) {
      return `La contraseña debe tener al menos ${LONGITUD_MINIMA} caracteres.`
    }
    if (!/[a-zA-Z]/.test(formulario.contrasena) || !/\d/.test(formulario.contrasena)) {
      return 'La contraseña debe combinar letras y números.'
    }
    if (formulario.contrasena !== formulario.confirmacion) {
      return 'Las contraseñas no coinciden.'
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
    const credenciales = {
      correo: formulario.correo.trim(),
      contrasena: formulario.contrasena,
    }
    try {
      await servicioAcceso.registrar({ ...credenciales, nombre: formulario.nombre.trim() })
      // Se abre la sesión de inmediato para que el usuario continúe sin volver
      // a escribir sus credenciales.
      await iniciarSesion(credenciales)
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
          <h1 className="h4 mb-1">Crear una cuenta</h1>
          <p className="texto-ayuda mb-4">
            El registro es gratuito y le permite guardar sus planes y consultarlos cuando
            quiera.
          </p>

          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={enviar} noValidate>
            <div className="mb-3">
              <label className="form-label" htmlFor="nombre">
                Nombre completo
              </label>
              <input
                id="nombre"
                name="nombre"
                type="text"
                className="form-control form-control-lg control-tactil"
                value={formulario.nombre}
                onChange={actualizar}
                autoComplete="name"
                required
              />
            </div>

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

            <div className="mb-3">
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
                autoComplete="new-password"
                required
              />
              <div className="form-text">
                Mínimo {LONGITUD_MINIMA} caracteres, combinando letras y números.
              </div>
            </div>

            <div className="mb-4">
              <label className="form-label" htmlFor="confirmacion">
                Repita la contraseña
              </label>
              <input
                id="confirmacion"
                name="confirmacion"
                type="password"
                className="form-control form-control-lg control-tactil"
                value={formulario.confirmacion}
                onChange={actualizar}
                autoComplete="new-password"
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-principal btn-lg w-100 control-tactil"
              disabled={enviando}
            >
              {enviando ? 'Creando la cuenta…' : 'Registrarme'}
            </button>
          </form>

          <p className="text-center mt-4 mb-0">
            ¿Ya tiene cuenta? <Link to="/acceso">Inicie sesión</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
