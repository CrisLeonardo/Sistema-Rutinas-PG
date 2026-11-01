/**
 * Mensajes de validación en español.
 *
 * El servidor redacta en español los mensajes de sus validadores propios, pero
 * las comprobaciones estándar de Pydantic —un número fuera de rango, un texto
 * demasiado corto, un correo mal escrito— llegan en inglés. Antes se mostraban
 * tal cual («Input should be less than or equal to 100»), sin decir qué dato
 * falló. Aquí se redactan a partir del tipo de error y de sus límites.
 */

/** Nombres legibles de los campos, para no mostrar al usuario los identificadores técnicos. */
export const ETIQUETAS_CAMPO = {
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
  contrasena_actual: 'Contraseña actual',
  contrasena_nueva: 'Contraseña nueva',
  perimetro_cintura_cm: 'Perímetro de cintura',
  sesiones_cumplidas: 'Sesiones cumplidas',
  adherencia_nutricional: 'Cumplimiento del plan',
  fecha_registro: 'Fecha',
  fecha: 'Fecha',
  series: 'Series',
  repeticiones: 'Repeticiones',
  duracion_segundos: 'Duración',
  repeticiones_en_reserva: 'Repeticiones en reserva',
  percepcion_esfuerzo: 'Esfuerzo de la sesión',
  duracion_minutos: 'Duración',
  notas: 'Notas',
  sesion_id: 'Sesión',
  energia_kcal_100g: 'Energía por 100 g',
  proteina_g_100g: 'Proteína por 100 g',
  carbohidrato_g_100g: 'Carbohidrato por 100 g',
  grasa_g_100g: 'Grasa por 100 g',
  costo_aproximado_quetzales: 'Costo',
  medida_casera: 'Medida casera',
  categoria: 'Categoría',
  grupo_muscular: 'Grupo muscular',
  equipamiento: 'Equipamiento',
  descripcion: 'Descripción',
}

const numero = valor => Number(valor).toLocaleString('es-GT')

/** Redacta el problema sin el nombre del campo, según el tipo de error de Pydantic. */
function redactar(problema, texto) {
  const ctx = problema.ctx ?? {}
  switch (problema.type) {
    case 'less_than_equal': return `debe ser como máximo ${numero(ctx.le)}.`
    case 'less_than': return `debe ser menor que ${numero(ctx.lt)}.`
    case 'greater_than_equal': return `debe ser como mínimo ${numero(ctx.ge)}.`
    case 'greater_than': return `debe ser mayor que ${numero(ctx.gt)}.`
    case 'int_parsing': case 'int_type': case 'int_from_float': return 'debe ser un número entero.'
    case 'float_parsing': case 'float_type': return 'debe ser un número.'
    case 'string_too_short': return `debe tener al menos ${ctx.min_length} caracteres.`
    case 'string_too_long': return `admite como máximo ${ctx.max_length} caracteres.`
    case 'too_short': return `debe incluir al menos ${ctx.min_length} elemento${ctx.min_length === 1 ? '' : 's'}.`
    case 'too_long': return `admite como máximo ${ctx.max_length} elementos.`
    case 'enum': case 'literal_error': return 'tiene un valor que no está entre las opciones permitidas.'
    case 'date_parsing': case 'date_type': case 'date_from_datetime_parsing': return 'debe ser una fecha válida.'
    case 'bool_parsing': case 'bool_type': return 'debe ser sí o no.'
    case 'string_type': return 'debe ser un texto.'
    default: break
  }
  if (/valid email/i.test(texto)) return 'no es una dirección de correo válida.'
  return null
}

/** Convierte el detalle de un error de validación en un texto legible. */
export function describirValidacion(detalle) {
  if (!Array.isArray(detalle)) return null
  const mensajes = detalle.map((problema) => {
    // Pydantic antepone «Value error, » al mensaje que escribe el validador.
    const texto = String(problema.msg ?? '').replace(/^Value error,\s*/, '')
    const ruta = (problema.loc ?? []).filter(parte => !['body', 'query', 'path'].includes(parte))
    const nombres = ruta.filter(parte => typeof parte === 'string')
    const campo = nombres.at(-1) ?? ''
    const etiqueta = ETIQUETAS_CAMPO[campo] ?? ETIQUETAS_CAMPO[nombres.join('.')] ?? (campo || 'Dato')
    const posicion = ruta.findIndex(parte => typeof parte === 'number')
    const serie = nombres[0] === 'series' && posicion >= 0 ? ` de la serie ${ruta[posicion] + 1}` : ''

    if (problema.type === 'missing') return `${etiqueta}${serie}: este dato es obligatorio.`
    // Los validadores propios del servidor ya redactan un mensaje completo en
    // español; solo esos pasan sin cambios.
    if (problema.type === 'value_error' && !/valid email/i.test(texto)) return texto
    const redactado = redactar(problema, texto)
    return `${etiqueta}${serie}: ${redactado ?? 'tiene un valor no válido.'}`
  })
  return mensajes.join(' ')
}
