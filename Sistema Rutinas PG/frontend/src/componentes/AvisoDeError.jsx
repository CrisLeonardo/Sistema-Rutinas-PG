/**
 * Error de red o del servidor.
 *
 * Muestra el mensaje que el servidor destinó al usuario y ofrece volver a
 * intentarlo. Sin el botón, la única salida era recargar la página, y sobre una
 * conexión móvil intermitente eso significa perder el sitio donde se estaba.
 */
export default function AvisoDeError({ mensaje, alReintentar }) {
  return (
    <div className="pila-3">
      <p className="aviso aviso--peligro" role="alert">
        {mensaje}
      </p>
      {alReintentar && (
        <button type="button" className="boton boton--secundario" onClick={alReintentar}>
          Reintentar
        </button>
      )}
    </div>
  )
}
