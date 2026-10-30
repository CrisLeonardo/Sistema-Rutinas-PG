/**
 * Cronómetro de descanso entre series.
 *
 * El descanso prescrito —dos minutos en los ejercicios compuestos— es parte de
 * la dosis, no una pausa cualquiera: acortarlo cambia el estímulo. Hasta ahora
 * la pantalla lo declaraba en texto y dejaba que el usuario lo midiera por su
 * cuenta, que en la práctica significa no medirlo.
 *
 * Arranca solo al confirmar una serie y se puede saltar. Al terminar avisa con
 * una vibración corta, porque en un gimnasio con música un sonido no se escucha
 * y la pantalla suele estar apagada. La vibración se puede apagar desde «Más»:
 * no todos los teléfonos la hacen igual de discreta.
 *
 * Ocupa el ancho de la pantalla en acento pleno: es lo único que hay que mirar
 * mientras dura, y se queda pegado arriba para seguir a la vista al recorrer la
 * sesión.
 */

import { useEffect, useRef, useState } from 'react'

import { usePreferencias } from '../contexto/ContextoPreferencias.jsx'
import { segundosRestantes } from '../interaccion/respuestas.mjs'

function comoReloj(segundos) {
  const minutos = Math.floor(segundos / 60)
  const resto = segundos % 60
  return `${minutos}:${String(resto).padStart(2, '0')}`
}

export default function CronometroDescanso({ segundos, alTerminar, alSaltar }) {
  const { vibracion } = usePreferencias()
  const [restante, setRestante] = useState(segundos)
  const avisos = useRef({ vibracion, alTerminar })
  avisos.current = { vibracion, alTerminar }

  useEffect(() => {
    const venceEn = Date.now() + Math.max(segundos, 0) * 1000
    let avisado = false
    let temporizador
    const actualizar = () => {
      const siguiente = segundosRestantes(venceEn)
      setRestante(siguiente)
      if (siguiente === 0 && !avisado) {
        avisado = true
        clearInterval(temporizador)
        if (avisos.current.vibracion && !document.hidden) {
          try { navigator.vibrate?.([200, 100, 200]) } catch { /* El texto permanece. */ }
        }
        avisos.current.alTerminar?.()
      }
    }
    actualizar()
    if (segundos > 0) temporizador = setInterval(actualizar, 250)
    document.addEventListener('visibilitychange', actualizar)
    return () => {
      clearInterval(temporizador)
      document.removeEventListener('visibilitychange', actualizar)
    }
  }, [segundos])

  const terminado = restante <= 0

  return (
    <>
    <div
      className={`cronometro${terminado ? ' cronometro--terminado' : ''}`}
      role="timer"
      aria-live="off"
    >
      <div className="pila-2">
        <span className="cronometro__rotulo">
          {terminado ? 'Descanso terminado' : 'Descanso'}
        </span>
        <span className="cronometro__cifra">{comoReloj(Math.max(restante, 0))}</span>
      </div>
      <button type="button" className="cronometro__boton" onClick={alSaltar}>
        {terminado ? 'Listo' : 'Saltar'}
      </button>
      <span className="solo-lectores">
        {terminado ? 'El descanso terminó.' : `Quedan ${restante} segundos de descanso.`}
      </span>
    </div>
    <p className="solo-lectores" role="status">{terminado ? 'Descanso terminado. Puede continuar con su siguiente serie.' : ''}</p>
    </>
  )
}
