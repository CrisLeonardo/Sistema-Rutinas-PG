/**
 * Pantalla del menú diario (historia HU-08).
 *
 * Presenta el reparto del plan en los cinco tiempos de comida, con las
 * cantidades en gramos y también en medidas caseras, porque la mayoría de los
 * hogares del municipio no dispone de báscula de cocina. Cada porción muestra
 * su alternativa de aporte equivalente, para los días en que el alimento
 * principal no se consigue.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPlan } from '../servicios/api.js'

export default function MenuDiario() {
  const { token } = useSesion()

  const [menu, setMenu] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [sustitutosVisibles, setSustitutosVisibles] = useState({})

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      setMenu(await servicioPlan.consultarMenu(token))
      setError(null)
    } catch (fallo) {
      if (fallo instanceof ErrorApi && fallo.codigo === 404) {
        setMenu(null)
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

  const alternar = (identificador) => {
    setSustitutosVisibles((anterior) => ({
      ...anterior,
      [identificador]: !anterior[identificador],
    }))
  }

  if (cargando) {
    return <p className="texto-ayuda">Cargando su menú…</p>
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    )
  }

  if (!menu) {
    return (
      <div className="card shadow-sm">
        <div className="card-body text-center p-4">
          <h1 className="h5">Todavía no tiene menú</h1>
          <p className="texto-ayuda">
            Su menú se arma junto con su plan de alimentación.
          </p>
          <Link to="/plan-nutricional" className="btn btn-principal control-tactil">
            Generar mi plan
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="row g-4">
      <div className="col-12">
        <h1 className="h3 mb-1">Qué comer cada día</h1>
        <p className="texto-ayuda mb-0">
          Un reparto de su plan en cinco tiempos, con alimentos que se consiguen en el
          municipio. Las cantidades están en gramos y en medidas de cocina.
        </p>
      </div>

      <div className="col-12">
        <div className="card shadow-sm">
          <div className="card-body">
            <div className="row g-3 text-center text-sm-start">
              <div className="col-6 col-sm-3">
                <div className="texto-ayuda">Energía del menú</div>
                <div className="h4 mb-0">{menu.energia_kcal} kcal</div>
              </div>
              <div className="col-6 col-sm-3">
                <div className="texto-ayuda">Su plan pide</div>
                <div className="h4 mb-0">{Math.round(menu.energia_objetivo_kcal)} kcal</div>
              </div>
              <div className="col-6 col-sm-3">
                <div className="texto-ayuda">Proteína</div>
                <div className="h4 mb-0">{menu.proteina_g} g</div>
              </div>
              <div className="col-6 col-sm-3">
                <div className="texto-ayuda">Alimentos distintos</div>
                <div className="h4 mb-0">{menu.alimentos_distintos}</div>
              </div>
            </div>
            <p className="texto-ayuda mt-3 mb-0">
              El menú queda a {menu.desviacion_energia_porcentaje} % de lo que su plan
              pide. Esa diferencia viene de redondear las porciones a cantidades que se
              puedan servir.
            </p>
          </div>
        </div>
      </div>

      {menu.tiempos.map((tiempo) => (
        <div className="col-12 col-lg-6" key={tiempo.nombre}>
          <div className="card shadow-sm h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-baseline gap-2">
                <h2 className="h5 card-title mb-0">{tiempo.nombre}</h2>
                <span className="texto-ayuda flex-shrink-0">
                  {tiempo.energia_kcal} kcal · {tiempo.proteina_g} g proteína
                </span>
              </div>

              <ul className="list-group list-group-flush mt-3">
                {tiempo.porciones.map((porcion) => {
                  const clave = `${tiempo.nombre}-${porcion.alimento_id}`
                  const visible = sustitutosVisibles[clave]
                  return (
                    <li key={clave} className="list-group-item px-0">
                      <div className="d-flex justify-content-between align-items-start gap-3">
                        <div>
                          <div className="fw-semibold">{porcion.nombre}</div>
                          <div className="texto-ayuda">{porcion.nombre_categoria}</div>
                        </div>
                        <div className="text-end flex-shrink-0">
                          <div className="fw-semibold">{porcion.gramos} g</div>
                          {porcion.cantidad_en_medida_casera && (
                            <div className="texto-ayuda">
                              {porcion.cantidad_en_medida_casera}
                            </div>
                          )}
                        </div>
                      </div>

                      {porcion.sustituto && (
                        <div className="mt-2">
                          <button
                            type="button"
                            className="btn btn-sm btn-link p-0 texto-ayuda"
                            onClick={() => alternar(clave)}
                            aria-expanded={Boolean(visible)}
                          >
                            {visible ? 'Ocultar alternativa' : '¿No consiguió este alimento?'}
                          </button>
                          {visible && (
                            <div className="alert alert-light border mt-2 mb-0 py-2">
                              Puede cambiarlo por{' '}
                              <span className="fw-semibold">{porcion.sustituto.nombre}</span>,{' '}
                              {porcion.sustituto.gramos} g
                              {porcion.sustituto.medida_casera
                                ? ` (${porcion.sustituto.medida_casera})`
                                : ''}
                              . Aporta prácticamente lo mismo.
                            </div>
                          )}
                        </div>
                      )}
                    </li>
                  )
                })}
              </ul>
            </div>
          </div>
        </div>
      ))}

      <div className="col-12">
        <div className="alert alert-secondary mb-0" role="note">
          <strong>Importante.</strong> Este menú es una propuesta, no una obligación.
          Puede intercambiar alimentos de una misma categoría respetando las cantidades.
          Ante cualquier condición de salud, consulte a un profesional.
        </div>
      </div>
    </div>
  )
}
