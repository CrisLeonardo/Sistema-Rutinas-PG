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
import { vibracionHabilitada } from '../interaccion/respuestas.mjs'

const CLAVE_VIBRACION = 'rutinas.vibracion'

const ContextoPreferencias = createContext(null)

/** Se activa únicamente después de elegirla expresamente. */
function leerVibracion() {
  try {
    return vibracionHabilitada(localStorage.getItem(CLAVE_VIBRACION))
  } catch {
    return false
  }
}

export function ProveedorPreferencias({ children }) {
  const [tema, setTema] = useState(leerTema)
  const [vibracion, setVibracion] = useState(leerVibracion)
  const [reducirMovimiento, setReducirMovimiento] = useState(() => {
    try { return localStorage.getItem('senda.movimiento') === 'reducido' } catch { return false }
  })
  useEffect(() => {
    document.documentElement.dataset.movimiento = reducirMovimiento ? 'reducido' : 'normal'
    try { localStorage.setItem('senda.movimiento', reducirMovimiento ? 'reducido' : 'normal') } catch { /* Preferencia de esta visita. */ }
    window.dispatchEvent(new Event('senda:movimiento'))
  }, [reducirMovimiento])
  const alternarMovimiento = useCallback(() => setReducirMovimiento(actual => !actual), [])

  // El script en línea de index.html ya puso el atributo antes de que React
  // montara. Este efecto lo mantiene al día cuando el usuario lo cambia.
  useEffect(() => {
    aplicarTema(tema)
  }, [tema])

  const alternarTema = useCallback(() => {
    setTema((actual) => (actual === 'dark' ? 'light' : 'dark'))
  }, [])

  const elegirTema = useCallback((siguiente) => {
    if (siguiente === 'light' || siguiente === 'dark') setTema(siguiente)
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
    () => ({ tema, elegirTema, alternarTema, vibracion, alternarVibracion, reducirMovimiento, alternarMovimiento }),
    [tema, elegirTema, alternarTema, vibracion, alternarVibracion, reducirMovimiento, alternarMovimiento],
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
