/**
 * Valores controlados del perfil biométrico, con su descripción en lenguaje sencillo.
 *
 * Reproducen las enumeraciones del servidor. Las descripciones atienden el
 * requerimiento no funcional 4.5.3: toda cifra o término técnico se acompaña de
 * una explicación breve, porque el 42.6 % de los encuestados declaró una
 * facilidad de uso percibida media o baja.
 */

export const RANGOS = {
  pesoMinimo: 30,
  pesoMaximo: 250,
  estaturaMinima: 120,
  estaturaMaxima: 220,
  edadMinima: 18,
  edadMaxima: 100,
  diasMinimos: 1,
  diasMaximos: 7,
}

export const SEXOS = [
  { valor: 'masculino', etiqueta: 'Masculino' },
  { valor: 'femenino', etiqueta: 'Femenino' },
]

export const NIVELES_ACTIVIDAD = [
  {
    valor: 'sedentario',
    etiqueta: 'Sedentario',
    detalle: 'Trabajo de oficina y poco o ningún ejercicio.',
  },
  {
    valor: 'ligero',
    etiqueta: 'Ligero',
    detalle: 'Camina a diario o entrena una o dos veces por semana.',
  },
  {
    valor: 'moderado',
    etiqueta: 'Moderado',
    detalle: 'Entrena de tres a cuatro veces por semana.',
  },
  {
    valor: 'alto',
    etiqueta: 'Alto',
    detalle: 'Entrena de cinco a seis veces por semana.',
  },
  {
    valor: 'muy_alto',
    etiqueta: 'Muy alto',
    detalle: 'Entrena a diario o realiza trabajo físico pesado.',
  },
]

export const OBJETIVOS = [
  {
    valor: 'perdida_grasa',
    etiqueta: 'Perder grasa',
    detalle: 'Reducir el porcentaje de grasa conservando la masa muscular.',
  },
  {
    valor: 'mantenimiento',
    etiqueta: 'Mantener el peso',
    detalle: 'Sostener la composición corporal actual.',
  },
  {
    valor: 'ganancia_muscular',
    etiqueta: 'Ganar músculo',
    detalle: 'Aumentar la masa muscular de forma progresiva.',
  },
]

export const NIVELES_EXPERIENCIA = [
  {
    valor: 'principiante',
    etiqueta: 'Principiante',
    detalle: 'Menos de seis meses entrenando con pesas.',
  },
  {
    valor: 'intermedio',
    etiqueta: 'Intermedio',
    detalle: 'Entre seis meses y dos años de entrenamiento constante.',
  },
  {
    valor: 'avanzado',
    etiqueta: 'Avanzado',
    detalle: 'Más de dos años entrenando de forma planificada.',
  },
]

/** Historial de lesiones: la rutina deja fuera los ejercicios que cargan la zona. */
export const ZONAS_LESION = [
  { valor: 'hombro', etiqueta: 'Hombro' },
  { valor: 'codo_muneca', etiqueta: 'Codo o muñeca' },
  { valor: 'espalda_baja', etiqueta: 'Espalda baja' },
  { valor: 'rodilla', etiqueta: 'Rodilla' },
  { valor: 'tobillo', etiqueta: 'Tobillo' },
]

/**
 * Patologías crónicas severas (restricción RE-02). Con cualquiera de ellas el
 * servidor no genera el plan y remite a un profesional de la salud.
 */
export const CONDICIONES_MEDICAS = [
  { valor: 'cardiopatia', etiqueta: 'Enfermedad del corazón' },
  { valor: 'hipertension_no_controlada', etiqueta: 'Presión alta sin control médico' },
  { valor: 'diabetes', etiqueta: 'Diabetes' },
  { valor: 'enfermedad_renal', etiqueta: 'Enfermedad de los riñones' },
  { valor: 'trastorno_alimentario', etiqueta: 'Trastorno de la conducta alimentaria' },
]

/** Busca la etiqueta legible de un valor dentro de una lista de opciones. */
export function etiquetaDe(opciones, valor) {
  return opciones.find((opcion) => opcion.valor === valor)?.etiqueta ?? valor ?? '—'
}
