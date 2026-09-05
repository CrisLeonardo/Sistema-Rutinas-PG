/**
 * Fila de ajuste con interruptor.
 *
 * La fila entera es el control: en un teléfono, apuntar a un interruptor de
 * 46×28 px con el pulgar falla más veces de las que acierta, y no hay razón
 * para que el texto que lo nombra no sirva también para accionarlo.
 */
export default function Interruptor({ etiqueta, encendido, alCambiar }) {
  return (
    <button
      type="button"
      className="lista__fila"
      role="switch"
      aria-checked={encendido}
      onClick={alCambiar}
    >
      <span className="lista__etiqueta crece">{etiqueta}</span>
      <span className={`interruptor${encendido ? ' interruptor--encendido' : ''}`}>
        <span className="interruptor__perilla" />
      </span>
    </button>
  )
}
