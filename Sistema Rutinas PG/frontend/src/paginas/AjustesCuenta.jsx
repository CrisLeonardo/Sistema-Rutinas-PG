/**
 * «Más»: la cuenta y todo lo que no se consulta a diario.
 *
 * Es el quinto destino de la barra. Recoge lo que antes estaba repartido entre
 * el menú desplegable, la tarjeta «Su cuenta» del panel y una pantalla de
 * ajustes que mezclaba los datos de la cuenta con el formulario de contraseña.
 *
 * Dos listas y nada más: a dónde se puede ir, y qué se puede cambiar. El
 * formulario de contraseña tiene pantalla propia, y la administración aparece
 * solo si la cuenta es administradora.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import Icono from '../componentes/Icono.jsx'
import Interruptor from '../componentes/Interruptor.jsx'
import { usePreferencias } from '../contexto/ContextoPreferencias.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPerfil } from '../servicios/api.js'

/** Iniciales del nombre: la marca es tipográfica y no hay fotografías. */
function iniciales(nombre) {
  if (!nombre) return '—'
  const partes = nombre.trim().split(/\s+/)
  const primera = partes[0]?.[0] ?? ''
  const segunda = partes.length > 1 ? partes[partes.length - 1][0] : ''
  return `${primera}${segunda}`.toUpperCase()
}

function fechaLegible(valor) {
  if (!valor) return 'Sin registro'
  return new Date(valor).toLocaleDateString('es-GT', { dateStyle: 'long' })
}

const ACCESOS = [
  { ruta: '/avance/medidas', etiqueta: 'Mis medidas', conPeso: true },
  { ruta: '/comer/plan', etiqueta: 'Mi plan de alimentación' },
  { ruta: '/comer/compras', etiqueta: 'Lista de compras' },
  { ruta: '/entrenar/bitacora', etiqueta: 'Mi bitácora' },
]

const ADMINISTRACION = [
  { ruta: '/admin/catalogos', etiqueta: 'Catálogos' },
  { ruta: '/admin/cuentas', etiqueta: 'Cuentas' },
]

export default function AjustesCuenta() {
  const { usuario, token, esAdministrador, cerrarSesion } = useSesion()
  const { tema, alternarTema, vibracion, alternarVibracion } = usePreferencias()
  const navegar = useNavigate()

  const [pesoVigente, setPesoVigente] = useState(null)

  const cargarPeso = useCallback(async () => {
    try {
      const vigente = await servicioPerfil.consultarVigente(token)
      setPesoVigente(vigente?.peso_kg ?? null)
    } catch (fallo) {
      // Sin medidas todavía la fila sigue existiendo: lleva al sitio donde se
      // registran. Un 404 aquí no es un fallo que haya que contar.
      if (!(fallo instanceof ErrorApi)) throw fallo
      setPesoVigente(null)
    }
  }, [token])

  useEffect(() => {
    cargarPeso()
  }, [cargarPeso])

  const salir = () => {
    cerrarSesion()
    navegar('/acceso', { replace: true })
  }

  return (
    <div className="pila-5">
      <div className="fila">
        <span className="avatar avatar--grande" aria-hidden="true">
          {iniciales(usuario?.nombre)}
        </span>
        <div className="pila-2 crece">
          <h1 className="titulo-tarjeta">{usuario?.nombre}</h1>
          <p className="apoyo">{usuario?.correo}</p>
        </div>
      </div>

      <div className="lista">
        {ACCESOS.map((acceso) => (
          <Link key={acceso.ruta} to={acceso.ruta} className="lista__fila">
            <span className="lista__etiqueta crece">{acceso.etiqueta}</span>
            {acceso.conPeso && pesoVigente !== null && (
              <span className="lista__valor lista__valor--tenue">{pesoVigente} kg</span>
            )}
            <Icono nombre="arrow-right-01" tamano={17} className="lista__chevron" />
          </Link>
        ))}
      </div>

      <div className="lista">
        <Interruptor etiqueta="Tema oscuro" encendido={tema === 'dark'} alCambiar={alternarTema} />
        <Interruptor
          etiqueta="Cronómetro con vibración"
          encendido={vibracion}
          alCambiar={alternarVibracion}
        />
        <Link to="/mas/contrasena" className="lista__fila">
          <span className="lista__etiqueta crece">Cambiar mi contraseña</span>
          <Icono nombre="arrow-right-01" tamano={17} className="lista__chevron" />
        </Link>
      </div>

      {esAdministrador && (
        <div className="lista">
          {ADMINISTRACION.map((destino) => (
            <Link key={destino.ruta} to={destino.ruta} className="lista__fila">
              <span className="lista__etiqueta crece">{destino.etiqueta}</span>
              <Icono nombre="arrow-right-01" tamano={17} className="lista__chevron" />
            </Link>
          ))}
        </div>
      )}

      <div className="bloque-tenue">
        <p className="nota-al-pie">
          Sus medidas, su plan y su avance solo los ve usted. Ni el administrador del
          sistema tiene acceso a ellos.
        </p>
        <p className="nota-al-pie mono">
          Miembro desde el {fechaLegible(usuario?.fecha_registro)}
        </p>
      </div>

      <button type="button" className="boton boton--destructivo" onClick={salir}>
        Cerrar sesión
      </button>
    </div>
  )
}
