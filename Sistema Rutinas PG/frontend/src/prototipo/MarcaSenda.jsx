import { TRAZO_CAMINO, FLECHA_CAMINO } from '../marca/identidad.mjs'
/** Dibujos propios. Camino comparte la geometría aprobada con la aplicación. */
export function SimboloSenda({ variante = 'camino', ...props }) {
  return (
    <svg viewBox="0 0 48 48" fill="none" aria-hidden="true" {...props}>
      {variante === 'camino' && <>
        <path d={TRAZO_CAMINO} stroke="currentColor" strokeWidth="7" strokeLinecap="round" />
        <path d={FLECHA_CAMINO} stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
      </>}
      {variante === 'paso' && <>
        <circle cx="30" cy="9" r="5" fill="currentColor" />
        <path d="m13 21 10-5 8 8 8-1M25 18l-5 13-9 7m10-9 10 3 3 8" stroke="currentColor" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
      </>}
      {variante === 'cumbre' && <>
        <path d="M8 37 23 10l17 27M16 24l8 5 8-5" stroke="currentColor" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M23 37h9" stroke="currentColor" strokeWidth="6" strokeLinecap="round" />
      </>}
    </svg>
  )
}

export function MarcaSenda({ variante = 'camino' }) {
  return <span className="s1-marca"><SimboloSenda variante={variante} /><span>senda<span className="s1-marca-punto">.</span></span></span>
}

export function Icono({ nombre, ...props }) {
  const trazos = {
    flecha: <path d="M5 12h14m-6-6 6 6-6 6" />,
    atras: <path d="M19 12H5m6-6-6 6 6 6" />,
    hoy: <><path d="m3 10 9-7 9 7v10H3Z" /><path d="M9 20v-7h6v7" /></>,
    entrenar: <><path d="m7 7 10 10M3 8l5-5m8 18 5-5M5 10l5-5m4 14 5-5" /></>,
    comer: <><path d="M7 3v7m-3-7v5a3 3 0 0 0 6 0V3M7 11v10m11 0V3c-5 3-5 10 0 10" /></>,
    avance: <><path d="M4 20h16M7 16v-5m5 5V7m5 9V3" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    reloj: <><circle cx="12" cy="12" r="9" /><path d="M12 6v6l4 2" /></>,
    sol: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1" /></>,
  }
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{trazos[nombre] || trazos.flecha}</svg>
}

/** Ilustración conceptual de progreso, sin prometer resultados medidos. */
export function PaisajeSenda() {
  return <svg className="s1-paisaje" viewBox="0 0 600 560" fill="none" role="img" aria-label="Un camino curvo asciende entre colinas hacia el sol">
    <circle cx="410" cy="115" r="67" fill="var(--s1-sol)" />
    <path d="M0 250C100 160 188 166 299 258c100 83 203-68 301-67v369H0Z" fill="var(--s1-colina-lejos)" />
    <path d="M0 338c142-77 203-27 290-13 125 21 208-106 310-40v275H0Z" fill="var(--s1-colina)" />
    <path d="M0 464c110-104 227-72 328-33 114 44 211-29 272-45v174H0Z" fill="var(--s1-bosque)" />
    <path d="M235 560c-60-100 158-100 146-177-10-61-177-43-175-94 2-40 148-30 151-68 2-25-31-32-36-34" stroke="var(--s1-camino)" strokeWidth="32" />
    <path d="M235 560c-60-100 158-100 146-177-10-61-177-43-175-94 2-40 148-30 151-68 2-25-31-32-36-34" stroke="var(--s1-bosque)" strokeOpacity=".4" strokeWidth="2" strokeDasharray="5 8" />
    <path d="m91 360 18-50 18 50m-18-18v37M460 375l23-64 23 64m-23-26v44" stroke="var(--s1-camino)" strokeOpacity=".65" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
    <circle cx="326" cy="369" r="10" fill="var(--s1-sol)" />
    <path d="m324 387-9 23 19 13m-14-23 22 3 9-13m-34 21-13 19m29-9 7 17" stroke="var(--s1-camino)" strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" />
    <path d="m42 100 11-5 11 5m118-37 11-5 11 5" stroke="var(--s1-bosque)" strokeWidth="2" strokeLinecap="round" />
  </svg>
}
