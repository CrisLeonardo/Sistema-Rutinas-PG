/**
 * Cliente de la interfaz de programación de aplicaciones.
 *
 * Centraliza el envío de peticiones para que las pantallas no repitan la
 * construcción de encabezados ni el tratamiento de errores.
 */

const URL_API = import.meta.env.VITE_URL_API ?? 'http://localhost:8000/api/v1'

/** Error con el mensaje que el servidor destinó al usuario final. */
export class ErrorApi extends Error {
  constructor(mensaje, codigo) {
    super(mensaje)
    this.name = 'ErrorApi'
    this.codigo = codigo
  }
}

/** Nombres legibles de los campos, para no mostrar al usuario los identificadores técnicos. */
const ETIQUETAS_CAMPO = {
  correo: 'Correo electrónico',
  nombre: 'Nombre',
  contrasena: 'Contraseña',
  peso_kg: 'Peso',
  estatura_cm: 'Estatura',
  edad: 'Edad',
  sexo: 'Sexo',
  nivel_actividad: 'Nivel de actividad',
  objetivo: 'Objetivo',
  nivel_experiencia: 'Nivel de experiencia',
  dias_entrenamiento_semana: 'Días de entrenamiento por semana',
}

/** Convierte el detalle de un error de validación en un texto legible. */
function describirValidacion(detalle) {
  if (!Array.isArray(detalle)) return null
  const mensajes = detalle.map((problema) => {
    // Pydantic antepone «Value error, » al mensaje que escribe el validador;
    // se retira para que el usuario lea únicamente el texto en español.
    const texto = String(problema.msg ?? '').replace(/^Value error,\s*/, '')
    const campo = problema.loc?.filter((parte) => parte !== 'body').join('.') ?? ''
    const etiqueta = ETIQUETAS_CAMPO[campo]

    if (problema.type === 'missing') {
      return `${etiqueta ?? campo}: este dato es obligatorio.`
    }
    // Los validadores del servidor ya redactan un mensaje completo en español,
    // de modo que anteponer el nombre del campo solo añadiría ruido.
    if (/^[A-ZÁÉÍÓÚÑ]/.test(texto)) return texto
    return etiqueta || campo ? `${etiqueta ?? campo}: ${texto}` : texto
  })
  return mensajes.join(' ')
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
  return 'No fue posible completar la operación. Intente de nuevo.'
}

/**
 * Envía una petición a la interfaz de programación de aplicaciones.
 *
 * @param {string} ruta Ruta relativa dentro de la interfaz, por ejemplo `/usuarios`.
 * @param {object} opciones Método, cuerpo y token de sesión.
 */
export async function peticion(ruta, { metodo = 'GET', datos = null, token = null } = {}) {
  const encabezados = { Accept: 'application/json' }
  if (datos !== null) encabezados['Content-Type'] = 'application/json'
  if (token) encabezados.Authorization = `Bearer ${token}`

  let respuesta
  try {
    respuesta = await fetch(`${URL_API}${ruta}`, {
      method: metodo,
      headers: encabezados,
      body: datos !== null ? JSON.stringify(datos) : undefined,
    })
  } catch {
    throw new ErrorApi(
      'No se pudo comunicar con el servidor. Verifique su conexión e intente de nuevo.',
      0,
    )
  }

  if (!respuesta.ok) {
    throw new ErrorApi(await interpretarError(respuesta), respuesta.status)
  }

  if (respuesta.status === 204) return null
  return respuesta.json()
}

export const servicioAcceso = {
  registrar: (datos) => peticion('/autenticacion/registro', { metodo: 'POST', datos }),
  iniciarSesion: (datos) => peticion('/autenticacion/acceso', { metodo: 'POST', datos }),
  renovar: (token) => peticion('/autenticacion/renovacion', { metodo: 'POST', token }),
  consultarSesion: (token) => peticion('/autenticacion/sesion', { token }),
}

export const servicioPerfil = {
  registrar: (datos, token) =>
    peticion('/perfil-biometrico', { metodo: 'POST', datos, token }),
  consultarVigente: (token) => peticion('/perfil-biometrico', { token }),
  consultarHistorial: (token) => peticion('/perfil-biometrico/historial', { token }),
}

export const servicioPlan = {
  generar: (token) => peticion('/plan-nutricional', { metodo: 'POST', token }),
  consultarVigente: (token) => peticion('/plan-nutricional', { token }),
  consultarHistorial: (token) => peticion('/plan-nutricional/historial', { token }),
  consultarMenu: (token) => peticion('/plan-nutricional/menu', { token }),
}

export const servicioRutina = {
  consultarVigente: (token) => peticion('/rutina', { token }),
}

export const servicioProgreso = {
  registrar: (datos, token) => peticion('/progreso', { metodo: 'POST', datos, token }),
  consultarHistorial: (token) => peticion('/progreso', { token }),
  consultarReporte: (token) => peticion('/progreso/reporte', { token }),
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
