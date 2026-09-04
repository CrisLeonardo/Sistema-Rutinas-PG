/**
 * Lista de compras de la semana.
 *
 * El menú diario dice qué comer en cada tiempo; esta pantalla suma esa comida
 * por siete días y la agrupa por el puesto donde cada cosa se compra, con el
 * costo a la vista antes de salir de casa.
 *
 * Las cantidades vienen del servidor ya expresadas en libras, que es la unidad
 * con que se despacha en los mercados del municipio: nadie pide «1 815 gramos
 * de pollo» en un puesto.
 *
 * Los renglones se pueden ir marcando conforme se recorren los puestos. La
 * marca vive en el navegador y no en el servidor: es una ayuda para el rato que
 * dura la compra, no un dato del plan.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPlan } from '../servicios/api.js'

const CLAVE_MARCADOS = 'rutinas.compras.marcados'

function leerMarcados() {
  try {
    return new Set(JSON.parse(localStorage.getItem(CLAVE_MARCADOS) ?? '[]'))
  } catch {
    return new Set()
  }
}

function guardarMarcados(marcados) {
  try {
    localStorage.setItem(CLAVE_MARCADOS, JSON.stringify([...marcados]))
  } catch {
    // El navegador puede tener el almacenamiento bloqueado. La lista sigue
    // sirviendo sin la marca; no hay nada que informar al usuario.
  }
}

export default function ListaDeCompras() {
  const { token } = useSesion()

  const [lista, setLista] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [marcados, setMarcados] = useState(leerMarcados)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      setLista(await servicioPlan.consultarListaDeCompras(token))
      setError(null)
    } catch (fallo) {
      if (fallo instanceof ErrorApi && fallo.codigo === 404) {
        setLista(null)
        setError(null)
      } else {
        setError(fallo.message)
      }
    } finally {
      setCargando(false)
    }
  }, [token])

  useEffect(() => {
    cargar()
  }, [cargar])

  const alternar = (alimentoId) => {
    setMarcados((anterior) => {
      const siguiente = new Set(anterior)
      if (siguiente.has(alimentoId)) siguiente.delete(alimentoId)
      else siguiente.add(alimentoId)
      guardarMarcados(siguiente)
      return siguiente
    })
  }

  const limpiar = () => {
    setMarcados(new Set())
    guardarMarcados(new Set())
  }

  if (cargando) {
    return <p className="texto-ayuda">Cargando su lista…</p>
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    )
  }

  if (!lista) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center p-4">
          <h1 className="h5">Todavía no tiene lista de compras</h1>
          <p className="texto-ayuda">
            La lista se arma con el menú de su plan de alimentación.
          </p>
          <Link to="/plan-nutricional" className="btn btn-principal control-tactil">
            Generar mi plan
          </Link>
        </div>
      </div>
    )
  }

  const totalRenglones = lista.alimentos_distintos
  const completados = lista.grupos.reduce(
    (suma, grupo) =>
      suma + grupo.renglones.filter((renglon) => marcados.has(renglon.alimento_id)).length,
    0,
  )

  return (
    <div className="row g-4">
      <div className="col-12 d-flex flex-column flex-sm-row justify-content-between gap-3">
        <div>
          <h1 className="h3 mb-1">Lista de compras</h1>
          <p className="texto-ayuda mb-0">
            Todo lo que su plan necesita para una semana, agrupado por puesto.
          </p>
        </div>
        <button
          type="button"
          className="btn btn-outline-secondary control-tactil align-self-start no-imprimir"
          onClick={() => window.print()}
        >
          Imprimir
        </button>
      </div>

      <div className="col-12">
        <div className="card shadow-sm">
          <div className="card-body">
            <div className="row g-3 text-center text-sm-start">
              <div className="col-6 col-sm-4">
                <div className="texto-ayuda">Costo de la semana</div>
                <div className="h4 mb-0">
                  Q{lista.costo_total_quetzales.toFixed(2)}
                </div>
              </div>
              <div className="col-6 col-sm-4">
                <div className="texto-ayuda">Al mes</div>
                <div className="h4 mb-0">
                  Q{Math.round(lista.costo_mensual_quetzales).toLocaleString('es-GT')}
                </div>
              </div>
              <div className="col-12 col-sm-4">
                <div className="texto-ayuda">Alimentos</div>
                <div className="h4 mb-0">
                  {completados} de {totalRenglones} comprados
                </div>
              </div>
            </div>

            <div
              className="progress mt-3 no-imprimir"
              role="progressbar"
              aria-label="Avance de la compra"
              aria-valuenow={completados}
              aria-valuemin={0}
              aria-valuemax={totalRenglones}
            >
              <div
                className="progress-bar barra-avance"
                style={{
                  width: `${totalRenglones ? (completados / totalRenglones) * 100 : 0}%`,
                }}
              />
            </div>

            <p className="texto-ayuda mt-3 mb-0">{lista.aviso_costo}</p>
          </div>
        </div>
      </div>

      {lista.grupos.map((grupo) => (
        <div className="col-12 col-lg-6" key={grupo.categoria}>
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-baseline gap-2">
                <h2 className="h5 card-title mb-0">{grupo.nombre_categoria}</h2>
                <span className="texto-ayuda flex-shrink-0">
                  Q{grupo.costo_quetzales.toFixed(2)}
                </span>
              </div>

              <ul className="list-group list-group-flush mt-3">
                {grupo.renglones.map((renglon) => {
                  const comprado = marcados.has(renglon.alimento_id)
                  const identificador = `compra-${renglon.alimento_id}`
                  return (
                    <li key={renglon.alimento_id} className="list-group-item px-0">
                      <div className="form-check d-flex gap-3 align-items-start opcion-tactil mb-0">
                        <input
                          className="form-check-input flex-shrink-0"
                          type="checkbox"
                          id={identificador}
                          checked={comprado}
                          onChange={() => alternar(renglon.alimento_id)}
                        />
                        <label
                          className={`form-check-label w-100 ${comprado ? 'renglon-comprado' : ''}`}
                          htmlFor={identificador}
                        >
                          <div className="d-flex justify-content-between gap-3">
                            <span className="fw-semibold">{renglon.nombre}</span>
                            <span className="text-end flex-shrink-0">
                              <span className="fw-semibold d-block">
                                {renglon.cantidad_de_mercado}
                              </span>
                              <span className="texto-ayuda">
                                {renglon.costo_quetzales === null
                                  ? 'sin precio'
                                  : `Q${renglon.costo_quetzales.toFixed(2)}`}
                              </span>
                            </span>
                          </div>
                        </label>
                      </div>
                    </li>
                  )
                })}
              </ul>
            </div>
          </div>
        </div>
      ))}

      {completados > 0 && (
        <div className="col-12 no-imprimir">
          <button
            type="button"
            className="btn btn-outline-secondary control-tactil"
            onClick={limpiar}
          >
            Desmarcar todo
          </button>
        </div>
      )}

      <div className="col-12">
        <div className="alert alert-secondary mb-0" role="note">
          <strong>Cómo usarla.</strong> Marque cada alimento conforme lo compre. Las
          cantidades alcanzan para siete días siguiendo el menú completo; si comparte la
          comida con su familia, multiplique por las personas que van a comer lo mismo.
        </div>
      </div>
    </div>
  )
}
