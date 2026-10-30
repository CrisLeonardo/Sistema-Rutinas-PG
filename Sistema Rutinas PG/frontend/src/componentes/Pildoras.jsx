/**
 * Píldoras de pestaña de una sección.
 *
 * Sustituyen a las pantallas sueltas: «Comer» y «Entrenar» agrupan tres
 * destinos cada una y la píldora dice en cuál se está sin obligar a volver
 * atrás para cambiar. La activa se deduce de la ruta, no de un estado propio:
 * así el botón de retroceso del navegador y un enlace directo dejan la pestaña
 * correcta marcada.
 *
 * Cuando las píldoras no caben —«Avance» tiene cinco— la fila se desplaza en
 * horizontal, y la activa se lleva a la vista al abrir la pantalla: de otro
 * modo, en un teléfono estrecho la última pestaña quedaría marcada pero fuera
 * del borde, y el usuario no sabría en cuál está.
 */

import { useEffect, useRef } from 'react'
import { Link, useLocation } from 'react-router-dom'

export default function Pildoras({ etiquetaGrupo, opciones }) {
  const { pathname } = useLocation()
  const activa = useRef(null)

  useEffect(() => {
    activa.current?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' })
  }, [pathname])

  return (
    <div className="pildoras no-imprimir" role="tablist" aria-label={etiquetaGrupo}>
      {opciones.map((opcion) => {
        const esActiva = pathname === opcion.ruta
        return (
          <Link
            key={opcion.ruta}
            ref={esActiva ? activa : undefined}
            to={opcion.ruta}
            role="tab"
            aria-selected={esActiva}
            className={`pildora${esActiva ? ' pildora--activa' : ''}`}
          >
            {opcion.etiqueta}
          </Link>
        )
      })}
    </div>
  )
}
