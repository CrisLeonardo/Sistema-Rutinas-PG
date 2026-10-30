import { renderToString } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { ProveedorPreferencias } from '../contexto/ContextoPreferencias.jsx'
import { ProveedorSesion } from '../contexto/ContextoSesion.jsx'
import SitioPublico from './SitioPublico.jsx'
export { PAGINAS_PUBLICAS } from './contenido.js'

export function renderizar(ruta) {
  return renderToString(<MemoryRouter initialEntries={[ruta]}><ProveedorPreferencias><ProveedorSesion><SitioPublico /></ProveedorSesion></ProveedorPreferencias></MemoryRouter>)
}
