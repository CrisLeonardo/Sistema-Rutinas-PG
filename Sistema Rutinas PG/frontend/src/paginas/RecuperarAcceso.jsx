import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import CabeceraCuenta from '../componentes/MarcaProducto.jsx'
import { servicioAcceso } from '../servicios/api.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'

export default function RecuperarAcceso({ restablecer = false }) {
  const { cerrarSesion } = useSesion()
  const [token] = useState(() => new URLSearchParams(window.location.hash.slice(1)).get('token') || '')
  const [correo, setCorreo] = useState('')
  const [clave, setClave] = useState('')
  const [confirmacion, setConfirmacion] = useState('')
  const [opciones, setOpciones] = useState(null)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [intento, setIntento] = useState(0)
  useEffect(() => {
    if (restablecer) {
      // Se retira el secreto de la barra y de la entrada actual del historial.
      // No se persiste en sessionStorage/localStorage ni en la URL de una petición.
      window.history.replaceState(window.history.state, '', window.location.pathname + window.location.search)
      return undefined
    }
    let vigente = true
    setError('')
    servicioAcceso.opcionesPublicas().then(datos => { if (vigente) setOpciones(datos) }).catch(() => { if (vigente) setError('No se pudo consultar la disponibilidad del correo. Puede volver a consultar sin salir de esta pantalla.') })
    return () => { vigente = false }
  }, [restablecer, intento])
  async function enviar(evento) {
    evento.preventDefault()
    setError('')
    if (restablecer && clave !== confirmacion) { setError('Las contraseñas no coinciden.'); return }
    setEnviando(true)
    try {
      const respuesta = restablecer
        ? await servicioAcceso.restablecer({ token, contrasena_nueva: clave })
        : await servicioAcceso.recuperar({ correo: correo.trim() })
      setMensaje(respuesta.mensaje)
      if (restablecer) cerrarSesion()
      setClave('')
      setConfirmacion('')
    } catch (fallo) { setError(fallo.message) }
    finally { setEnviando(false) }
  }
  const sinToken = restablecer && !/^[A-Za-z0-9_-]{43,128}$/.test(token)
  return <div className="entrada cuenta-senda"><CabeceraCuenta /><div className="pila-3"><p className="rotulo">TU CUENTA / SENDA</p><h1 className="titulo-grande">{restablecer ? 'Elige una nueva contraseña' : 'Recupera tu acceso'}</h1><p className="apoyo">{restablecer ? 'El enlace se puede usar una sola vez. Al cambiar la contraseña se cerrarán las sesiones anteriores.' : 'Te enviaremos un enlace al correo de tu cuenta. No necesitas compartir tu contraseña con nadie.'}</p></div>
    {error && <p className="aviso aviso--peligro" role="alert">{error}</p>}
    {!restablecer && !opciones && error && <button type="button" className="boton boton--secundario" onClick={() => setIntento(n => n + 1)}>Volver a consultar</button>}
    {mensaje ? <div className="pila-5"><p className="aviso aviso--neutro" role="status">{mensaje}</p><Link className="boton boton--principal" to="/acceso">Volver al acceso</Link></div> : sinToken ? <div className="pila-3"><p className="aviso aviso--aviso">Abre el enlace completo que recibiste por correo. Si recargaste esta página, vuelve a abrirlo desde el mensaje.</p><Link to="/recuperar-acceso">Solicitar un enlace nuevo</Link></div> : <>
      {!restablecer && opciones && !opciones.recuperacion_habilitada && <p className="aviso aviso--aviso" role="status">La recuperación por correo todavía no está disponible. Consulta los canales de <Link to="/ayuda">ayuda</Link>.</p>}
      <form onSubmit={enviar} className="pila-5">
        {restablecer ? <><label className="campo"><span className="campo__etiqueta">Contraseña nueva</span><input className="campo__control" type="password" autoComplete="new-password" value={clave} onChange={e => setClave(e.target.value)} minLength={8} maxLength={72} required /><span className="apoyo">Al menos 8 caracteres, con letras y números; sin espacios al inicio o final.</span></label><label className="campo"><span className="campo__etiqueta">Repite la contraseña nueva</span><input className="campo__control" type="password" autoComplete="new-password" value={confirmacion} onChange={e => setConfirmacion(e.target.value)} required /></label></> : <label className="campo"><span className="campo__etiqueta">Correo electrónico</span><input className="campo__control" type="email" autoComplete="email" value={correo} onChange={e => setCorreo(e.target.value)} maxLength={120} required /></label>}
        <button type="submit" className="boton boton--principal" disabled={enviando || (!restablecer && !opciones?.recuperacion_habilitada)}>{enviando ? 'Procesando…' : restablecer ? 'Guardar nueva contraseña' : 'Enviar enlace'}</button>
      </form>
    </>}
    <p className="apoyo centrado"><Link to="/acceso">Volver a entrar</Link> · <Link to="/ayuda">Necesito ayuda</Link></p>
  </div>
}
