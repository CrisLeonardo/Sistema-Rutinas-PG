/**
 * Navegación de la aplicación.
 *
 * Una sola barra de cinco destinos, fija en el borde inferior en todos los
 * tamaños de pantalla. El estudio del Capítulo I encontró que el 72.2 % de la
 * población accede desde un teléfono, y en un teléfono el borde inferior es lo
 * que el pulgar alcanza sin recolocar la mano. Desde 1025 px la misma barra se
 * pasa arriba —eso lo resuelve la hoja de estilos— porque en una pantalla
 * grande el borde inferior ya no es el sitio donde se mira.
 *
 * Las dieciséis rutas sueltas de antes se agrupan en cinco secciones: lo que
 * antes obligaba a recordar una dirección ahora está a un toque. El destino
 * central, «Hoy», sobresale de la barra: es la pantalla que se abre a diario.
 *
 * La barra desaparece durante la sesión de entrenamiento, que es modo enfoque,
 * y mientras no hay sesión iniciada.
 */

import { Link, useLocation } from 'react-router-dom'

import Icono from './Icono.jsx'
import { IconoAvance, IconoComer, IconoEntrenar, IconoInicio } from './Iconos.jsx'

/** Los cinco destinos, en el orden en que se dibujan. */
const DESTINOS = [
  { ruta: '/comer', etiqueta: 'Comer', Icono: IconoComer, prefijos: ['/comer'] },
  { ruta: '/entrenar', etiqueta: 'Entrenar', Icono: IconoEntrenar, prefijos: ['/entrenar'] },
  { ruta: '/panel', etiqueta: 'HOY', Icono: IconoInicio, prefijos: ['/panel'], centro: true },
  { ruta: '/avance', etiqueta: 'Avance', Icono: IconoAvance, prefijos: ['/avance'] },
  { ruta: '/mas', etiqueta: 'Más', hugeicon: 'more-horizontal', prefijos: ['/mas', '/admin'] },
]

/** Una ruta pertenece a la sección si es la sección o cuelga de ella. */
function perteneceA(ruta, prefijos) {
  return prefijos.some((prefijo) => ruta === prefijo || ruta.startsWith(`${prefijo}/`))
}

export default function BarraNavegacion() {
  const { pathname } = useLocation()

  return (
    <nav className="barra-navegacion no-imprimir" aria-label="Navegación principal">
      {DESTINOS.map((destino) => {
        const activo = perteneceA(pathname, destino.prefijos)

        if (destino.centro) {
          return (
            <Link
              key={destino.ruta}
              to={destino.ruta}
              className="barra-navegacion__destino barra-navegacion__destino--centro"
              aria-current={activo ? 'page' : undefined}
            >
              <span className="barra-navegacion__circulo">
                <destino.Icono tamano={20} grosor={2} />
                <span className="barra-navegacion__circulo-texto">{destino.etiqueta}</span>
              </span>
            </Link>
          )
        }

        return (
          <Link
            key={destino.ruta}
            to={destino.ruta}
            className={`barra-navegacion__destino${
              activo ? ' barra-navegacion__destino--activo' : ''
            }`}
            aria-current={activo ? 'page' : undefined}
          >
            {destino.hugeicon ? (
              <Icono nombre={destino.hugeicon} tamano={22} />
            ) : (
              <destino.Icono tamano={22} grosor={activo ? 2 : 1.8} />
            )}
            <span className="barra-navegacion__etiqueta">{destino.etiqueta}</span>
          </Link>
        )
      })}
    </nav>
  )
}
