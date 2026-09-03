import { Navigate } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'

/**
 * Impide el acceso a las pantallas internas sin sesión activa.
 *
 * Es un refuerzo de la experiencia de uso: la comprobación determinante se
 * realiza en el servidor, conforme al requerimiento no funcional 4.5.1.
 */
export default function RutaProtegida({ children, soloAdministrador = false }) {
  const { autenticado, esAdministrador } = useSesion()

  if (!autenticado) {
    return <Navigate to="/acceso" replace />
  }

  if (soloAdministrador && !esAdministrador) {
    return (
      <div className="alert alert-warning" role="alert">
        Esta sección está reservada a las cuentas con rol de administrador.
      </div>
    )
  }

  return children
}
