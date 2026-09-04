/**
 * Navegación de la aplicación.
 *
 * Se resuelve en dos piezas porque los dos tamaños de pantalla se usan de forma
 * distinta. En computadora, la barra superior de siempre. En teléfono, una barra
 * inferior fija con los cinco destinos que se visitan a diario: el estudio del
 * Capítulo I encontró que el 72.2 % de la población accede desde un teléfono, y
 * en un teléfono el borde inferior es lo que el pulgar alcanza sin recolocar la
 * mano. El menú desplegable se conserva para el resto de los destinos.
 *
 * La sección para registrar el avance no aparecía en ninguna parte de la
 * navegación: la ruta existía y solo se alcanzaba escribiendo la dirección.
 */

import { Link, NavLink, useNavigate } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'
import {
  IconoAvance,
  IconoComer,
  IconoEntrenar,
  IconoEvolucion,
  IconoInicio,
} from './Iconos.jsx'

/** Destinos del uso diario. Son los que ocupan la barra inferior en teléfono. */
const DESTINOS_PRINCIPALES = [
  { ruta: '/panel', etiqueta: 'Inicio', Icono: IconoInicio },
  { ruta: '/menu', etiqueta: 'Comer', Icono: IconoComer },
  { ruta: '/rutina', etiqueta: 'Entrenar', Icono: IconoEntrenar },
  { ruta: '/progreso', etiqueta: 'Avance', Icono: IconoAvance },
  { ruta: '/reportes', etiqueta: 'Evolución', Icono: IconoEvolucion },
]

/** Destinos de consulta ocasional. Viven en el menú desplegable. */
const DESTINOS_SECUNDARIOS = [
  { ruta: '/bitacora', etiqueta: 'Mi bitácora' },
  { ruta: '/plan-nutricional', etiqueta: 'Mi plan' },
  { ruta: '/compras', etiqueta: 'Lista de compras' },
  { ruta: '/historial-medidas', etiqueta: 'Mis medidas' },
  { ruta: '/perfil-biometrico', etiqueta: 'Actualizar medidas' },
  { ruta: '/cuenta', etiqueta: 'Mi cuenta' },
]

const DESTINOS_ADMINISTRACION = [
  { ruta: '/catalogos', etiqueta: 'Catálogos' },
  { ruta: '/cuentas', etiqueta: 'Cuentas' },
]

export default function BarraNavegacion() {
  const { autenticado, esAdministrador, usuario, cerrarSesion } = useSesion()
  const navegar = useNavigate()

  const salir = () => {
    cerrarSesion()
    navegar('/acceso', { replace: true })
  }

  return (
    <>
      <nav className="navbar navbar-expand-lg navbar-dark barra-superior no-imprimir">
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
                  {/* En teléfono estos cinco ya están en la barra inferior, de
                      modo que el desplegable solo repite lo indispensable. */}
                  {DESTINOS_PRINCIPALES.map((destino) => (
                    <li className="nav-item d-none d-lg-block" key={destino.ruta}>
                      <NavLink className="nav-link" to={destino.ruta}>
                        {destino.etiqueta}
                      </NavLink>
                    </li>
                  ))}
                  {DESTINOS_SECUNDARIOS.map((destino) => (
                    <li className="nav-item d-lg-none" key={destino.ruta}>
                      <NavLink className="nav-link" to={destino.ruta}>
                        {destino.etiqueta}
                      </NavLink>
                    </li>
                  ))}

                  <li className="nav-item dropdown d-none d-lg-block">
                    <button
                      className="nav-link dropdown-toggle btn btn-link"
                      type="button"
                      data-bs-toggle="dropdown"
                      aria-expanded="false"
                    >
                      Más
                    </button>
                    <ul className="dropdown-menu">
                      {DESTINOS_SECUNDARIOS.map((destino) => (
                        <li key={destino.ruta}>
                          <NavLink className="dropdown-item" to={destino.ruta}>
                            {destino.etiqueta}
                          </NavLink>
                        </li>
                      ))}
                    </ul>
                  </li>

                  {esAdministrador &&
                    DESTINOS_ADMINISTRACION.map((destino) => (
                      <li className="nav-item" key={destino.ruta}>
                        <NavLink className="nav-link" to={destino.ruta}>
                          {destino.etiqueta}
                        </NavLink>
                      </li>
                    ))}
                </ul>

                <div className="d-flex flex-column flex-lg-row align-items-lg-center gap-2 py-2 py-lg-0">
                  <span className="text-white-50 small text-truncate">
                    {usuario?.correo}
                  </span>
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

      {autenticado && (
        <nav
          className="barra-inferior d-lg-none no-imprimir"
          aria-label="Navegación principal"
        >
          {DESTINOS_PRINCIPALES.map((destino) => (
            <NavLink
              key={destino.ruta}
              to={destino.ruta}
              className={({ isActive }) =>
                `destino-inferior ${isActive ? 'destino-activo' : ''}`
              }
            >
              <destino.Icono />
              <span className="etiqueta-destino">{destino.etiqueta}</span>
            </NavLink>
          ))}
        </nav>
      )}
    </>
  )
}
