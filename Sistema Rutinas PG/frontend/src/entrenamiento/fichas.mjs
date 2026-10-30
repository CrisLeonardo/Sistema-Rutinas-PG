// Contenido editorial versionado; no modifica la prescripción ni el catálogo.
// Las fuentes se consultaron el 30-10-2026. Textos e ilustraciones propios.
const nasm = slug => `https://www.nasm.org/resource-center/exercise-library/${slug}`
const ace = ruta => `https://www.acefitness.org/resources/everyone/exercise-library/${ruta}/`

export const GRUPOS = { pecho: 'Pecho', espalda: 'Espalda', pierna: 'Pierna', hombro: 'Hombro', brazo: 'Brazo', abdomen: 'Abdomen' }
export const FICHAS = [
  {
    clave: 'press-banca', nombre: 'Press de banca con barra', grupo_muscular: 'pecho', equipamiento: 'Barra y discos',
    material: 'Banca plana, barra, discos, soportes y seguros; apoyo de una persona capacitada.',
    objetivo: 'Empuje horizontal: pectorales y tríceps.', dificultad: 'Requiere aprender el manejo de la barra y los seguros.', vista: 'Lateral',
    inicio: 'Apoya los pies en el suelo y la espalda en la banca. Sujeta la barra con el pulgar cerrado y las muñecas alineadas.',
    fases: [ ['Prepara', 'Estabiliza los hombros y coloca la barra sobre el pecho con ayuda si la necesitas.'], ['Desciende', 'Baja con control hacia el pecho, sin rebote y sin perder los apoyos.'], ['Empuja', 'Extiende los brazos para volver al inicio, sin un golpe al final.'] ],
    claves: ['Mantén pies y glúteos apoyados.', 'Expulsa el aire al empujar; evita contenerlo.'],
    errores: ['Rebotar la barra en el pecho.', 'Separar los glúteos de la banca o perder el control de las muñecas.'],
    variantes: ['Press con mancuernas: permite un agarre diferente, con aprendizaje propio.'],
    alternativas: ['Lagartijas: otro empuje de pecho; la dificultad y la carga no son equivalentes.'],
    fuente: { nombre: 'NASM · Barbell Bench Press', url: nasm('barbell-bench-press') },
  },
  {
    clave: 'lagartijas', nombre: 'Lagartijas', grupo_muscular: 'pecho', equipamiento: 'Peso corporal', material: 'Suelo estable y espacio libre.',
    objetivo: 'Empuje con el peso corporal y estabilidad del tronco.', dificultad: 'Ajusta la variante a tu control del cuerpo.', vista: 'Lateral',
    inicio: 'Coloca las manos algo más abiertas que los hombros. Apoya las puntas de los pies y alinea cabeza, tronco y piernas.',
    fases: [ ['Alinea', 'Activa el abdomen y mantén el cuello siguiendo la línea de la espalda.'], ['Baja', 'Flexiona los codos en diagonal hacia atrás, acercando el pecho al suelo con control.'], ['Sube', 'Empuja el suelo y eleva el cuerpo como una unidad.'] ],
    claves: ['Mueve hombros y caderas juntos.', 'Usa un recorrido que puedas controlar.'],
    errores: ['Dejar caer la cadera.', 'Abrir los codos completamente hacia los lados.'],
    variantes: ['Manos sobre un apoyo elevado y estable para reducir la dificultad.'],
    alternativas: ['Press de banca: mismo patrón general de empuje, con preparación y equipo distintos.'],
    fuente: { nombre: 'NASM · Push-Up', url: nasm('push-up') },
  },
  {
    clave: 'remo-barra', nombre: 'Remo con barra', grupo_muscular: 'espalda', equipamiento: 'Barra y discos', material: 'Barra, discos y espacio libre.',
    objetivo: 'Tracción horizontal para la espalda y los brazos.', dificultad: 'Requiere dominar la bisagra de cadera; ACE lo clasifica avanzado.', vista: 'Lateral',
    inicio: 'Flexiona ligeramente las rodillas e inclina el tronco desde las caderas. Mantén la espalda estable y la barra bajo los hombros.',
    fases: [ ['Estabiliza', 'Sostén el tronco inclinado con el abdomen activo y los brazos extendidos.'], ['Acerca', 'Lleva la barra hacia el abdomen moviendo los codos hacia atrás.'], ['Devuelve', 'Extiende los brazos con control sin cambiar la inclinación del tronco.'] ],
    claves: ['Mantén el cuello alineado.', 'El tronco permanece estable durante la tracción.'],
    errores: ['Impulsarse con las caderas.', 'Redondear la espalda para alcanzar la barra.'],
    variantes: ['Distintos agarres requieren revisar la trayectoria y el control.'],
    alternativas: ['Remo con mancuerna apoyado en banca: cambia el apoyo y el trabajo por lado.'],
    fuente: { nombre: 'ACE · Bent-over Row', url: ace('12/bent-over-row') },
  },
  {
    clave: 'jalon-pecho', nombre: 'Jalón al pecho en polea', grupo_muscular: 'espalda', equipamiento: 'Polea', material: 'Polea alta con asiento y sujeción para los muslos.',
    objetivo: 'Tracción vertical para la espalda y los brazos.', dificultad: 'Aprende a ajustar la máquina antes de cargarla.', vista: 'Frontal',
    inicio: 'Ajusta el apoyo de los muslos y afirma los pies. Sujeta la barra y estabiliza el tronco con una pequeña inclinación hacia atrás.',
    fases: [ ['Ajusta', 'Comienza con los brazos arriba, sin colgarte de la zona lumbar.'], ['Tira', 'Guía los codos hacia abajo y acerca la barra a la parte alta del pecho. Detén el descenso si los codos empiezan a ir hacia atrás.'], ['Acompaña', 'Permite que la barra suba lentamente sin soltar el control.'] ],
    claves: ['La barra pasa por delante de la cabeza.', 'Mantén casi constante la inclinación del tronco.'],
    errores: ['Tirar detrás de la nuca.', 'Balancearse o llevar los codos demasiado atrás.'],
    variantes: ['Un agarre distinto cambia el recorrido; compruébalo con quien te guía.'],
    alternativas: ['Dominadas: tracción vertical con mayor demanda relativa y otro apoyo.'],
    fuente: { nombre: 'ACE · Seated Lat Pulldown', url: ace('158/seated-lat-pulldown') },
  },
  {
    clave: 'sentadilla', nombre: 'Sentadilla con barra', grupo_muscular: 'pierna', equipamiento: 'Barra y discos', material: 'Rack, barra, discos y seguros ajustados a la altura adecuada.',
    objetivo: 'Extensión de rodillas y caderas para el tren inferior.', dificultad: 'Requiere práctica previa sin carga y manejo del rack.', vista: 'Lateral',
    inicio: 'Apoya la barra en la parte alta de la espalda, fuera del cuello. Afirma los pies y prepara el abdomen antes de salir del rack.',
    fases: [ ['Prepara', 'Estabiliza la barra y distribuye el apoyo sobre el pie completo.'], ['Desciende', 'Flexiona caderas y rodillas juntas, con las rodillas siguiendo la dirección de los pies.'], ['Asciende', 'Empuja el suelo y vuelve a erguirte manteniendo el control del tronco.'] ],
    claves: ['La profundidad depende de tu movilidad y control.', 'Mantén los talones apoyados.'],
    errores: ['Forzar profundidad perdiendo la posición de la espalda.', 'Perder el apoyo del pie o dejar caer las rodillas hacia dentro.'],
    variantes: ['Sentadilla sin carga para practicar el patrón antes de añadir peso.'],
    alternativas: ['Prensa: requiere ajustes propios y no reproduce toda la demanda de estabilidad.'],
    fuente: { nombre: 'NASM · Squats and Deadlifts, páginas 6–8', url: 'https://trainer.nasm.org/hubfs/NASM_Free%20Guide_Squats%20and%20Deadlifts.pdf?hsLang=en' },
  },
  {
    clave: 'zancadas', nombre: 'Zancadas con mancuernas', grupo_muscular: 'pierna', equipamiento: 'Mancuernas', material: 'Mancuernas y suelo despejado, firme y antideslizante.',
    objetivo: 'Trabajo de piernas por lado con control del equilibrio.', dificultad: 'Practica primero el paso sin mancuernas.', vista: 'Lateral',
    inicio: 'De pie, sujeta las mancuernas a los lados. Da un paso al frente con anchura suficiente para mantener el equilibrio.',
    fases: [ ['Da el paso', 'Apoya el pie delantero y conserva el tronco estable.'], ['Desciende', 'Flexiona ambas rodillas sin golpear el suelo con la de atrás.'], ['Regresa', 'Empuja con la pierna delantera para volver con control.'] ],
    claves: ['La rodilla sigue la dirección del pie.', 'Mantén espacio lateral entre ambos apoyos.'],
    errores: ['Cruzar los pies como sobre una cuerda.', 'Dejar caer el cuerpo o impulsarse sin control.'],
    variantes: ['Zancada sin carga para aprender el recorrido.'],
    alternativas: ['Sentadilla: apoyo bilateral; no sustituye automáticamente el trabajo por lado.'],
    fuente: { nombre: 'ACE · Forward Lunge y progresión con mancuernas', url: 'https://www.acefitness.org/resources/everyone/blog/5032/try-this-fat-burning-leg-workout/' },
  },
  {
    clave: 'talones', nombre: 'Elevación de talones de pie', grupo_muscular: 'pierna', equipamiento: 'Peso corporal', material: 'Suelo plano y un apoyo estable si necesitas equilibrio.',
    objetivo: 'Elevación del talón mediante los músculos de la pantorrilla.', dificultad: 'Puede practicarse sin carga y con apoyo.', vista: 'Lateral',
    inicio: 'Ponte erguido, con los pies separados de forma cómoda. Usa un apoyo fijo si te cuesta equilibrarte.',
    fases: [ ['Apoya', 'Distribuye el peso y mantén las rodillas estables.'], ['Eleva', 'Levanta los talones de forma suave, sin girar los tobillos.'], ['Desciende', 'Baja los talones lentamente hasta el suelo.'] ],
    claves: ['Sube y baja con control.', 'Evita convertirlo en pequeños saltos.'],
    errores: ['Rebotar.', 'Perder el equilibrio por añadir carga antes de dominar el gesto.'],
    variantes: ['Con apoyo de una silla firme para estabilizarse.'],
    alternativas: ['La versión con mancuernas añade resistencia; requiere reevaluar la carga.'],
    fuente: { nombre: 'Mayo Clinic · Calf raise', url: 'https://www.mayoclinic.org/healthy-lifestyle/fitness/multimedia/calf-raise/vid-20084681' },
  },
  {
    clave: 'laterales', nombre: 'Elevaciones laterales con mancuernas', grupo_muscular: 'hombro', equipamiento: 'Mancuernas', material: 'Dos mancuernas que puedas mover sin impulso.',
    objetivo: 'Elevación lateral del brazo para los deltoides.', dificultad: 'Prioriza control con una carga manejable.', vista: 'Frontal',
    inicio: 'De pie, sostiene las mancuernas junto a los muslos con los codos ligeramente flexionados y las muñecas alineadas.',
    fases: [ ['Estabiliza', 'Afirma el abdomen y mantén el cuello relajado.'], ['Eleva', 'Lleva los brazos hacia los lados hasta aproximadamente la altura de los hombros.'], ['Baja', 'Vuelve lentamente a los costados sin dejar caer las mancuernas.'] ],
    claves: ['Codos y brazos suben juntos.', 'Evita el gesto de verter una jarra con los pulgares hacia abajo.'],
    errores: ['Balancear el tronco.', 'Encoger los hombros o forzar la altura.'],
    variantes: ['Sentado, con una posición estable y un rango cómodo.'],
    alternativas: ['Elevación en polea: resistencia y ajuste diferentes.'],
    fuente: { nombre: 'ACE · Lateral Raise', url: ace('26/lateral-raise') },
  },
  {
    clave: 'curl-barra', nombre: 'Curl de bíceps con barra', grupo_muscular: 'brazo', equipamiento: 'Barra y discos', material: 'Barra y carga manejable con un agarre cómodo.',
    objetivo: 'Flexión de codo para los bíceps.', dificultad: 'Aprende a separar el movimiento del codo del balanceo del cuerpo.', vista: 'Lateral',
    inicio: 'De pie, toma la barra con las palmas hacia delante, los codos junto al tronco y las muñecas alineadas.',
    fases: [ ['Prepara', 'Estabiliza el tronco y deja la barra delante de los muslos.'], ['Flexiona', 'Acerca la barra hacia los hombros doblando los codos sin impulsar la cadera.'], ['Extiende', 'Baja con control sin forzar la extensión del codo.'] ],
    claves: ['Mantén el brazo superior estable.', 'Elige una carga que no te obligue a inclinarte.'],
    errores: ['Lanzar la barra con el cuerpo.', 'Doblar las muñecas o adelantar mucho los codos.'],
    variantes: ['Barra EZ: cambia el agarre y debe resultar cómoda.'],
    alternativas: ['Curl con mancuernas: permite ajustar cada agarre por separado.'],
    fuente: { nombre: 'NASM · Barbell Bicep Curl', url: nasm('barbell-bicep-curl') },
  },
  {
    clave: 'plancha', nombre: 'Plancha frontal', grupo_muscular: 'abdomen', equipamiento: 'Peso corporal', material: 'Suelo firme o colchoneta antideslizante.',
    objetivo: 'Estabilidad del tronco resistiendo la extensión lumbar.', dificultad: 'La calidad de la posición determina cuánto puedes sostenerla.', vista: 'Lateral', esIsometrico: true,
    inicio: 'Apoya los antebrazos con los codos bajo los hombros y las puntas de los pies. Prepara el abdomen antes de elevarte.',
    fases: [ ['Colócate', 'Alinea cabeza, tronco y piernas sin dejar caer la zona lumbar.'], ['Sostén', 'Conserva la posición mientras respiras de forma continua.'], ['Descansa', 'Apoya las rodillas para salir con control.'] ],
    claves: ['Es una posición sostenida, no repeticiones de subir y bajar.', 'Termina cuando ya no puedas mantener la alineación.'],
    errores: ['Hundirse en la zona lumbar.', 'Elevar demasiado la cadera o contener la respiración.'],
    variantes: ['Rodillas apoyadas para reducir la palanca.'],
    alternativas: ['Plancha con brazos extendidos: cambia los apoyos y su exigencia.'],
    fuente: { nombre: 'NASM · Plank', url: nasm('plank') },
  },
].map(ficha => ({ ...ficha, version: '0.1.1', preparadaEl: '2026-10-30',
  autoria: 'Senda · redacción e ilustración vectorial originales', licencia: 'Mismas condiciones de uso que el código del proyecto; sin recursos gráficos de terceros.',
  validacion: { estado: 'pendiente', responsable: null, fecha: null },
}))

// No se utilizan IDs supuestos, coincidencias parciales ni similitud de nombres.
export function fichaPara(ejercicio) {
  // El catálogo devuelve la clave; la API de sesión devuelve su etiqueta.
  const grupo = Object.hasOwn(GRUPOS, ejercicio.grupo_muscular) ? ejercicio.grupo_muscular
    : Object.keys(GRUPOS).find(clave => GRUPOS[clave] === ejercicio.grupo_muscular)
  return FICHAS.find(f => f.nombre === ejercicio.nombre && f.grupo_muscular === grupo && f.equipamiento === ejercicio.equipamiento) ?? null
}

export function animacionPublicable(ficha) {
  return ficha?.validacion.estado === 'revisada' && Boolean(ficha.validacion.responsable && ficha.validacion.fecha)
}

export function filtrarEjercicios(ejercicios, { busqueda = '', grupo = '', equipo = '', soloGuias = false } = {}) {
  const normalizar = texto => texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
  const palabras = normalizar(busqueda.trim()).split(/\s+/).filter(Boolean)
  return ejercicios.filter(e => e.disponible_localmente && (!grupo || e.grupo_muscular === grupo) && (!equipo || e.equipamiento === equipo)
    && (!soloGuias || fichaPara(e)) && palabras.every(p => normalizar(`${e.nombre} ${e.equipamiento} ${GRUPOS[e.grupo_muscular] ?? ''}`).includes(p)))
}
