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
 * y la pantalla suele estar apagada.
 */

import { useEffect, useRef, useState } from 'react'

function comoReloj(segundos) {
  const minutos = Math.floor(segundos / 60)
  const resto = segundos % 60
  return `${minutos}:${String(resto).padStart(2, '0')}`
}

export default function CronometroDescanso({ segundos, alTerminar, alSaltar }) {
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
    // La vibración es opcional: el escritorio no la implementa y algunos
    // navegadores la exigen tras una interacción del usuario.
    try {
      navigator.vibrate?.([200, 100, 200])
    } catch {
      // Sin vibración, el aviso es visual y es suficiente.
    }
    alTerminar?.()
  }, [restante, alTerminar])

  const terminado = restante <= 0
  const proporcion = segundos > 0 ? Math.max(restante, 0) / segundos : 0

  return (
    <div className={`cronometro ${terminado ? 'cronometro-listo' : ''}`} role="timer" aria-live="off">
      <div className="cronometro-cuerpo">
        <div>
          <div className="cronometro-rotulo">
            {terminado ? 'Descanso terminado' : 'Descanse antes de la siguiente serie'}
          </div>
          <div className="cronometro-cifra">{comoReloj(Math.max(restante, 0))}</div>
        </div>
        <button
          type="button"
          className="btn btn-light control-tactil flex-shrink-0"
          onClick={alSaltar}
        >
          {terminado ? 'Listo' : 'Saltar'}
        </button>
      </div>
      <div className="cronometro-barra">
        <div className="cronometro-avance" style={{ width: `${proporcion * 100}%` }} />
      </div>
      <span className="visually-hidden">
        {terminado ? 'El descanso terminó.' : `Quedan ${restante} segundos de descanso.`}
      </span>
    </div>
  )
}
