/**
 * Tema claro y oscuro.
 *
 * Hasta ahora el tema lo decidía `prefers-color-scheme` y el usuario no podía
 * cambiarlo. La aplicación se usa en el gimnasio, donde la luz no es la misma
 * que la del teléfono en casa, así que la preferencia del sistema deja de ser
 * la última palabra: es solo el valor inicial. La elección explícita se guarda
 * en `localStorage` y se aplica como atributo `data-scheme` en `<html>`.
 *
 * El mismo cálculo vive duplicado en el script en línea de `index.html`, que se
 * ejecuta antes de que React monte para que la pantalla no aparezca primero en
 * claro y salte a oscuro un instante después.
 */

export const CLAVE_TEMA = 'rutinas.tema'

/** Tema guardado por el usuario, o el que prefiere su sistema operativo. */
export function leerTema() {
  try {
    const guardado = localStorage.getItem(CLAVE_TEMA)
    if (guardado === 'dark' || guardado === 'light') return guardado
  } catch {
    // Almacenamiento no disponible: se sigue con la preferencia del sistema.
  }

  const prefiereClaro =
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-color-scheme: light)').matches

  return prefiereClaro ? 'light' : 'dark'
}

/** Escribe el tema en el documento y lo recuerda para la próxima visita. */
export function aplicarTema(tema) {
  document.documentElement.setAttribute('data-scheme', tema)
  // La barra del navegador se pinta del mismo color que el fondo: en un
  // teléfono, una franja blanca sobre una pantalla oscura se nota.
  const meta = document.querySelector('meta[name="theme-color"]')
  if (meta) meta.setAttribute('content', tema === 'light' ? '#f4f4f6' : '#0a0a0d')

  try {
    localStorage.setItem(CLAVE_TEMA, tema)
  } catch {
    // Si no se puede guardar, el tema vale para esta visita y ya.
  }
}
