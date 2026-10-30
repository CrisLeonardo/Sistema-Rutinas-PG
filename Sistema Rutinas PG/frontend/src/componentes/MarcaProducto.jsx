import { Link } from 'react-router-dom'
import { usePreferencias } from '../contexto/ContextoPreferencias.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import SimboloCamino from './SimboloCamino.jsx'

// Nombre y símbolo Camino elegidos por el autor; comunes al sitio y al sistema.
export function NombreSenda() {
  return <span className="marca-producto"><SimboloCamino /><span className="nombre-senda">senda<span aria-hidden="true">.</span></span></span>
}

export function CambiarTema() {
  const { tema, alternarTema } = usePreferencias()
  return <button type="button" className="cambiar-tema" onClick={alternarTema} aria-label={tema === 'dark' ? 'Activar modo claro' : 'Activar modo oscuro'}>{tema === 'dark' ? '☀' : '☾'}<span>{tema === 'dark' ? 'Claro' : 'Oscuro'}</span></button>
}

export default function CabeceraCuenta() {
  const { autenticado } = useSesion()
  return <div className="cabecera-cuenta"><Link to={autenticado ? '/panel' : '/'} aria-label={autenticado ? 'Senda, ir a mi día' : 'Senda, ir al inicio'}><NombreSenda /></Link><CambiarTema /></div>
}
