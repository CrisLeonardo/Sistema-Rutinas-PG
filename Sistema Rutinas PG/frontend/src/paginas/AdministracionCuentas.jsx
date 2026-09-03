import { useCallback, useEffect, useState } from 'react'

import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioUsuarios } from '../servicios/api.js'

/** Administración de cuentas y roles, reservada al administrador (historia HU-03). */
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

  return (
    <div>
      <div className="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
        <div>
          <h1 className="h3 mb-1">Cuentas registradas</h1>
          <p className="texto-ayuda mb-0">
            Asigne roles y controle qué cuentas pueden administrar los catálogos.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-outline-secondary control-tactil"
          onClick={cargar}
          disabled={cargando}
        >
          Actualizar
        </button>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}
      {aviso && (
        <div className="alert alert-success" role="alert">
          {aviso}
        </div>
      )}

      {cargando ? (
        <p className="texto-ayuda">Cargando las cuentas…</p>
      ) : (
        <div className="card shadow-sm">
          <div className="contenedor-tabla">
            <table className="table tabla-cuentas mb-0">
              <thead className="table-light">
                <tr>
                  <th scope="col">Nombre</th>
                  <th scope="col">Correo</th>
                  <th scope="col">Rol</th>
                  <th scope="col">Estado</th>
                  <th scope="col" className="text-end">
                    Acción
                  </th>
                </tr>
              </thead>
              <tbody>
                {cuentas.map((cuenta) => {
                  const esPropia = cuenta.id === usuario?.id
                  const ocupada = enProceso === cuenta.id
                  return (
                    <tr key={cuenta.id}>
                      <td>
                        {cuenta.nombre}
                        {esPropia && <span className="badge bg-info text-dark ms-2">Usted</span>}
                      </td>
                      <td className="text-break">{cuenta.correo}</td>
                      <td>
                        <select
                          className="form-select form-select-sm control-tactil"
                          value={cuenta.rol}
                          onChange={(evento) => cambiarRol(cuenta, evento.target.value)}
                          disabled={ocupada}
                          aria-label={`Rol de ${cuenta.correo}`}
                        >
                          <option value="usuario">Usuario deportista</option>
                          <option value="administrador">Administrador</option>
                        </select>
                      </td>
                      <td>
                        <span className={`badge ${cuenta.activo ? 'bg-success' : 'bg-secondary'}`}>
                          {cuenta.activo ? 'Activa' : 'Desactivada'}
                        </span>
                      </td>
                      <td className="text-end">
                        <button
                          type="button"
                          className={`btn btn-sm control-tactil ${
                            cuenta.activo ? 'btn-outline-danger' : 'btn-outline-success'
                          }`}
                          onClick={() => cambiarEstado(cuenta)}
                          disabled={ocupada || esPropia}
                          title={
                            esPropia ? 'No puede desactivar la cuenta con la que inició sesión' : ''
                          }
                        >
                          {cuenta.activo ? 'Desactivar' : 'Activar'}
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
