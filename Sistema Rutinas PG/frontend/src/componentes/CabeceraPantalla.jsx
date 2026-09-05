/**
 * Cabecera de una pantalla interior: flecha de volver, título y, si la pantalla
 * la tiene, una sola acción a la derecha.
 *
 * La flecha lleva a la sección de la que cuelga la pantalla en vez de deshacer
 * el último paso del historial: quien llega desde un enlace directo también
 * tiene que poder subir un nivel.
 */

import { Link } from 'react-router-dom'

import Icono from './Icono.jsx'

export default function CabeceraPantalla({ titulo, hacia, apoyo, accion }) {
  return (
    <div className="pila-2">
      <div className="cabecera-pantalla">
        {hacia && (
          <Link to={hacia} className="cabecera-pantalla__volver" aria-label="Volver">
            <Icono nombre="arrow-left-01" tamano={20} />
          </Link>
        )}
        <h1 className="titulo-pantalla crece">{titulo}</h1>
        {accion}
      </div>
      {apoyo && <p className="apoyo">{apoyo}</p>}
    </div>
  )
}
