import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'
import CabeceraCuenta from '../componentes/MarcaProducto.jsx'
import { useConexion } from '../componentes/EstadoConexion.jsx'
import { conexion } from '../servicios/conexion.mjs'

/**
 * Pantalla de inicio de sesión (historia HU-02).
 *
 * Dos campos y una acción. Nada de tarjeta con sombra sobre fondo gris: la
 * pantalla entera es el formulario, centrada verticalmente, con la marca arriba
 * para saber dónde se está antes de escribir nada.
 *
 * Comparte la comprobación iniciada al abrir Senda y envía las credenciales una
 * sola vez cuando la API responde. Una espera por sí sola no prueba suspensión.
 */

export default function Acceso() {
  const { iniciarSesion, expiroPorInactividad } = useSesion()
  const navegar = useNavigate()

  const [formulario, setFormulario] = useState({ correo: '', contrasena: '' })
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [visible, setVisible] = useState(false)
  const { fase } = useConexion()

  const actualizar = (evento) => {
    const { name, value } = evento.target
    setFormulario((anterior) => ({ ...anterior, [name]: value }))
  }

  const enviar = async (evento) => {
    evento.preventDefault()
    setError(null)
    setEnviando(true)
    try {
      if (!await conexion.comprobar()) return
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
    <div className="entrada cuenta-senda">
      <CabeceraCuenta />
      <div className="pila-5">
        <p className="rotulo">SU SIGUIENTE PASO EMPIEZA AQUÍ</p>
        <h1 className="titulo-grande">Qué gusto volver.</h1>
        <p className="apoyo">Entre para ver qué le toca hoy: entrenar, comer y seguir avanzando.</p>
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

      <form onSubmit={enviar} className="pila-5" aria-busy={enviando}>
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
                aria-label={visible ? 'Ocultar la contraseña' : 'Ver la contraseña'}
                aria-pressed={visible}
              >
                {visible ? 'Ocultar' : 'Ver'}
              </button>
            </span>
          </div>
        </div>

        <button type="submit" className="boton boton--principal" disabled={enviando}>
          {enviando && <span className="carga-boton" aria-hidden="true" />}
          {enviando ? fase === 'conectando' ? 'Conectando…' : 'Verificando…' : 'Entrar a mi día'}
        </button>
        <p className="acceso-conexion" role="status"><span className={`conexion-indicador${fase === 'conectando' ? ' conexion-indicador--espera' : ''}`} aria-hidden="true" />{fase === 'disponible' ? 'Senda está disponible' : fase === 'sin-conexion' ? 'Conexión pendiente · puede volver a intentar' : 'Preparando la conexión mientras escribe'}</p>
      </form>

      <p className="apoyo centrado"><Link to="/recuperar-acceso">Olvidé mi contraseña</Link></p>

      <p className="apoyo centrado">
        ¿Aún no tiene cuenta? <Link to="/registro">Regístrese</Link>
      </p>
      <p className="nota-al-pie centrado"><Link to="/privacidad">Privacidad</Link> · <Link to="/ayuda">Ayuda</Link></p>
    </div>
  )
}
