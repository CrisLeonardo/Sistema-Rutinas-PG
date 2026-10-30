import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export default function MetadatosPrivados() {
  const { pathname } = useLocation()
  useEffect(() => {
    document.title = 'Senda · Mi cuenta'
    const robots = document.querySelector('meta[name="robots"]')
    if (robots) robots.content = 'noindex, nofollow'
  }, [pathname])
  return null
}
