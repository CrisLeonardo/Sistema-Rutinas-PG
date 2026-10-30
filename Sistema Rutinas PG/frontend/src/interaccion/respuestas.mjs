import { trazosCaminoSVG } from '../marca/identidad.mjs'
/** Funciones puras para respuestas de interfaz; no conceden puntos ni guardan datos. */
export function segundosRestantes(venceEn, ahora = Date.now()) {
  return Math.max(0, Math.ceil((venceEn - ahora) / 1000))
}

export function vibracionHabilitada(valorGuardado) {
  return valorGuardado === 'encendida'
}

export function textoConfirmacionSerie(nombre, numero, hecha) {
  return hecha
    ? `${nombre}, serie ${numero} anotada en este dispositivo. Guarde la sesión al terminar.`
    : `${nombre}, serie ${numero} desmarcada.`
}

/** Copia únicamente los aportes que se muestran al comparar, sin referencias mutables. */
export function compararComidas(antes, despues, dia, tiempo) {
  const resumir = comida => ({
    ...Object.fromEntries(['receta', 'energia_kcal', 'proteina_g', 'carbohidrato_g', 'grasa_g', 'costo_quetzales'].map(k => [k, comida[k] ?? null])),
    porciones: (comida.porciones ?? []).map(p => ({ nombre: p.nombre, gramos: p.gramos, estado: p.estado })),
  })
  return { dia, tiempo, antes: resumir(antes), despues: resumir(despues) }
}

const escapar = texto => texto.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' })[c])

/** Lista de inclusión deliberada: la tarjeta nunca copia medidas, cuenta o historial. */
export function crearTarjetaLogro(logro) {
  if (logro?.obtenido !== true || typeof logro.nombre !== 'string' || !logro.nombre.trim()) {
    throw new Error('Solo se puede preparar una tarjeta de una insignia conseguida.')
  }
  const nombre = logro.nombre.replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 100)
  const palabras = nombre.split(' ')
  const lineas = []
  for (const palabra of palabras) {
    const fragmentos = palabra.match(/.{1,22}/gu) ?? []
    for (const fragmento of fragmentos) {
      if (!lineas.length || `${lineas.at(-1)} ${fragmento}`.length > 22) lineas.push(fragmento)
      else lineas[lineas.length - 1] += ` ${fragmento}`
    }
  }
  const texto = `Conseguí la insignia «${nombre}» en Senda. Un paso a la vez.`
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="440" viewBox="0 0 600 440" role="img" aria-labelledby="titulo">
<title id="titulo">Insignia conseguida: ${escapar(nombre)}</title>
<rect width="600" height="440" rx="28" fill="#f6f3eb"/>
  <g transform="translate(226 22) scale(.65)">${trazosCaminoSVG()}</g>
<path d="M266 84l34 18 34-18v56l-34 24-34-24z" fill="#244b3b"/>
<circle cx="300" cy="119" r="10" fill="#e8bd65"/>
<g fill="#233d32" font-family="Arial,sans-serif" text-anchor="middle">
<text x="312" y="54" font-size="26" font-weight="bold">senda.</text>
<text x="300" y="196" font-size="16">INSIGNIA CONSEGUIDA</text>
${lineas.slice(0, 5).map((l, i) => `<text x="300" y="${236 + i * 28}" font-size="24" font-weight="bold">${escapar(l)}</text>`).join('')}
<text x="300" y="405" font-size="16">Un paso a la vez. A tu manera.</text>
</g></svg>`
  return { svg, texto, nombreArchivo: 'senda-insignia.svg' }
}
