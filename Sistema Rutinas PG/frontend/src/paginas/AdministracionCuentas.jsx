/**
 * Administración de cuentas y roles, reservada al administrador (historia HU-03).
 *
 * La tabla se conserva —es lo que hace falta para revisar muchas cuentas de una
 * vez— pero pasa al armazón de escritorio, con una fila de cifras arriba que
 * responde de un vistazo cuántas cuentas hay, cuántas administran y cuántas
 * están desactivadas.
 *
 * Se mantiene la regla de no poder desactivar la cuenta con la que se inició
 * sesión: un administrador que se desactiva a sí mismo deja el sistema sin quien
 * lo administre.
 */

import { useCallback, useEffect, useState } from 'react'

import ArmazonAdmin from '../componentes/ArmazonAdmin.jsx'
import AvisoDeError from '../componentes/AvisoDeError.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioUsuarios } from '../servicios/api.js'

const COLUMNAS = '1.6fr 2fr 1.4fr 1fr 1fr'
const TREINTA_DIAS = 30 * 86_400_000

export default function AdministracionCuentas() {
  const { token, usuario } = useSesion()

  const [cuentas, setCuentas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [aviso, setAviso] = useState(null)
  const [enProceso, setEnProceso] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      setCuentas(await servicioUsuarios.listar(token))
    } catch (fallo) {
      setError(fallo.message)
    } finally {
      setCargando(false)
    }
  }, [token])

  useEffect(() => {
    cargar()
  }, [cargar])

  /** Ejecuta una operación sobre una cuenta y refleja el resultado en la tabla. */
  const operar = async (id, accion, mensajeExito) => {
    setEnProceso(id)
    setError(null)
    setAviso(null)
    try {
      const actualizada = await accion()
      setCuentas((anteriores) =>
        anteriores.map((cuenta) => (cuenta.id === actualizada.id ? actualizada : cuenta)),
      )
      setAviso(mensajeExito)
    } catch (fallo) {
      setError(fallo.message)
    } finally {
      setEnProceso(null)
    }
  }

  const cambiarRol = (cuenta, rol) =>
    operar(
      cuenta.id,
      () => servicioUsuarios.cambiarRol(cuenta.id, rol, token),
      `Se actualizó el rol de ${cuenta.correo}.`,
    )

  const cambiarEstado = (cuenta) =>
    operar(
      cuenta.id,
      () => servicioUsuarios.cambiarEstado(cuenta.id, !cuenta.activo, token),
      `La cuenta ${cuenta.correo} quedó ${cuenta.activo ? 'desactivada' : 'activada'}.`,
    )

  const administradores = cuentas.filter((cuenta) => cuenta.rol === 'administrador').length
  const desactivadas = cuentas.filter((cuenta) => !cuenta.activo).length
  const conAccesoReciente = cuentas.filter(
    (cuenta) =>
      cuenta.ultimo_acceso && Date.now() - new Date(cuenta.ultimo_acceso).getTime() < TREINTA_DIAS,
  ).length

  return (
    <ArmazonAdmin
      titulo="Cuentas"
      explicacion="Asigne roles y controle qué cuentas pueden administrar los catálogos."
      accion={
        <button
          type="button"
          className="boton boton--secundario boton--compacto"
          onClick={cargar}
          disabled={cargando}
        >
          Actualizar
        </button>
      }
    >
      {error && <AvisoDeError mensaje={error} alReintentar={cargar} />}
      {aviso && (
        <p className="aviso aviso--ok" role="status">
          {aviso}
        </p>
      )}

      <div className="cifras cifras--envuelve">
        <div className="cifras__columna">
          <span className="cifras__valor">{cuentas.length}</span>
          <span className="cifras__rotulo">cuentas registradas</span>
        </div>
        <div className="cifras__columna">
          <span className="cifras__valor">{conAccesoReciente}</span>
          <span className="cifras__rotulo">con acceso en los últimos 30 días</span>
        </div>
        <div className="cifras__columna">
          <span className="cifras__valor">{administradores}</span>
          <span className="cifras__rotulo">administradores</span>
        </div>
        <div className="cifras__columna">
          <span className="cifras__valor">{desactivadas}</span>
          <span className="cifras__rotulo">desactivadas</span>
        </div>
      </div>

      {cargando ? (
        <div className="pila-3" aria-busy="true">
          <div className="esqueleto esqueleto--fila" />
          <div className="esqueleto esqueleto--fila" />
          <div className="esqueleto esqueleto--fila" />
          <span className="solo-lectores">Cargando las cuentas…</span>
        </div>
      ) : (
        <div className="tabla">
          <div className="tabla__desplazamiento">
            <div className="tabla__cabecera" style={{ gridTemplateColumns: COLUMNAS }}>
              <span>Nombre</span>
              <span>Correo</span>
              <span>Rol</span>
              <span>Estado</span>
              <span className="tabla__numero">Acciones</span>
            </div>

            {cuentas.map((cuenta) => {
              const esPropia = cuenta.id === usuario?.id
              const ocupada = enProceso === cuenta.id
              return (
                <div
                  key={cuenta.id}
                  className={`tabla__fila${cuenta.activo ? '' : ' tabla__fila--baja'}`}
                  style={{ gridTemplateColumns: COLUMNAS }}
                >
                  <span className="fila">
                    <span>{cuenta.nombre}</span>
                    {esPropia && <span className="chip chip--info">USTED</span>}
                  </span>
                  <span className="mono lista__detalle">{cuenta.correo}</span>
                  <span>
                    <select
                      className="selector-rol"
                      value={cuenta.rol}
                      onChange={(evento) => cambiarRol(cuenta, evento.target.value)}
                      disabled={ocupada}
                      aria-label={`Rol de ${cuenta.correo}`}
                    >
                      <option value="usuario">Usuario deportista</option>
                      <option value="administrador">Administrador</option>
                    </select>
                  </span>
                  <span>
                    <span className={`chip ${cuenta.activo ? 'chip--ok' : 'chip--neutro'}`}>
                      {cuenta.activo ? 'Activa' : 'Desactivada'}
                    </span>
                  </span>
                  <span className="tabla__acciones">
                    <button
                      type="button"
                      className={`boton-texto${cuenta.activo ? ' boton-texto--peligro' : ''}`}
                      onClick={() => cambiarEstado(cuenta)}
                      disabled={ocupada || esPropia}
                      title={
                        esPropia ? 'No puede desactivar la cuenta con la que inició sesión' : ''
                      }
                    >
                      {cuenta.activo ? 'Desactivar' : 'Activar'}
                    </button>
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </ArmazonAdmin>
  )
}
