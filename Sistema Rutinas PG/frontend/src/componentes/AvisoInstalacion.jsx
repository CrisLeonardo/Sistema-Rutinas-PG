/**
 * Invitación a instalar la aplicación en la pantalla de inicio.
 *
 * En Android y escritorio, Chrome y Edge avisan de que la página es
 * instalable con el evento `beforeinstallprompt`; ese evento se intercepta
 * para lanzarlo desde un botón propio en vez del icono discreto de la barra
 * de direcciones, que casi nadie nota.
 *
 * iOS no dispara ese evento —Safari no ofrece instalación con un solo toque
 * para ningún sitio— así que ahí se muestra una guía de los pasos manuales
 * (Compartir → Agregar a pantalla de inicio).
 *
 * Quien ya instaló la aplicación nunca ve este aviso: se comprueba con
 * `display-mode: standalone` (Android/escritorio) y `navigator.standalone`
 * (iOS). Quien lo descarta no vuelve a verlo hasta pasadas dos semanas.
 */

import { useEffect, useState } from 'react'

const CLAVE_OCULTO = 'rutinas.instalacion.oculta'
const DIAS_REAPARICION = 14
const RETRASO_IOS_MS = 2500

function estaInstalada() {
  return (
    window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true
  )
}

function esIOS() {
  const ua = window.navigator.userAgent
  const esDispositivoApple = /iphone|ipad|ipod/i.test(ua)
  const esIPadComoEscritorio = ua.includes('Macintosh') && navigator.maxTouchPoints > 1
  return esDispositivoApple || esIPadComoEscritorio
}

function ocultoRecientemente() {
  const valor = localStorage.getItem(CLAVE_OCULTO)
  if (!valor) return false
  const dias = (Date.now() - Number(valor)) / (1000 * 60 * 60 * 24)
  return dias < DIAS_REAPARICION
}

function IconoCompartir() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">
      <path d="M12 15V3" />
      <path d="M8 7l4-4 4 4" />
      <path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7" />
    </svg>
  )
}

function IconoAgregar() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <path d="M12 8v8" />
      <path d="M8 12h8" />
    </svg>
  )
}

export default function AvisoInstalacion({ conBarra = false }) {
  const [eventoDiferido, setEventoDiferido] = useState(null)
  const [visible, setVisible] = useState(false)
  const [mostrarGuiaIOS, setMostrarGuiaIOS] = useState(false)
  const [instalando, setInstalando] = useState(false)

  useEffect(() => {
    if (estaInstalada() || ocultoRecientemente()) return undefined

    if (esIOS()) {
      const temporizador = setTimeout(() => setVisible(true), RETRASO_IOS_MS)
      return () => clearTimeout(temporizador)
    }

    function alEstarListo(evento) {
      evento.preventDefault()
      setEventoDiferido(evento)
      setVisible(true)
    }
    window.addEventListener('beforeinstallprompt', alEstarListo)
    return () => window.removeEventListener('beforeinstallprompt', alEstarListo)
  }, [])

  useEffect(() => {
    function alInstalarse() {
      setVisible(false)
    }
    window.addEventListener('appinstalled', alInstalarse)
    return () => window.removeEventListener('appinstalled', alInstalarse)
  }, [])

  if (!visible) return null

  const ocultar = () => {
    localStorage.setItem(CLAVE_OCULTO, String(Date.now()))
    setVisible(false)
  }

  const instalar = async () => {
    if (!eventoDiferido) return
    setInstalando(true)
    try {
      eventoDiferido.prompt()
      const eleccion = await eventoDiferido.userChoice
      if (eleccion.outcome === 'accepted') {
        setVisible(false)
      } else {
        ocultar()
      }
    } finally {
      setInstalando(false)
      setEventoDiferido(null)
    }
  }

  return (
    <div
      className={`aviso-instalacion no-imprimir${conBarra ? '' : ' aviso-instalacion--sin-barra'}`}
      role="dialog"
      aria-label="Instalar la aplicación"
    >
      <div className="aviso-instalacion__cabecera">
        <img src="/pwa-192x192.png" alt="" className="aviso-instalacion__logo" />
        <p className="cuerpo">
          <strong>Instale la aplicación</strong> para abrirla desde su pantalla de inicio, como
          cualquier otra app.
        </p>
      </div>

      {esIOS() && mostrarGuiaIOS && (
        <ol className="aviso-instalacion__pasos">
          <li>
            Toque <IconoCompartir /> <strong>Compartir</strong> en la barra de Safari.
          </li>
          <li>
            Elija <strong>Agregar a pantalla de inicio</strong> <IconoAgregar />.
          </li>
          <li>Confirme con «Agregar».</li>
        </ol>
      )}

      <div className="aviso-instalacion__acciones">
        <button type="button" className="boton boton--secundario" onClick={ocultar}>
          Ahora no
        </button>
        {esIOS() ? (
          mostrarGuiaIOS ? (
            <button type="button" className="boton boton--principal" onClick={ocultar}>
              Entendido
            </button>
          ) : (
            <button type="button" className="boton boton--principal" onClick={() => setMostrarGuiaIOS(true)}>
              Ver cómo
            </button>
          )
        ) : (
          <button type="button" className="boton boton--principal" onClick={instalar} disabled={instalando}>
            {instalando ? 'Instalando…' : 'Instalar'}
          </button>
        )}
      </div>
    </div>
  )
}
