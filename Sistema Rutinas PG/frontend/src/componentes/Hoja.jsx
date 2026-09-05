/**
 * Hoja inferior.
 *
 * Sustituye a los desplegables y a los cuadros de diálogo de antes: las
 * alternativas de un alimento, la explicación de la progresión, el esfuerzo
 * percibido, la comparación de planes. Entra desde abajo porque es donde está
 * el pulgar, y deja ver el velo del fondo para que no se pierda el sitio desde
 * el que se abrió.
 *
 * Cierra con Escape y tocando el velo. Mientras está abierta, el fondo no se
 * desplaza: en un teléfono, arrastrar dentro de la hoja movía la pantalla de
 * atrás y se perdía la posición de lectura.
 */

import { useEffect, useRef } from 'react'

import Icono from './Icono.jsx'

export default function Hoja({ titulo, descripcion, alCerrar, children, pie }) {
  const panel = useRef(null)

  useEffect(() => {
    const alPulsarTecla = (evento) => {
      if (evento.key === 'Escape') alCerrar()
    }
    document.addEventListener('keydown', alPulsarTecla)

    const desbordeAnterior = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    // El foco entra en la hoja: quien navega con teclado no debería tener que
    // recorrer toda la pantalla de atrás para llegar a lo que acaba de abrir.
    panel.current?.focus()

    return () => {
      document.removeEventListener('keydown', alPulsarTecla)
      document.body.style.overflow = desbordeAnterior
    }
  }, [alCerrar])

  return (
    <>
      <div className="velo no-imprimir" onClick={alCerrar} aria-hidden="true" />
      <div
        className="hoja-inferior no-imprimir"
        role="dialog"
        aria-modal="true"
        aria-label={titulo}
        tabIndex={-1}
        ref={panel}
      >
        <span className="hoja-inferior__asa" />
        <div className="hoja-inferior__cabecera">
          <div className="pila-2">
            <h2 className="titulo-tarjeta">{titulo}</h2>
            {descripcion && <p className="apoyo">{descripcion}</p>}
          </div>
          <button
            type="button"
            className="boton boton--circular"
            onClick={alCerrar}
            aria-label="Cerrar"
          >
            <Icono nombre="cancel-01" tamano={18} />
          </button>
        </div>
        {children}
        {pie}
      </div>
    </>
  )
}
