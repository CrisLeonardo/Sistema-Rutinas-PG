// Camino, elegido por el autor el 30-10-2026. Geometría original del prototipo.
export const VERSION_MARCA = 'camino-1'
export const TRAZO_CAMINO = 'M10 36h14a8 8 0 0 0 0-16h-1a5 5 0 0 1 0-10h15'
export const FLECHA_CAMINO = 'm32 5 7 5-7 5'
export const COLOR_MARCA = '#244b3b'
export const FONDO_MARCA = '#f6f3eb'

export function trazosCaminoSVG(color = COLOR_MARCA) {
  return `<path d="${TRAZO_CAMINO}" fill="none" stroke="${color}" stroke-width="7" stroke-linecap="round"/><path d="${FLECHA_CAMINO}" fill="none" stroke="${color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>`
}

export function iconoSendaSVG({ maskable = false } = {}) {
  // La figura queda dentro del círculo central del 80 % para iconos maskable.
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" role="img" aria-label="Senda, símbolo Camino"><rect width="512" height="512" rx="${maskable ? 0 : 96}" fill="${FONDO_MARCA}"/><g transform="translate(76 76) scale(7.5)">${trazosCaminoSVG()}</g></svg>`
}
