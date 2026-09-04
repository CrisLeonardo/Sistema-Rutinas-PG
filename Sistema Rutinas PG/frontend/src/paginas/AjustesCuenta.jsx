/**
 * Ajustes de la cuenta.
 *
 * Reúne lo que el usuario puede hacer sobre su propia cuenta. Hasta ahora no
 * había ninguna pantalla para esto: una contraseña comprometida no tenía
 * remedio dentro del sistema, y la única salida era pedirle al administrador
 * que desactivara la cuenta.
 */

import { useState } from 'react'

import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioAcceso } from '../servicios/api.js'

const LONGITUD_MINIMA = 8

function fechaLegible(valor) {
  if (!valor) return 'Sin registro'
  return new Date(valor).toLocaleString('es-GT', { dateStyle: 'long', timeStyle: 'short' })
}

export default function AjustesCuenta() {
  const { usuario, token, esAdministrador, renovarSesion } = useSesion()

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

  return (
    <div className="row g-4">
      <div className="col-12">
        <h1 className="h3 mb-1">Ajustes de la cuenta</h1>
        <p className="texto-ayuda mb-0">Sus datos de acceso y su contraseña.</p>
      </div>

      <div className="col-12 col-lg-5">
        <div className="card shadow-sm h-100">
          <div className="card-body">
            <h2 className="h5 card-title">Sus datos</h2>
            <dl className="row mb-0 mt-3">
              <dt className="col-5">Nombre</dt>
              <dd className="col-7">{usuario?.nombre}</dd>

              <dt className="col-5">Correo</dt>
              <dd className="col-7 text-break">{usuario?.correo}</dd>

              <dt className="col-5">Tipo de cuenta</dt>
              <dd className="col-7">
                <span
                  className={`badge ${esAdministrador ? 'bg-warning text-dark' : 'bg-success'}`}
                >
                  {esAdministrador ? 'Administrador' : 'Usuario deportista'}
                </span>
              </dd>

              <dt className="col-5">Registro</dt>
              <dd className="col-7">{fechaLegible(usuario?.fecha_registro)}</dd>

              <dt className="col-5">Último acceso</dt>
              <dd className="col-7 mb-0">{fechaLegible(usuario?.ultimo_acceso)}</dd>
            </dl>
            <p className="texto-ayuda mt-3 mb-0">
              Sus medidas, su plan y su avance solo los ve usted. Ni el administrador
              del sistema tiene acceso a ellos.
            </p>
          </div>
        </div>
      </div>

      <div className="col-12 col-lg-7">
        <div className="card shadow-sm h-100">
          <div className="card-body">
            <h2 className="h5 card-title">Cambiar la contraseña</h2>
            <p className="texto-ayuda">
              Se le pide la contraseña actual aunque ya tenga la sesión abierta: así, un
              teléfono desatendido no basta para quedarse con su cuenta.
            </p>

            {exito && (
              <div className="alert alert-success" role="status">
                Su contraseña se cambió. Úsela la próxima vez que inicie sesión.
              </div>
            )}

            {error && (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            )}

            <form onSubmit={enviar} noValidate>
              <div className="mb-3">
                <label className="form-label" htmlFor="contrasena_actual">
                  Contraseña actual
                </label>
                <input
                  id="contrasena_actual"
                  name="contrasena_actual"
                  type="password"
                  className="form-control form-control-lg control-tactil"
                  value={formulario.contrasena_actual}
                  onChange={actualizar}
                  autoComplete="current-password"
                  required
                />
              </div>

              <div className="mb-3">
                <label className="form-label" htmlFor="contrasena_nueva">
                  Contraseña nueva
                </label>
                <input
                  id="contrasena_nueva"
                  name="contrasena_nueva"
                  type={visible ? 'text' : 'password'}
                  className="form-control form-control-lg control-tactil"
                  value={formulario.contrasena_nueva}
                  onChange={actualizar}
                  autoComplete="new-password"
                  aria-describedby="ayuda-contrasena"
                  required
                />
                <div id="ayuda-contrasena" className="form-text">
                  Al menos {LONGITUD_MINIMA} caracteres, con una letra y un número.
                </div>
              </div>

              <div className="mb-3">
                <label className="form-label" htmlFor="confirmacion">
                  Repita la contraseña nueva
                </label>
                <input
                  id="confirmacion"
                  name="confirmacion"
                  type={visible ? 'text' : 'password'}
                  className="form-control form-control-lg control-tactil"
                  value={formulario.confirmacion}
                  onChange={actualizar}
                  autoComplete="new-password"
                  required
                />
              </div>

              <div className="form-check mb-4 opcion-tactil">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="ver-contrasena"
                  checked={visible}
                  onChange={() => setVisible((anterior) => !anterior)}
                />
                <label className="form-check-label" htmlFor="ver-contrasena">
                  Mostrar la contraseña
                </label>
              </div>

              <button
                type="submit"
                className="btn btn-principal btn-lg w-100 control-tactil"
                disabled={enviando}
              >
                {enviando ? 'Guardando…' : 'Cambiar mi contraseña'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
