/**
 * Píldoras de pestaña de una sección.
 *
 * Sustituyen a las pantallas sueltas: «Comer» y «Entrenar» agrupan tres
 * destinos cada una y la píldora dice en cuál se está sin obligar a volver
 * atrás para cambiar. La activa se deduce de la ruta, no de un estado propio:
 * así el botón de retroceso del navegador y un enlace directo dejan la pestaña
 * correcta marcada.
 */

import { Link, useLocation } from 'react-router-dom'

export default function Pildoras({ etiquetaGrupo, opciones }) {
  const { pathname } = useLocation()

  return (
    <div className="pildoras no-imprimir" role="tablist" aria-label={etiquetaGrupo}>
      {opciones.map((opcion) => {
        const activa = pathname === opcion.ruta
        return (
          <Link
            key={opcion.ruta}
            to={opcion.ruta}
            role="tab"
            aria-selected={activa}
            className={`pildora${activa ? ' pildora--activa' : ''}`}
          >
            {opcion.etiqueta}
          </Link>
        )
      })}
    </div>
  )
}
