/**
 * Armazón de la administración.
 *
 * Es la única sección que no es de teléfono. El administrador trabaja sentado,
 * con teclado y ratón, y necesita ver muchas filas a la vez: una tabla de
 * ciento cuarenta alimentos en una columna de 390 px no es una tabla, es una
 * lista infinita.
 *
 * Barra lateral de 244 px con los dos destinos de administración, barra
 * superior con el título y la acción de la pantalla, y una subbarra opcional
 * de pestañas. Por debajo de 900 px la barra lateral se oculta —lo resuelve la
 * hoja de estilos— y la navegación vuelve a la barra inferior de siempre.
 */

import { Link, useLocation } from 'react-router-dom'

import Icono from './Icono.jsx'
import { IconoComer } from './Iconos.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { iniciales } from '../utilidades/formatos.js'

const DESTINOS = [
  { ruta: '/admin/catalogos', etiqueta: 'Catálogos' },
  { ruta: '/admin/cuentas', etiqueta: 'Cuentas' },
]

export default function ArmazonAdmin({ titulo, explicacion, accion, subbarra, children }) {
  const { pathname } = useLocation()
  const { usuario } = useSesion()

  return (
    <div className="admin">
      <aside className="admin__lateral no-imprimir">
        <div className="pila-2">
          <Link to="/panel" className="admin__marca">
            <span className="admin__marca-cuadro" aria-hidden="true">
              P
            </span>
            <span className="lista__etiqueta">Planes y Rutinas</span>
          </Link>
        </div>

        <nav className="pila-2" aria-label="Administración">
          {DESTINOS.map((destino) => (
            <Link
              key={destino.ruta}
              to={destino.ruta}
              className={`admin__enlace${
                pathname === destino.ruta ? ' admin__enlace--activo' : ''
              }`}
              aria-current={pathname === destino.ruta ? 'page' : undefined}
            >
              {destino.ruta.endsWith('catalogos') ? (
                <IconoComer tamano={16} grosor={1.8} />
              ) : (
                <Icono nombre="user" tamano={17} />
              )}
              <span>{destino.etiqueta}</span>
            </Link>
          ))}
        </nav>

        <div className="admin__cuenta empuja">
          <span className="admin__cuenta-avatar" aria-hidden="true">
            {iniciales(usuario?.nombre)}
          </span>
          <span className="pila-2">
            <span className="admin__cuenta-nombre">{usuario?.nombre}</span>
            <span className="cifras__rotulo">Administrador</span>
          </span>
        </div>
      </aside>

      <div className="admin__cuerpo">
        <header className="admin__barra-superior">
          <h1 className="titulo-admin">{titulo}</h1>
          {explicacion && <p className="apoyo admin__explicacion">{explicacion}</p>}
          {accion}
        </header>

        {subbarra && <div className="admin__subbarra no-imprimir">{subbarra}</div>}

        <div className="admin__contenido">{children}</div>
      </div>
    </div>
  )
}
