/**
 * Preferencias de la aplicación: tema y vibración del cronómetro.
 *
 * No son datos del usuario —no viajan al servidor ni forman parte de su
 * plan—: son dos decisiones sobre cómo se comporta este teléfono. Viven en
 * `localStorage`, que sobrevive al cierre de la pestaña, y no en el
 * `sessionStorage` donde vive la sesión.
 *
 * El tema se aplica como atributo `data-scheme` en `<html>` para que baste con
 * redefinir las variables de tokens.css; la vibración la consulta el cronómetro
 * de descanso antes de pedirla.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

import { aplicarTema, leerTema } from '../utilidades/tema.js'

const CLAVE_VIBRACION = 'rutinas.vibracion'

const ContextoPreferencias = createContext(null)

/** La vibración está encendida salvo que el usuario la haya apagado. */
function leerVibracion() {
  try {
    return localStorage.getItem(CLAVE_VIBRACION) !== 'apagada'
  } catch {
    return true
  }
}

export function ProveedorPreferencias({ children }) {
  const [tema, setTema] = useState(leerTema)
  const [vibracion, setVibracion] = useState(leerVibracion)

  // El script en línea de index.html ya puso el atributo antes de que React
  // montara. Este efecto lo mantiene al día cuando el usuario lo cambia.
  useEffect(() => {
    aplicarTema(tema)
  }, [tema])

  const alternarTema = useCallback(() => {
    setTema((actual) => (actual === 'dark' ? 'light' : 'dark'))
  }, [])

  const alternarVibracion = useCallback(() => {
    setVibracion((actual) => {
      const siguiente = !actual
      try {
        localStorage.setItem(CLAVE_VIBRACION, siguiente ? 'encendida' : 'apagada')
      } catch {
        // Sin almacenamiento, la preferencia vale para esta visita.
      }
      return siguiente
    })
  }, [])

  const valor = useMemo(
    () => ({ tema, alternarTema, vibracion, alternarVibracion }),
    [tema, alternarTema, vibracion, alternarVibracion],
  )

  return <ContextoPreferencias.Provider value={valor}>{children}</ContextoPreferencias.Provider>
}

/** Acceso a las preferencias desde cualquier componente. */
export function usePreferencias() {
  const contexto = useContext(ContextoPreferencias)
  if (contexto === null) {
    throw new Error('usePreferencias debe utilizarse dentro de ProveedorPreferencias.')
  }
  return contexto
}
