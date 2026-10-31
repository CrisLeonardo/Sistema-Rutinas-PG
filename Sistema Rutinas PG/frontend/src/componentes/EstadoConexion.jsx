import { useEffect, useState, useSyncExternalStore } from 'react'
import { Link } from 'react-router-dom'
import { conexion } from '../servicios/conexion.mjs'

export function useConexion() {
  return useSyncExternalStore(conexion.suscribir, conexion.leer, conexion.leer)
}

export default function EstadoConexion() {
  const { fase, detalle } = useConexion()
  const [mostrarEspera, setMostrarEspera] = useState(false)
  useEffect(() => { void conexion.comprobar() }, [])
  useEffect(() => {
    setMostrarEspera(false)
    if (fase !== 'conectando') return
    const reloj = setTimeout(() => setMostrarEspera(true), 4_000)
    return () => clearTimeout(reloj)
  }, [fase])
  useEffect(() => {
    const reconectar = () => { void conexion.comprobar() }
    const sinRed = () => conexion.fallo('Está sin conexión a Internet. Recupere la señal para consultar o guardar.')
    window.addEventListener('online', reconectar)
    window.addEventListener('offline', sinRed)
    return () => { window.removeEventListener('online', reconectar); window.removeEventListener('offline', sinRed) }
  }, [])
  if (fase !== 'sin-conexion' && !(fase === 'conectando' && mostrarEspera)) return null
  return <aside className="estado-conexion no-imprimir" aria-label="Conexión con Senda">
    <span className={`conexion-indicador${fase === 'conectando' ? ' conexion-indicador--espera' : ''}`} aria-hidden="true" />
    <p role="status">{fase === 'conectando' ? 'Conectando con Senda. Si el servicio necesita arrancar, puede tardar alrededor de un minuto.' : detalle}</p>
    {fase === 'sin-conexion' && <div className="estado-conexion__acciones"><button type="button" className="boton-texto" onClick={() => { void conexion.comprobar() }}>Volver a conectar</button><Link to="/ayuda">Ayuda</Link></div>}
  </aside>
}
