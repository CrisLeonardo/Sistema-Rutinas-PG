import { Link, NavLink, useNavigate } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'

/** Barra superior con la navegación disponible según el rol de la cuenta. */
export default function BarraNavegacion() {
  const { autenticado, esAdministrador, usuario, cerrarSesion } = useSesion()
  const navegar = useNavigate()

  const salir = () => {
    cerrarSesion()
    navegar('/acceso', { replace: true })
  }

  return (
    <nav className="navbar navbar-expand-md navbar-dark barra-superior">
      <div className="container">
        <Link className="navbar-brand marca-sistema" to="/">
          Planes y Rutinas
        </Link>

        {autenticado && (
          <>
            <button
              className="navbar-toggler control-tactil"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#menu-principal"
              aria-controls="menu-principal"
              aria-expanded="false"
              aria-label="Mostrar u ocultar el menú"
            >
              <span className="navbar-toggler-icon" />
            </button>

            <div className="collapse navbar-collapse" id="menu-principal">
              <ul className="navbar-nav me-auto">
                <li className="nav-item">
                  <NavLink className="nav-link" to="/panel">
                    Mi panel
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/historial-medidas">
                    Mis medidas
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/plan-nutricional">
                    Mi plan
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/menu">
                    Qué comer
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/rutina">
                    Mi rutina
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink className="nav-link" to="/reportes">
                    Mi evolución
                  </NavLink>
                </li>
                {esAdministrador && (
                  <>
                    <li className="nav-item">
                      <NavLink className="nav-link" to="/catalogos">
                        Catálogos
                      </NavLink>
                    </li>
                    <li className="nav-item">
                      <NavLink className="nav-link" to="/cuentas">
                        Cuentas
                      </NavLink>
                    </li>
                  </>
                )}
              </ul>

              <div className="d-flex flex-column flex-md-row align-items-md-center gap-2 py-2 py-md-0">
                <span className="text-white-50 small">{usuario?.correo}</span>
                <button
                  type="button"
                  className="btn btn-outline-light btn-sm control-tactil"
                  onClick={salir}
                >
                  Cerrar sesión
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </nav>
  )
}
