/** Mensaje persistente: permanece disponible para leerlo sin una cuenta atrás. */
export default function RespuestaAccion({ mensaje, children }) {
  return <div className="respuesta-accion" role="status" aria-live="polite" aria-atomic="true">
    <span aria-hidden="true" className="respuesta-accion__marca">✓</span>
    <div>{mensaje}{children}</div>
  </div>
}
