import { PESTANAS_AVANCE, PESTANAS_COMER, PESTANAS_ENTRENAR } from './secciones.js'

// Ayuda ligada a acciones reales, disponible también en carga, vacío y error.
const guias = {
  '/panel': ['Su día', 'Elija su siguiente paso', ['La tarjeta principal indica qué puede hacer hoy.', 'Use Entrenar para su rutina y Comer para sus porciones.', 'Anote su avance y consulte sus logros en Mi senda.']],
  '/bienvenida': ['Primeros pasos', 'Prepare su recorrido', ['Complete sus medidas y su objetivo.', 'Genere su plan de alimentación y entrenamiento.', 'Vuelva a Hoy para encontrar su siguiente acción.']],
  '/comer': ['Menú diario', 'Lea sus porciones', ['Abra el tiempo de comida que va a preparar.', 'Revise los gramos, la medida casera y el estado del alimento.', 'Para organizar varios días, abra Semana; para reunir ingredientes, Compras.']],
  '/comer/semana': ['Mi semana de comidas', 'Organice siete días', ['Revise primero sus alergias y restricciones.', 'Prepare la semana y elija un día para ver sus comidas.', 'Cambie una comida desde su tarjeta o abra las compras de los siete días.']],
  '/comer/recetas': ['Recetas', 'Encuentre una idea para cocinar', ['Busque una receta por su nombre.', 'Abra Ingredientes y preparación para ver los pasos.', 'Use Semana para obtener porciones ajustadas a su plan.']],
  '/comer/preferencias': ['Mis restricciones', 'Indique lo que necesita evitar', ['Marque alergias e intolerancias por separado de sus preferencias.', 'Si su restricción no aparece, use la opción correspondiente.', 'Guarde los cambios y prepare otra semana para aplicarlos.']],
  '/comer/plan': ['Mi plan', 'Entienda su objetivo diario', ['Genere el plan después de registrar sus medidas.', 'Consulte la energía diaria y abra los nutrientes para entenderlos.', 'El menú y la rutina le muestran cómo llevar ese plan a su día.']],
  '/comer/compras': ['Mis compras', 'Lleve lo necesario', ['Revise las cantidades y el costo estimado antes de comprar.', 'Marque cada alimento al conseguirlo; la fila completa se puede pulsar.', 'Puede imprimir la lista o quitar las marcas para otra compra.']],
  '/entrenar': ['Mi rutina', 'Prepare su sesión', ['La tarjeta superior muestra su sesión de hoy o la siguiente.', 'Abra la sesión para consultar ejercicios, series y descansos.', 'En Ejercicios puede ver cada guía antes de empezar.']],
  '/entrenar/biblioteca': ['Guías de ejercicios', 'Entienda el movimiento', ['Busque por nombre o filtre por músculo y equipo.', 'Abra una ficha para ver la preparación y el recorrido.', 'Pause el dibujo, elija una fase y lea qué cuidar.']],
  '/entrenar/bitacora': ['Mis sesiones', 'Vea lo que ha registrado', ['El historial reúne las sesiones guardadas en su cuenta.', 'Abra una sesión para revisar las series realizadas.', 'En Marcas puede consultar la evolución de cada ejercicio.']],
  '/entrenar/marcas': ['Mis marcas', 'Compare sus propios registros', ['Seleccione un ejercicio con registros.', 'Consulte la gráfica y sus valores escritos.', 'Las marcas dependen de las sesiones guardadas, no de ver una guía.']],
  '/avance': ['Registrar avance', 'Una revisión de su semana', ['Indique su peso de hoy y la fecha del registro.', 'Anote las sesiones realizadas y estime cuánto siguió su plan.', 'Guarde una vez y lea el resultado antes de continuar.']],
  '/avance/senda': ['Mi senda', 'Haga visible su constancia', ['Consulte sus puntos y lo que falta para el siguiente nivel.', 'Abra una insignia para entender cómo se obtiene.', 'Los logros se basan en sus propios registros.']],
  '/avance/evolucion': ['Mi evolución', 'Vea sus cambios con contexto', ['Revise las fechas y el número de registros.', 'Compare peso y constancia; puede abrir los valores en texto.', 'Use Registrar avance para añadir una nueva semana.']],
  '/avance/medidas': ['Mis medidas', 'Consulte su historial', ['La medición más reciente aparece primero.', 'Abra un registro para consultar sus datos.', 'Actualizar medidas añade un registro y conserva los anteriores.']],
  '/avance/medidas/editar': ['Actualizar medidas', 'Complete cuatro pasos', ['Registre medidas, actividad y objetivo.', 'Indique experiencia, días disponibles y antecedentes de salud.', 'Revise sus respuestas y guarde para añadirlas a su historial.']],
  '/avance/informes': ['Mis informes', 'Consulte o lleve sus datos', ['Elija el informe que necesita.', 'Revise su contenido y sus fechas antes de descargar.', 'Use PDF para leer o imprimir; Excel y CSV para trabajar los datos.']],
  '/mas': ['Mi cuenta', 'Ajuste Senda a su gusto', ['Use los accesos para encontrar sus medidas, plan y sesiones.', 'Elija tema, movimiento y vibración según sus preferencias.', 'Cierre sesión al terminar en un dispositivo compartido.']],
  '/mas/contrasena': ['Mi contraseña', 'Actualice su acceso', ['Escriba la contraseña actual.', 'Elija y confirme una nueva contraseña con letras y números.', 'Guarde el cambio; Senda adoptará la sesión renovada.']],
  '/admin/catalogos': ['Catálogos', 'Revise la disponibilidad local', ['Elija alimentos o ejercicios y busque un elemento.', 'Revise los datos antes de guardar cualquier cambio.', 'La disponibilidad controla qué elementos puede proponer el sistema.']],
  '/admin/cuentas': ['Cuentas', 'Administre accesos', ['Busque una cuenta y compruebe su identidad.', 'Revise el efecto del cambio de rol o estado.', 'Los perfiles de salud de otras personas no se muestran aquí.']],
  '/admin/informes': ['Informes de administración', 'Consulte los datos disponibles', ['Seleccione un informe del catálogo autorizado.', 'Revise las columnas y las fechas.', 'Descargue solo la información que necesita para su trabajo.']],
}

export function recorridoPara(ruta) {
  if (/^\/entrenar\/\d+\/?$/.test(ruta)) return { titulo: 'Mi entrenamiento', resumen: 'Una serie a la vez', pasos: ['Abra Cómo hacerlo para consultar la guía.', 'Anote la carga y las repeticiones o segundos de cada serie, y márquela al terminar.', 'Use el descanso y guarde la sesión al finalizar. Marcar una serie por sí solo no la envía al servidor.'], opciones: null, volver: '/entrenar' }
  const clave = ruta.startsWith('/entrenar/biblioteca/') ? '/entrenar/biblioteca' : ruta
  const guia = guias[clave]
  if (!guia) return null
  const opciones = ruta.startsWith('/comer') ? PESTANAS_COMER : ruta.startsWith('/entrenar') ? PESTANAS_ENTRENAR : ruta.startsWith('/avance') ? PESTANAS_AVANCE : null
  return { titulo: guia[0], resumen: guia[1], pasos: guia[2], opciones, volver: ruta.startsWith('/admin') ? '/mas' : '/panel' }
}

export function rutaActiva(ruta, opciones) {
  return opciones?.filter(o => ruta === o.ruta || ruta.startsWith(`${o.ruta}/`)).sort((a, b) => b.ruta.length - a.ruta.length)[0]?.ruta
}
