/**
 * Aviso previo al cierre de la sesión por inactividad.
 *
 * La sesión caduca a los treinta minutos sin interacción, como exige el criterio
 * de aceptación de la historia HU-02. Hasta ahora se cerraba de golpe: el
 * usuario perdía lo que estuviera escribiendo y solo se enteraba al llegar de
 * vuelta a la pantalla de acceso. Registrar el perfil biométrico son cuatro
 * pasos, y perderlos a la mitad es motivo suficiente para no volver a
 * intentarlo.
 *
 * El aviso aparece dos minutos antes y ofrece continuar sin volver a escribir
 * las credenciales. No sustituye el cierre: si el usuario no responde, la sesión
 * caduca igual.
 *
 * Aparece como hoja sobre la barra de navegación y no como banda superior: en
 * un teléfono, el aviso que hay que responder debe caer donde está el pulgar,
 * no en el extremo opuesto de la pantalla.
 */

import { useState } from 'react'

import { useSesion } from '../contexto/ContextoSesion.jsx'

export default function AvisoDeSesion() {
  const { porExpirar, autenticado, continuarSesion } = useSesion()
  const [continuando, setContinuando] = useState(false)

  if (!autenticado || !porExpirar) return null

  const continuar = async () => {
    setContinuando(true)
    try {
      await continuarSesion()
    } finally {
      setContinuando(false)
    }
  }

  return (
    <div className="aviso-sesion no-imprimir" role="alertdialog" aria-live="assertive">
      <p className="cuerpo">
        <strong>Su sesión está por cerrarse</strong> por inactividad. Si sigue aquí, continúe
        para no perder lo que haya escrito.
      </p>
      <button
        type="button"
        className="boton boton--principal"
        onClick={continuar}
        disabled={continuando}
      >
        {continuando ? 'Continuando…' : 'Seguir conectado'}
      </button>
    </div>
  )
}
