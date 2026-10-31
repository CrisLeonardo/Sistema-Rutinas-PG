import { useCallback, useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import Hoja from './Hoja.jsx'
import Pildoras from './Pildoras.jsx'
import { recorridoPara } from '../datos/recorridos.mjs'

export default function ContextoPantalla() {
  const { pathname } = useLocation()
  const guia = recorridoPara(pathname)
  const [abierta, setAbierta] = useState(false)
  const cerrar = useCallback(() => setAbierta(false), [])
  useEffect(() => { setAbierta(false) }, [pathname])
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' })
    const region = document.querySelector('.vista-senda')
    if (!region) return
    const enfocar = () => {
      const destino = region.querySelector('h1, [role="alert"]')
      if (!destino) return false
      destino.setAttribute('tabindex', '-1')
      destino.focus({ preventScroll: true })
      return true
    }
    if (enfocar()) return
    const observador = new MutationObserver(() => { if (enfocar()) observador.disconnect() })
    observador.observe(region, { subtree: true, childList: true })
    const reloj = setTimeout(() => observador.disconnect(), 35_000)
    return () => { observador.disconnect(); clearTimeout(reloj) }
  }, [pathname])
  if (!guia) return null
  return <div className="contexto-pantalla no-imprimir">
    <div className="contexto-pantalla__fila">{pathname === '/panel' ? <span className="rotulo">SENDA / HOY</span> : <Link to={guia.volver}>{guia.volver === '/entrenar' ? '← Mi rutina' : guia.volver === '/mas' ? '← Mi cuenta' : '← Hoy'}</Link>}<span>{pathname === '/panel' ? 'Su recorrido personal' : guia.titulo}</span><button type="button" onClick={() => setAbierta(true)} aria-haspopup="dialog" className="ayuda-pantalla"><span aria-hidden="true">?</span>Cómo usar</button></div>
    {guia.opciones && <Pildoras etiquetaGrupo={`Secciones de ${pathname.startsWith('/comer') ? 'alimentación' : pathname.startsWith('/entrenar') ? 'entrenamiento' : 'avance'}`} opciones={guia.opciones} />}
    {abierta && <Hoja titulo={guia.resumen} alCerrar={cerrar}><ol className="ayuda-pasos">{guia.pasos.map((paso, i) => <li key={paso}><span aria-hidden="true">{i + 1}</span><p>{paso}</p></li>)}</ol><p className="apoyo">Si una consulta falla, use Reintentar en esa pantalla. Si una escritura queda sin confirmación, compruebe su resultado antes de repetirla.</p><Link to="/ayuda" className="boton-texto">Más ayuda y contacto</Link></Hoja>}
  </div>
}
