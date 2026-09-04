/**
 * Manejo de la sesión del usuario en la interfaz de cliente.
 *
 * Implementa el cierre automático tras el periodo de inactividad exigido por el
 * criterio de aceptación de la historia HU-02: mientras el usuario interactúa
 * con la aplicación el token se renueva; cuando deja de hacerlo, la sesión
 * caduca y se le devuelve a la pantalla de acceso.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'

import { servicioAcceso } from '../servicios/api.js'

const CLAVE_TOKEN = 'rutinas.token'
const CLAVE_USUARIO = 'rutinas.usuario'

// Frecuencia con que se revisa la inactividad y margen para renovar el token
// antes de que expire.
const INTERVALO_REVISION_MS = 30_000
const MARGEN_RENOVACION_MS = 5 * 60_000

// Antelación con que se avisa que la sesión está por caducar. Sin el aviso, la
// sesión se cerraba de golpe y se perdía lo que el usuario estuviera
// escribiendo, que en el formulario del perfil biométrico son cuatro pasos.
const MARGEN_AVISO_MS = 2 * 60_000

const EVENTOS_ACTIVIDAD = ['mousedown', 'keydown', 'scroll', 'touchstart', 'pointerdown']

const ContextoSesion = createContext(null)

/** Recupera el valor guardado en el almacenamiento de la pestaña. */
function leerAlmacenado(clave, comoJson = false) {
  try {
    const valor = sessionStorage.getItem(clave)
    if (valor === null) return null
    return comoJson ? JSON.parse(valor) : valor
  } catch {
    return null
  }
}

export function ProveedorSesion({ children }) {
  const [token, setToken] = useState(() => leerAlmacenado(CLAVE_TOKEN))
  const [usuario, setUsuario] = useState(() => leerAlmacenado(CLAVE_USUARIO, true))
  const [expiroPorInactividad, setExpiroPorInactividad] = useState(false)
  const [porExpirar, setPorExpirar] = useState(false)

  const ultimaActividad = useRef(Date.now())
  const vigenciaMs = useRef(30 * 60_000)
  const emitidoEn = useRef(Date.now())

  const guardarSesion = useCallback((respuesta) => {
    sessionStorage.setItem(CLAVE_TOKEN, respuesta.token_acceso)
    sessionStorage.setItem(CLAVE_USUARIO, JSON.stringify(respuesta.usuario))
    vigenciaMs.current = respuesta.expira_en_segundos * 1000
    emitidoEn.current = Date.now()
    ultimaActividad.current = Date.now()
    setToken(respuesta.token_acceso)
    setUsuario(respuesta.usuario)
    setExpiroPorInactividad(false)
    setPorExpirar(false)
  }, [])

  const limpiarSesion = useCallback(() => {
    sessionStorage.removeItem(CLAVE_TOKEN)
    sessionStorage.removeItem(CLAVE_USUARIO)
    setToken(null)
    setUsuario(null)
  }, [])

  const iniciarSesion = useCallback(
    async (credenciales) => {
      guardarSesion(await servicioAcceso.iniciarSesion(credenciales))
    },
    [guardarSesion],
  )

  const cerrarSesion = useCallback(() => {
    limpiarSesion()
    setExpiroPorInactividad(false)
    setPorExpirar(false)
  }, [limpiarSesion])

  /** Prolonga la sesión sin que el usuario tenga que volver a autenticarse. */
  const continuarSesion = useCallback(async () => {
    if (!token) return
    try {
      ultimaActividad.current = Date.now()
      guardarSesion(await servicioAcceso.renovar(token))
    } catch {
      limpiarSesion()
      setExpiroPorInactividad(true)
    }
  }, [token, guardarSesion, limpiarSesion])

  // Registra la última interacción del usuario con la aplicación.
  useEffect(() => {
    if (!token) return undefined
    const anotarActividad = () => {
      ultimaActividad.current = Date.now()
    }
    EVENTOS_ACTIVIDAD.forEach((evento) =>
      window.addEventListener(evento, anotarActividad, { passive: true }),
    )
    return () => {
      EVENTOS_ACTIVIDAD.forEach((evento) => window.removeEventListener(evento, anotarActividad))
    }
  }, [token])

  // Cierra la sesión por inactividad o renueva el token si el usuario sigue activo.
  useEffect(() => {
    if (!token) return undefined

    const revisar = async () => {
      const inactividad = Date.now() - ultimaActividad.current
      if (inactividad >= vigenciaMs.current) {
        limpiarSesion()
        setExpiroPorInactividad(true)
        setPorExpirar(false)
        return
      }

      // Se avisa antes de cerrar, en lugar de cerrar y ya: quien está llenando
      // un formulario largo debe poder salvar lo escrito.
      setPorExpirar(inactividad >= vigenciaMs.current - MARGEN_AVISO_MS)

      const transcurrido = Date.now() - emitidoEn.current
      if (transcurrido >= vigenciaMs.current - MARGEN_RENOVACION_MS) {
        try {
          guardarSesion(await servicioAcceso.renovar(token))
        } catch {
          limpiarSesion()
          setExpiroPorInactividad(true)
        }
      }
    }

    const temporizador = setInterval(revisar, INTERVALO_REVISION_MS)
    return () => clearInterval(temporizador)
  }, [token, guardarSesion, limpiarSesion])

  // Verifica contra el servidor que el token recuperado del almacenamiento siga vigente.
  useEffect(() => {
    if (!token) return
    let vigente = true
    servicioAcceso
      .consultarSesion(token)
      .then((cuenta) => {
        if (!vigente) return
        sessionStorage.setItem(CLAVE_USUARIO, JSON.stringify(cuenta))
        setUsuario(cuenta)
      })
      .catch(() => {
        if (vigente) limpiarSesion()
      })
    return () => {
      vigente = false
    }
    // Se ejecuta solo al montar y cuando cambia el token tras un acceso nuevo.
  }, [token, limpiarSesion])

  const valor = useMemo(
    () => ({
      token,
      usuario,
      autenticado: Boolean(token && usuario),
      esAdministrador: usuario?.rol === 'administrador',
      expiroPorInactividad,
      porExpirar,
      iniciarSesion,
      cerrarSesion,
      continuarSesion,
      // La usa el cambio de contraseña: el servidor emite un token nuevo y la
      // sesión debe adoptarlo, o seguiría atada al anterior.
      renovarSesion: guardarSesion,
    }),
    [
      token,
      usuario,
      expiroPorInactividad,
      porExpirar,
      iniciarSesion,
      cerrarSesion,
      continuarSesion,
      guardarSesion,
    ],
  )

  return <ContextoSesion.Provider value={valor}>{children}</ContextoSesion.Provider>
}

/** Acceso al estado de la sesión desde cualquier componente. */
export function useSesion() {
  const contexto = useContext(ContextoSesion)
  if (contexto === null) {
    throw new Error('useSesion debe utilizarse dentro de ProveedorSesion.')
  }
  return contexto
}
