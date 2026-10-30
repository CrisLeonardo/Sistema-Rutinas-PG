import { TRAZO_CAMINO, FLECHA_CAMINO } from '../marca/identidad.mjs'

export default function SimboloCamino(props) {
  return <svg viewBox="0 0 48 48" width="32" height="32" fill="none" aria-hidden="true" focusable="false" {...props}>
    <path d={TRAZO_CAMINO} stroke="currentColor" strokeWidth="7" strokeLinecap="round" />
    <path d={FLECHA_CAMINO} stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
}
