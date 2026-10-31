// Proyecciones gráficas originales. No son mediciones ni validación biomecánica.
const erguido = { hombro: [201, 79], cadera: [201, 157], pie: [201, 263], pieTrasero: [192, 263], mano: [208, 153] }
const plantillas = {
  'press-inclinado': [
    { hombro: [163, 134], cadera: [215, 183], pie: [271, 263], pieTrasero: [260, 263], mano: [192, 145] },
    { hombro: [163, 134], cadera: [215, 183], pie: [271, 263], pieTrasero: [260, 263], mano: [185, 65] },
  ],
  aperturas: [
    { hombro: [210, 145], cadera: [210, 177], pie: [233, 263], pieTrasero: [187, 263], mano: [223, 73] },
    { hombro: [210, 145], cadera: [210, 177], pie: [233, 263], pieTrasero: [187, 263], mano: [304, 145] },
  ],
  'remo-mancuerna': [
    { hombro: [232, 120], cadera: [174, 163], pie: [185, 263], pieTrasero: [113, 184], mano: [250, 192] },
    { hombro: [232, 120], cadera: [174, 163], pie: [185, 263], pieTrasero: [113, 184], mano: [208, 167] },
  ],
  dominadas: [
    { hombro: [210, 104], cadera: [210, 168], pie: [224, 244], pieTrasero: [196, 244], mano: [248, 46] },
    { hombro: [210, 56], cadera: [210, 120], pie: [224, 196], pieTrasero: [196, 196], mano: [248, 46] },
  ],
  prensa: [
    { hombro: [130, 169], cadera: [177, 217], pie: [233, 191], pieTrasero: [227, 188], mano: [153, 222] },
    { hombro: [130, 169], cadera: [177, 217], pie: [263, 165], pieTrasero: [257, 162], mano: [153, 222] },
  ],
  'peso-muerto-rumano': [erguido, { hombro: [237, 123], cadera: [176, 164], pie: [201, 263], pieTrasero: [192, 263], mano: [231, 196] }],
  'press-militar': [
    { hombro: [201, 106], cadera: [201, 184], pie: [220, 263], pieTrasero: [188, 263], mano: [227, 108] },
    { hombro: [201, 106], cadera: [201, 184], pie: [220, 263], pieTrasero: [188, 263], mano: [216, 38] },
  ],
  pajaros: [
    { hombro: [210, 115], cadera: [210, 174], pie: [231, 263], pieTrasero: [189, 263], mano: [250, 187] },
    { hombro: [210, 115], cadera: [210, 174], pie: [231, 263], pieTrasero: [189, 263], mano: [304, 119] },
  ],
  'press-arnold': [
    { hombro: [210, 110], cadera: [210, 188], pie: [233, 263], pieTrasero: [187, 263], mano: [213, 121] },
    { hombro: [210, 110], cadera: [210, 188], pie: [233, 263], pieTrasero: [187, 263], mano: [246, 44] },
  ],
  'curl-alterno': [{ hombro: [210, 104], cadera: [210, 182], pie: [233, 263], pieTrasero: [187, 263], mano: [230, 180] }],
  'triceps-polea': [{ hombro: [201, 106], cadera: [201, 184], pie: [220, 263], pieTrasero: [188, 263], mano: [244, 125] }],
  'fondos-bancas': [
    { hombro: [177, 108], cadera: [193, 183], pie: [284, 219], pieTrasero: [277, 219], mano: [149, 149] },
    { hombro: [177, 136], cadera: [193, 211], pie: [284, 219], pieTrasero: [277, 219], mano: [149, 149] },
  ],
  abdominales: [
    { hombro: [137, 250], cadera: [214, 253], pie: [290, 263], pieTrasero: [282, 263], mano: [172, 244] },
    { hombro: [150, 218], cadera: [214, 253], pie: [290, 263], pieTrasero: [282, 263], mano: [183, 230] },
  ],
  rueda: [
    { hombro: [167, 183], cadera: [211, 203], pie: [295, 263], pieTrasero: [288, 263], mano: [137, 252] },
    { hombro: [145, 203], cadera: [211, 228], pie: [295, 263], pieTrasero: [288, 263], mano: [91, 252] },
  ],
  'piernas-colgado': [
    { hombro: [201, 104], cadera: [201, 166], pie: [210, 245], pieTrasero: [203, 245], mano: [210, 46] },
    { hombro: [201, 104], cadera: [201, 166], pie: [279, 174], pieTrasero: [272, 174], mano: [210, 46] },
  ],
}
export const CLAVES_ADICIONALES = Object.keys(plantillas)
const interpolar = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t)
const polar = (origen, largo, angulo) => [origen[0] + largo * Math.cos(angulo), origen[1] + largo * Math.sin(angulo)]

export function poseAdicional(clave, p, articulacion) {
  const estados = plantillas[clave]
  if (!estados) return null
  const recorrido = p <= .5 ? p * 2 : (1 - p) * 2
  const t = (1 - Math.cos(Math.PI * recorrido)) / 2
  const pose = Object.fromEntries(Object.keys(estados[0]).map(k => [k, interpolar(estados[0][k], (estados[1] ?? estados[0])[k], t)]))
  const frontal = ['aperturas', 'dominadas', 'pajaros', 'press-arnold', 'curl-alterno'].includes(clave)
  const colgado = clave === 'dominadas' || clave === 'piernas-colgado'
  const longitudBrazo = clave === 'dominadas' ? 32 : colgado ? 30 : 38
  const { hombro, cadera, pie, pieTrasero } = pose
  const hombroDer = frontal ? [hombro[0] + 20, hombro[1]] : hombro
  const hombroIzq = frontal ? [hombro[0] - 20, hombro[1]] : [hombro[0] - 5, hombro[1] + 2]
  let mano = pose.mano
  let manoIzq = frontal ? [420 - mano[0], mano[1]] : [mano[0] - 6, mano[1] + 1]
  let codoDer, codoIzq
  if (clave === 'curl-alterno') {
    codoDer = [hombroDer[0], hombroDer[1] + 38]
    codoIzq = [hombroIzq[0], hombroIzq[1] + 38]
    // Dos flexiones sucesivas: nunca se animan ambos brazos al mismo tiempo.
    const derecha = p < .5 ? Math.sin(p * 2 * Math.PI) ** 2 : 0
    const izquierda = p >= .5 ? Math.sin((p - .5) * 2 * Math.PI) ** 2 : 0
    mano = polar(codoDer, 38, Math.PI / 2 - 2.6 * derecha)
    manoIzq = polar(codoIzq, 38, Math.PI / 2 + 2.6 * izquierda)
  }
  if (clave === 'triceps-polea') {
    codoDer = polar(hombroDer, 38, 1.33)
    codoIzq = polar(hombroIzq, 38, 1.33)
    mano = polar(codoDer, 38, -.5 + 1.95 * t)
    manoIzq = polar(codoIzq, 38, -.5 + 1.95 * t)
  }
  if (clave === 'remo-mancuerna') manoIzq = [262, 184]
  const lado = ['press-inclinado', 'abdominales'].includes(clave) ? -1 : 1
  codoDer ??= articulacion(hombroDer, mano, longitudBrazo, longitudBrazo, lado)
  codoIzq ??= articulacion(hombroIzq, manoIzq, longitudBrazo, longitudBrazo, frontal ? -1 : lado)
  const caderaDer = frontal ? [cadera[0] + 9, cadera[1]] : cadera
  const caderaIzq = frontal ? [cadera[0] - 9, cadera[1]] : [cadera[0] - 4, cadera[1]]
  const dePie = ['pajaros', 'press-arnold', 'curl-alterno', 'press-militar', 'triceps-polea'].includes(clave)
  const longitudPierna = colgado ? 40 : dePie ? Math.max(Math.hypot(pie[0] - caderaDer[0], pie[1] - caderaDer[1]), Math.hypot(pieTrasero[0] - caderaIzq[0], pieTrasero[1] - caderaIzq[1])) / 2 + .8 : 53
  const rodilla = clave === 'rueda' ? [253, 263] : articulacion(caderaDer, pie, longitudPierna, longitudPierna, -1)
  const rodillaTrasera = clave === 'remo-mancuerna' ? [153, 184] : clave === 'rueda' ? [247, 263] : articulacion(caderaIzq, pieTrasero, longitudPierna, longitudPierna, frontal ? 1 : -1)
  const dx = hombro[0] - cadera[0], dy = hombro[1] - cadera[1], largo = Math.hypot(dx, dy)
  const cabeza = [hombro[0] + dx / largo * (colgado ? 23 : 29), hombro[1] + dy / largo * (colgado ? 23 : 29)]
  return { ...pose, mano, manoIzq, cabeza, hombroDer, hombroIzq, caderaDer, caderaIzq, codoDer, codoIzq, rodilla, rodillaTrasera,
    frontal, dosLados: true, colgado, longitudBrazo, agarre: clave === 'press-arnold' ? (t < .35 ? 'Palmas hacia ti' : t > .7 ? 'Palmas al frente' : 'Giro progresivo') : null }
}
