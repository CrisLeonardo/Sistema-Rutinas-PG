/** Una comprobación compartida por pestaña; nunca repite escrituras ni credenciales. */
export function resolverUrlApi(configurada, produccion = false) {
  return (configurada?.trim() || (produccion ? '/api/v1' : 'http://127.0.0.1:8010/api/v1')).replace(/\/+$/, '')
}

export function crearMonitorConexion({ url, solicitar = (...args) => fetch(...args), plazo = 75_000, porIntento = 10_000, pausa = 1_500 } = {}) {
  let estado = { fase: 'inicial', detalle: '' }
  let pendiente = null
  let disponibleDesde = 0
  const oyentes = new Set()
  const actualizar = (fase, detalle = '') => {
    estado = { fase, detalle }
    oyentes.forEach(avisar => avisar())
  }
  const disponible = () => {
    disponibleDesde = Date.now()
    if (estado.fase !== 'disponible') actualizar('disponible')
  }
  const fallo = detalle => actualizar('sin-conexion', detalle)
  const comprobar = () => {
    if (pendiente) {
      if (estado.fase === 'sin-conexion') actualizar('conectando')
      return pendiente
    }
    if (estado.fase === 'disponible' && Date.now() - disponibleDesde < 15_000) return Promise.resolve(true)
    actualizar('conectando')
    pendiente = (async () => {
      const inicio = Date.now()
      let detalle = 'No pudimos conectar. Compruebe su conexión y vuelva a intentarlo.'
      do {
        if (globalThis.navigator?.onLine === false) {
          detalle = 'Está sin conexión a Internet. Puede volver a conectar cuando recupere la señal.'
          break
        }
        const controlador = new AbortController()
        const temporizador = setTimeout(() => controlador.abort(), Math.min(porIntento, plazo - (Date.now() - inicio)))
        try {
          const respuesta = await solicitar(`${url}/estado`, { signal: controlador.signal, cache: 'no-store', headers: { Accept: 'application/json' } })
          // Un rewrite incorrecto puede devolver index.html con estado 200.
          if (respuesta.ok && respuesta.headers.get('Content-Type')?.includes('application/json')) {
            const datos = await respuesta.json()
            if (datos?.estado === 'disponible') { disponible(); return true }
          }
          if (respuesta.ok || respuesta.status === 404) {
            detalle = 'La dirección del servicio no devuelve la respuesta esperada. Intente de nuevo o consulte Ayuda.'
            break
          }
        } catch { /* Solo se repite esta lectura pública de salud. */ }
        finally { clearTimeout(temporizador) }
        const restante = plazo - (Date.now() - inicio)
        if (restante > 0) await new Promise(resolve => setTimeout(resolve, Math.min(pausa, restante)))
      } while (Date.now() - inicio < plazo)
      fallo(detalle)
      return false
    })().finally(() => { pendiente = null })
    return pendiente
  }
  return { comprobar, disponible, fallo, leer: () => estado, suscribir: avisar => { oyentes.add(avisar); return () => oyentes.delete(avisar) } }
}

export const URL_API = resolverUrlApi(import.meta.env?.VITE_URL_API, import.meta.env?.PROD)
export const conexion = crearMonitorConexion({ url: URL_API })

/** Solo una respuesta de autenticación puede invalidar la sesión. */
export const sesionRechazada = fallo => [401, 403].includes(fallo?.codigo)
