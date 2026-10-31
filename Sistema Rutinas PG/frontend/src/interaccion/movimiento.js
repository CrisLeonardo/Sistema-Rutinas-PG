import { useEffect, useState } from 'react'

export function movimientoReducido() {
  return (typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches)
    || (typeof document !== 'undefined' && document.documentElement.dataset.movimiento === 'reducido')
}

export function useMovimientoReducido() {
  const [reducido, setReducido] = useState(movimientoReducido)
  useEffect(() => {
    const medio = matchMedia('(prefers-reduced-motion: reduce)')
    const actualizar = () => setReducido(movimientoReducido())
    actualizar()
    medio.addEventListener('change', actualizar)
    window.addEventListener('senda:movimiento', actualizar)
    return () => { medio.removeEventListener('change', actualizar); window.removeEventListener('senda:movimiento', actualizar) }
  }, [])
  return reducido
}
