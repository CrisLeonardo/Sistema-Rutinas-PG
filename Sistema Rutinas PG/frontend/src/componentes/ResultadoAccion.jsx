import { useEffect, useRef } from 'react'

export function enfocarResultado(elemento) {
  elemento?.focus({ preventScroll: true })
  window.scrollTo({ top: 0, behavior: 'instant' })
}

/** El resultado recibe foco después de guardar, sin esperar la animación. */
export default function ResultadoAccion({ titulo, children }) {
  const cabecera = useRef(null)
  useEffect(() => { enfocarResultado(cabecera.current) }, [])
  return <header className="resultado resultado-accion">
    <span className="resultado__circulo" aria-hidden="true">✓</span>
    <h1 className="titulo-resultado" tabIndex={-1} ref={cabecera}>{titulo}</h1>
    {children}
  </header>
}
