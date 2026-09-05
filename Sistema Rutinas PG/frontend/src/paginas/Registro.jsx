import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import Icono from '../componentes/Icono.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioAcceso } from '../servicios/api.js'

const LONGITUD_MINIMA = 8

/**
 * Pantalla de registro de cuentas nuevas (historia HU-01).
 *
 * Se parte en dos pasos: tres campos primero, la confirmación después. Cuatro
 * campos seguidos en un teléfono obligan a desplazarse para ver el botón, y el
 * usuario llega al final sin saber si lo que escribió sirve.
 *
 * La regla de la contraseña se comprueba mientras se escribe: un punto que se
 * enciende dice más, y antes, que un mensaje de error después de enviar.
 */
export default function Registro() {
  const { iniciarSesion } = useSesion()
  const navegar = useNavigate()

  const [paso, setPaso] = useState(1)
  const [formulario, setFormulario] = useState({
    nombre: '',
    correo: '',
    contrasena: '',
    confirmacion: '',
  })
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [visible, setVisible] = useState(false)

  const actualizar = (evento) => {
    const { name, value } = evento.target
    setFormulario((anterior) => ({ ...anterior, [name]: value }))
    setError(null)
  }

  const contrasenaValida =
    formulario.contrasena.length >= LONGITUD_MINIMA &&
    /[a-zA-Z]/.test(formulario.contrasena) &&
    /\d/.test(formulario.contrasena)

  /** Reproduce en la interfaz las reglas que el servidor vuelve a verificar. */
  const validarPrimerPaso = () => {
    if (formulario.nombre.trim().length < 2) {
      return 'Escriba su nombre completo.'
    }
    if (formulario.contrasena.length < LONGITUD_MINIMA) {
      return `La contraseña debe tener al menos ${LONGITUD_MINIMA} caracteres.`
    }
    if (!/[a-zA-Z]/.test(formulario.contrasena) || !/\d/.test(formulario.contrasena)) {
      return 'La contraseña debe combinar letras y números.'
    }
    return null
  }

  const continuar = (evento) => {
    evento.preventDefault()
    const problema = validarPrimerPaso()
    if (problema) {
      setError(problema)
      return
    }
    setError(null)
    setPaso(2)
  }

  const enviar = async (evento) => {
    evento.preventDefault()
    if (formulario.contrasena !== formulario.confirmacion) {
      setError('Las contraseñas no coinciden.')
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
      // Si el registro falla, el paso 1 es donde están los datos que hay que
      // corregir: el correo repetido, el nombre demasiado corto.
      setPaso(1)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="entrada">
      <div className="pila-3">
        <div className="fila">
          {paso === 2 && (
            <button
              type="button"
              className="cabecera-pantalla__volver"
              onClick={() => setPaso(1)}
              aria-label="Volver"
            >
              <Icono nombre="arrow-left-01" tamano={20} />
            </button>
          )}
          <span className="apoyo mono">Paso {paso} de 2</span>
        </div>
        <h1 className="titulo-grande">Crear una cuenta</h1>
        <p className="apoyo">
          El registro es gratuito y le permite guardar sus planes y consultarlos cuando
          quiera.
        </p>
      </div>

      {error && (
        <p className="aviso aviso--peligro" role="alert">
          {error}
        </p>
      )}

      {paso === 1 ? (
        <form onSubmit={continuar} noValidate className="pila-5">
          <div className="pila-3">
            <label className="campo">
              <span className="campo__etiqueta">Nombre completo</span>
              <input
                name="nombre"
                type="text"
                className="campo__control"
                value={formulario.nombre}
                onChange={actualizar}
                autoComplete="name"
                required
              />
            </label>

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
              <span className={`pista${contrasenaValida ? ' pista--cumplida' : ''}`}>
                <span className="pista__punto" />8 caracteres, con una letra y un número
              </span>
            </div>
          </div>

          <button type="submit" className="boton boton--principal">
            Continuar
          </button>
        </form>
      ) : (
        <form onSubmit={enviar} noValidate className="pila-5">
          <label className="campo">
            <span className="campo__etiqueta">Repita la contraseña</span>
            <input
              name="confirmacion"
              type={visible ? 'text' : 'password'}
              className="campo__control"
              value={formulario.confirmacion}
              onChange={actualizar}
              autoComplete="new-password"
              required
              autoFocus
            />
          </label>

          <p className="nota-al-pie">
            Al crear su cuenta, sus medidas, su plan y su avance solo los ve usted. Ni el
            administrador del sistema tiene acceso a ellos.
          </p>

          <button type="submit" className="boton boton--principal" disabled={enviando}>
            {enviando ? 'Creando la cuenta…' : 'Registrarme'}
          </button>
        </form>
      )}

      <p className="apoyo centrado">
        ¿Ya tiene cuenta? <Link to="/acceso">Inicie sesión</Link>
      </p>
    </div>
  )
}
