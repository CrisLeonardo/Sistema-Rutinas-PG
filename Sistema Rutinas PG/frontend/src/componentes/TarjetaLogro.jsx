import { useCallback, useMemo, useRef, useState } from 'react'
import Hoja from './Hoja.jsx'
import { crearTarjetaLogro } from '../interaccion/respuestas.mjs'

export default function TarjetaLogro({ logro }) {
  const [abierta, setAbierta] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const disparador = useRef(null)
  const tarjeta = useMemo(() => logro.obtenido ? crearTarjetaLogro(logro) : null, [logro])
  const cerrar = useCallback(() => {
    setAbierta(false)
    requestAnimationFrame(() => disparador.current?.focus())
  }, [])
  if (!tarjeta) return null

  function descargar() {
    const url = URL.createObjectURL(new Blob([tarjeta.svg], { type: 'image/svg+xml;charset=utf-8' }))
    const enlace = document.createElement('a')
    enlace.href = url; enlace.download = tarjeta.nombreArchivo
    document.body.appendChild(enlace); enlace.click(); enlace.remove()
    setTimeout(() => URL.revokeObjectURL(url), 10_000)
    setMensaje('Tarjeta preparada para descargar. Revise la descarga de su navegador.')
  }
  async function copiar() {
    try { await navigator.clipboard.writeText(tarjeta.texto); setMensaje('Mensaje copiado. Puede pegarlo donde elija.') }
    catch { setMensaje('No se pudo copiar. Puede seleccionar el mensaje de la vista previa.') }
  }

  return <>
    <button ref={disparador} type="button" className="boton-texto" onClick={() => { setMensaje(''); setAbierta(true) }} aria-label={`Preparar tarjeta de ${logro.nombre}`}>Preparar tarjeta</button>
    {abierta && <Hoja titulo="Revise su tarjeta" descripcion="Solo incluye el nombre de la insignia y Senda. No añade nombre, medidas, cargas, calorías ni historial. Usted elige dónde compartirla." alCerrar={cerrar}>
      <img className="tarjeta-logro" src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(tarjeta.svg)}`} alt={`Vista previa: insignia ${logro.nombre}`} width="600" height="440" />
      <p className="cuerpo tarjeta-logro__mensaje">{tarjeta.texto}</p>
      <button className="boton boton--principal" onClick={descargar}>Descargar tarjeta SVG</button>
      <button className="boton boton--secundario" onClick={copiar}>Copiar mensaje</button>
      <p className="apoyo" role="status">{mensaje}</p>
    </Hoja>}
  </>
}
