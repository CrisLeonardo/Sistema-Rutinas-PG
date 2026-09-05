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

function comoReloj(segundos) {
  const minutos = Math.floor(segundos / 60)
  const resto = segundos % 60
  return `${minutos}:${String(resto).padStart(2, '0')}`
}

export default function CronometroDescanso({ segundos, alTerminar, alSaltar }) {
  const { vibracion } = usePreferencias()
  const [restante, setRestante] = useState(segundos)
  const avisado = useRef(false)

  useEffect(() => {
    setRestante(segundos)
    avisado.current = false
  }, [segundos])

  useEffect(() => {
    if (restante <= 0) return undefined
    const temporizador = setTimeout(() => setRestante((valor) => valor - 1), 1000)
    return () => clearTimeout(temporizador)
  }, [restante])

  useEffect(() => {
    if (restante > 0 || avisado.current) return
    avisado.current = true
    if (vibracion) {
      // La vibración es opcional: el escritorio no la implementa y algunos
      // navegadores la exigen tras una interacción del usuario.
      try {
        navigator.vibrate?.([200, 100, 200])
      } catch {
        // Sin vibración, el aviso es visual y es suficiente.
      }
    }
    alTerminar?.()
  }, [restante, alTerminar, vibracion])

  const terminado = restante <= 0

  return (
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
  )
}
