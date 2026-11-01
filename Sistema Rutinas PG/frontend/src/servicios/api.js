/**
 * Cliente de la interfaz de programación de aplicaciones.
 *
 * Centraliza el envío de peticiones para que las pantallas no repitan la
 * construcción de encabezados ni el tratamiento de errores.
 */

import { conexion, URL_API } from './conexion.mjs'
import { describirValidacion } from './validacion.mjs'

/**
 * Tiempo que se espera una respuesta antes de darla por perdida.
 *
 * `fetch` no tiene tiempo límite propio: sin este corte, una petición contra un
 * servicio que acepta la conexión pero no contesta —el servidor arrancando, o
 * caído detrás de un reenvío que mantiene la conexión abierta— deja el botón en
 * «Verificando…» para siempre, sin error y sin forma de reintentar. Es el
 * síntoma de «no inicia sesión» que se reportó, y el corte lo convierte en un
 * mensaje que dice qué pasó.
 *
 * El acceso comprueba disponibilidad antes de enviar las credenciales. Este
 * corte de red no sustituye las metas de rendimiento de 3 s y 2 s.
 */
const TIEMPO_LIMITE_MS = 30_000

/** Error con el mensaje que el servidor destinó al usuario final. */
export class ErrorApi extends Error {
  constructor(mensaje, codigo) {
    super(mensaje)
    this.name = 'ErrorApi'
    this.codigo = codigo
  }
}

async function interpretarError(respuesta) {
  let detalle = null
  try {
    const cuerpo = await respuesta.json()
    detalle = cuerpo?.detail ?? null
  } catch {
    detalle = null
  }

  if (typeof detalle === 'string') return detalle
  const validacion = describirValidacion(detalle)
  if (validacion) return validacion

  if (respuesta.status === 401) return 'Su sesión no está activa. Inicie sesión nuevamente.'
  if (respuesta.status === 403) return 'No cuenta con permisos para realizar esta operación.'
  if (respuesta.status === 429) {
    return 'Demasiados intentos seguidos. Espere unos minutos antes de volver a intentarlo.'
  }
  if (respuesta.status >= 500) {
    return 'El servidor no pudo atender la solicitud. Intente de nuevo en unos momentos.'
  }
  return 'No fue posible completar la operación. Intente de nuevo.'
}

/**
 * Envía una petición a la interfaz de programación de aplicaciones.
 *
 * @param {string} ruta Ruta relativa dentro de la interfaz, por ejemplo `/usuarios`.
 * @param {object} opciones Método, cuerpo y token de sesión.
 */
async function solicitar(ruta, { metodo = 'GET', datos = null, token = null } = {}, archivo = false) {
  const encabezados = { Accept: 'application/json' }
  if (datos !== null) encabezados['Content-Type'] = 'application/json'
  if (token) encabezados.Authorization = `Bearer ${token}`

  const cancelacion = new AbortController()
  const reloj = setTimeout(() => cancelacion.abort(), TIEMPO_LIMITE_MS)

  try {
    const respuesta = await fetch(`${URL_API}${ruta}`, {
      method: metodo,
      headers: encabezados,
      body: datos !== null ? JSON.stringify(datos) : undefined,
      signal: cancelacion.signal,
      cache: 'no-store',
    })
    if (!respuesta.ok) {
      const mensaje = await interpretarError(respuesta)
      if (respuesta.status >= 500) conexion.fallo(mensaje)
      throw new ErrorApi(mensaje, respuesta.status)
    }
    if (respuesta.status === 204) { conexion.disponible(); return null }
    const tipo = respuesta.headers.get('Content-Type') ?? ''
    if ((!archivo && !tipo.includes('application/json')) || (archivo && tipo.includes('text/html'))) {
      const mensaje = 'El servicio devolvió una página en lugar de los datos. Intente de nuevo o consulte Ayuda.'
      conexion.fallo(mensaje)
      throw new ErrorApi(mensaje, 0)
    }
    const contenido = archivo ? await respuesta.blob() : await respuesta.json()
    conexion.disponible()
    return archivo ? { contenido, disposicion: respuesta.headers.get('Content-Disposition') ?? '' } : contenido
  } catch (fallo) {
    if (fallo instanceof ErrorApi) throw fallo
    // Se distingue el corte por tiempo de la falta de conexión: son dos
    // problemas distintos y el usuario puede hacer algo distinto con cada uno.
    if (fallo?.name === 'AbortError') {
      const mensaje = metodo === 'GET' ? 'La consulta tardó demasiado. Vuelva a intentarlo en un momento.'
        : 'No recibimos la confirmación a tiempo. Consulte si el cambio se guardó antes de volver a enviarlo.'
      conexion.fallo(mensaje)
      throw new ErrorApi(mensaje, 0)
    }
    const mensaje = 'No se pudo comunicar con el servidor. Verifique su conexión e intente de nuevo.'
    conexion.fallo(mensaje)
    throw new ErrorApi(mensaje, 0)
  } finally {
    clearTimeout(reloj)
  }
}

export const peticion = (ruta, opciones) => solicitar(ruta, opciones)

/**
 * Descarga un archivo de la interfaz de programación y lo entrega al navegador.
 *
 * No basta con un enlace: la ruta exige el token de sesión en el encabezado, y
 * un enlace no puede enviarlo. Se pide el archivo, se convierte en un objeto
 * local y se simula el clic sobre un enlace a ese objeto, que es lo que hace
 * que el navegador lo guarde con su nombre en lugar de abrirlo.
 *
 * @returns {Promise<string>} El nombre con que se guardó el archivo.
 */
export async function descargarArchivo(ruta, { token = null, nombrePorOmision = 'informe' } = {}) {
  const { contenido, disposicion } = await solicitar(ruta, { token }, true)
  const nombre = /filename="([^"]+)"/.exec(disposicion)?.[1] ?? nombrePorOmision
  const objeto = URL.createObjectURL(contenido)

  const enlace = document.createElement('a')
  enlace.href = objeto
  enlace.download = nombre
  document.body.appendChild(enlace)
  enlace.click()
  enlace.remove()
  // Se libera después de que el navegador haya tomado el archivo; liberarlo de
  // inmediato cancela la descarga en algunos navegadores de teléfono.
  setTimeout(() => URL.revokeObjectURL(objeto), 10_000)

  return nombre
}

export const servicioAcceso = {
  opcionesPublicas: () => peticion('/autenticacion/opciones-publicas'),
  recuperar: (datos) => peticion('/autenticacion/recuperacion', { metodo: 'POST', datos }),
  restablecer: (datos) => peticion('/autenticacion/restablecimiento', { metodo: 'POST', datos }),
  registrar: (datos) => peticion('/autenticacion/registro', { metodo: 'POST', datos }),
  iniciarSesion: (datos) => peticion('/autenticacion/acceso', { metodo: 'POST', datos }),
  renovar: (token) => peticion('/autenticacion/renovacion', { metodo: 'POST', token }),
  consultarSesion: (token) => peticion('/autenticacion/sesion', { token }),
  cambiarContrasena: (datos, token) =>
    peticion('/autenticacion/cambio-de-contrasena', { metodo: 'POST', datos, token }),
}

export const servicioPerfil = {
  registrar: (datos, token) =>
    peticion('/perfil-biometrico', { metodo: 'POST', datos, token }),
  consultarVigente: (token) => peticion('/perfil-biometrico', { token }),
  consultarHistorial: (token) => peticion('/perfil-biometrico/historial', { token }),
}

export const servicioAlimentacion = {
  preferencias: (token) => peticion('/alimentacion/preferencias', { token }),
  guardarPreferencias: (datos, token) => peticion('/alimentacion/preferencias', { metodo: 'PUT', datos, token }),
  recetas: (token) => peticion('/alimentacion/recetas', { token }),
  semana: (token) => peticion('/alimentacion/semana', { token }),
  preparar: (token) => peticion('/alimentacion/semana', { metodo: 'POST', token }),
  alternativas: (dia, tiempo, token) => peticion(`/alimentacion/alternativas?dia=${dia}&tiempo=${tiempo}`, { token }),
  cambiar: (datos, token) => peticion('/alimentacion/semana/comida', { metodo: 'PUT', datos, token }),
}

export const servicioPlan = {
  generar: (token) => peticion('/plan-nutricional', { metodo: 'POST', token }),
  consultarVigente: (token) => peticion('/plan-nutricional', { token }),
  consultarHistorial: (token) => peticion('/plan-nutricional/historial', { token }),
  consultarMenu: (token) => peticion('/plan-nutricional/menu', { token }),
  consultarListaDeCompras: (token) =>
    peticion('/plan-nutricional/lista-de-compras', { token }),
}

export const servicioRutina = {
  consultarVigente: (token) => peticion('/rutina', { token }),
}

export const servicioEntrenamiento = {
  abrirSesion: (sesionId, token) =>
    peticion(`/entrenamiento/sesiones/${sesionId}`, { token }),
  registrarSesion: (datos, token) =>
    peticion('/entrenamiento/sesiones', { metodo: 'POST', datos, token }),
  consultarBitacora: (token) => peticion('/entrenamiento/sesiones', { token }),
  consultarResumen: (token) => peticion('/entrenamiento/resumen', { token }),
  consultarEjercicio: (ejercicioId, token) =>
    peticion(`/entrenamiento/ejercicios/${ejercicioId}`, { token }),
}

export const servicioJuego = {
  consultarEstado: (token) => peticion('/juego', { token }),
}

export const servicioProgreso = {
  registrar: (datos, token) => peticion('/progreso', { metodo: 'POST', datos, token }),
  consultarHistorial: (token) => peticion('/progreso', { token }),
  consultarReporte: (token) => peticion('/progreso/reporte', { token }),
}

export const servicioInformes = {
  listar: (token) => peticion('/informes', { token }),
  consultar: (clave, token) => peticion(`/informes/${clave}`, { token }),
  descargar: (clave, formato, token) =>
    descargarArchivo(`/informes/${clave}/${formato}`, {
      token,
      nombrePorOmision: `informe-${clave}.${formato}`,
    }),
}

export const servicioCatalogos = {
  listarAlimentos: (token) => peticion('/catalogos/alimentos', { token }),
  crearAlimento: (datos, token) =>
    peticion('/catalogos/alimentos', { metodo: 'POST', datos, token }),
  modificarAlimento: (id, datos, token) =>
    peticion(`/catalogos/alimentos/${id}`, { metodo: 'PUT', datos, token }),
  cambiarDisponibilidadAlimento: (id, activo, token) =>
    peticion(`/catalogos/alimentos/${id}/disponibilidad`, {
      metodo: 'PUT',
      datos: { activo },
      token,
    }),
  listarEjercicios: (token) => peticion('/catalogos/ejercicios', { token }),
  crearEjercicio: (datos, token) =>
    peticion('/catalogos/ejercicios', { metodo: 'POST', datos, token }),
  modificarEjercicio: (id, datos, token) =>
    peticion(`/catalogos/ejercicios/${id}`, { metodo: 'PUT', datos, token }),
  cambiarDisponibilidadEjercicio: (id, activo, token) =>
    peticion(`/catalogos/ejercicios/${id}/disponibilidad`, {
      metodo: 'PUT',
      datos: { activo },
      token,
    }),
}

export const servicioUsuarios = {
  listar: (token) => peticion('/usuarios', { token }),
  cambiarRol: (id, rol, token) =>
    peticion(`/usuarios/${id}/rol`, { metodo: 'PUT', datos: { rol }, token }),
  cambiarEstado: (id, activo, token) =>
    peticion(`/usuarios/${id}/estado`, { metodo: 'PUT', datos: { activo }, token }),
}
