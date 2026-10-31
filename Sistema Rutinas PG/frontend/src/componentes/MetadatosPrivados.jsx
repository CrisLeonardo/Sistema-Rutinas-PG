import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

export default function MetadatosPrivados() {
  const { pathname } = useLocation()
  useEffect(() => {
    const titulos = { '/panel': 'Mi día', '/acceso': 'Entrar', '/registro': 'Crear cuenta', '/bienvenida': 'Primeros pasos', '/comer': 'Mi menú', '/comer/semana': 'Mis comidas de la semana', '/comer/recetas': 'Recetas', '/comer/preferencias': 'Mis restricciones alimentarias', '/comer/compras': 'Mis compras', '/comer/plan': 'Mi plan', '/entrenar': 'Mi rutina', '/entrenar/bitacora': 'Mis sesiones', '/entrenar/marcas': 'Mis marcas', '/avance': 'Registrar mi avance', '/avance/senda': 'Mi senda', '/avance/evolucion': 'Mi evolución', '/avance/medidas': 'Mis medidas', '/avance/medidas/editar': 'Mis medidas', '/avance/informes': 'Mis informes', '/recuperar-acceso': 'Recuperar acceso', '/restablecer-acceso': 'Restablecer acceso' }
    const cuentaYAdmin = { '/mas/contrasena': 'Cambiar mi contraseña', '/admin/catalogos': 'Administrar catálogos', '/admin/cuentas': 'Administrar cuentas', '/admin/informes': 'Informes de administración' }
    const titulo = titulos[pathname] ?? cuentaYAdmin[pathname] ?? (pathname.startsWith('/entrenar/biblioteca') ? 'Guías de ejercicios' : /^\/entrenar\/\d+/.test(pathname) ? 'Mi entrenamiento' : 'Mi cuenta')
    document.title = `Senda · ${titulo}`
    const robots = document.querySelector('meta[name="robots"]')
    if (robots) robots.content = 'noindex, nofollow'
  }, [pathname])
  return null
}
