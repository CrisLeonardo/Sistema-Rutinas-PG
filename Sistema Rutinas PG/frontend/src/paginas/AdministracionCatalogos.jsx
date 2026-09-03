/**
 * Pantalla de administración de los catálogos maestros (historia HU-11).
 *
 * Reservada al administrador. Permite dar de alta, modificar y dar de baja
 * alimentos y ejercicios. La baja es lógica: el elemento se marca como no
 * disponible y deja de proponerse en los planes nuevos, pero los planes ya
 * generados conservan su referencia.
 */

import { useCallback, useEffect, useState } from 'react'

import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioCatalogos } from '../servicios/api.js'

const CATEGORIAS = [
  { valor: 'cereal', etiqueta: 'Cereal' },
  { valor: 'proteina_animal', etiqueta: 'Proteína animal' },
  { valor: 'leguminosa', etiqueta: 'Leguminosa' },
  { valor: 'lacteo', etiqueta: 'Lácteo' },
  { valor: 'fruta', etiqueta: 'Fruta' },
  { valor: 'verdura', etiqueta: 'Verdura' },
  { valor: 'grasa', etiqueta: 'Grasa' },
  { valor: 'tuberculo', etiqueta: 'Tubérculo' },
]

const GRUPOS = [
  { valor: 'pecho', etiqueta: 'Pecho' },
  { valor: 'espalda', etiqueta: 'Espalda' },
  { valor: 'pierna', etiqueta: 'Pierna' },
  { valor: 'hombro', etiqueta: 'Hombro' },
  { valor: 'brazo', etiqueta: 'Brazo' },
  { valor: 'abdomen', etiqueta: 'Abdomen' },
]

const NIVELES = [
  { valor: 'principiante', etiqueta: 'Principiante' },
  { valor: 'intermedio', etiqueta: 'Intermedio' },
  { valor: 'avanzado', etiqueta: 'Avanzado' },
]

const ALIMENTO_VACIO = {
  nombre: '',
  categoria: 'cereal',
  energia_kcal_100g: '',
  proteina_g_100g: '',
  carbohidrato_g_100g: '',
  grasa_g_100g: '',
  costo_aproximado_quetzales: '',
  medida_casera: '',
  disponible_localmente: true,
}

const EJERCICIO_VACIO = {
  nombre: '',
  grupo_muscular: 'pecho',
  nivel_minimo: 'principiante',
  equipamiento: '',
  descripcion: '',
  es_compuesto: false,
  disponible_localmente: true,
}

export default function AdministracionCatalogos() {
  const { token } = useSesion()

  const [pestana, setPestana] = useState('alimentos')
  const [alimentos, setAlimentos] = useState([])
  const [ejercicios, setEjercicios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [aviso, setAviso] = useState(null)

  const [formularioAlimento, setFormularioAlimento] = useState(ALIMENTO_VACIO)
  const [formularioEjercicio, setFormularioEjercicio] = useState(EJERCICIO_VACIO)
  const [editandoAlimento, setEditandoAlimento] = useState(null)
  const [editandoEjercicio, setEditandoEjercicio] = useState(null)
  const [guardando, setGuardando] = useState(false)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      const [listaAlimentos, listaEjercicios] = await Promise.all([
        servicioCatalogos.listarAlimentos(token),
        servicioCatalogos.listarEjercicios(token),
      ])
      setAlimentos(listaAlimentos)
      setEjercicios(listaEjercicios)
      setError(null)
    } catch (fallo) {
      setError(fallo.message)
    } finally {
      setCargando(false)
    }
  }, [token])

  useEffect(() => {
    cargar()
  }, [cargar])

  const actualizarAlimento = (evento) => {
    const { name, value, type, checked } = evento.target
    setFormularioAlimento((anterior) => ({
      ...anterior,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const actualizarEjercicio = (evento) => {
    const { name, value, type, checked } = evento.target
    setFormularioEjercicio((anterior) => ({
      ...anterior,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const limpiarAlimento = () => {
    setFormularioAlimento(ALIMENTO_VACIO)
    setEditandoAlimento(null)
  }

  const limpiarEjercicio = () => {
    setFormularioEjercicio(EJERCICIO_VACIO)
    setEditandoEjercicio(null)
  }

  const guardarAlimento = async (evento) => {
    evento.preventDefault()
    setGuardando(true)
    setError(null)
    setAviso(null)
    const datos = {
      nombre: formularioAlimento.nombre.trim(),
      categoria: formularioAlimento.categoria,
      energia_kcal_100g: Number(formularioAlimento.energia_kcal_100g),
      proteina_g_100g: Number(formularioAlimento.proteina_g_100g),
      carbohidrato_g_100g: Number(formularioAlimento.carbohidrato_g_100g),
      grasa_g_100g: Number(formularioAlimento.grasa_g_100g),
      costo_aproximado_quetzales: formularioAlimento.costo_aproximado_quetzales
        ? Number(formularioAlimento.costo_aproximado_quetzales)
        : null,
      medida_casera: formularioAlimento.medida_casera.trim() || null,
      disponible_localmente: formularioAlimento.disponible_localmente,
    }
    try {
      if (editandoAlimento) {
        await servicioCatalogos.modificarAlimento(editandoAlimento, datos, token)
        setAviso(`Se actualizó «${datos.nombre}».`)
      } else {
        await servicioCatalogos.crearAlimento(datos, token)
        setAviso(`Se agregó «${datos.nombre}» al catálogo.`)
      }
      limpiarAlimento()
      await cargar()
    } catch (fallo) {
      setError(fallo.message)
    } finally {
      setGuardando(false)
    }
  }

  const guardarEjercicio = async (evento) => {
    evento.preventDefault()
    setGuardando(true)
    setError(null)
    setAviso(null)
    const datos = {
      nombre: formularioEjercicio.nombre.trim(),
      grupo_muscular: formularioEjercicio.grupo_muscular,
      nivel_minimo: formularioEjercicio.nivel_minimo,
      equipamiento: formularioEjercicio.equipamiento.trim(),
      descripcion: formularioEjercicio.descripcion.trim() || null,
      es_compuesto: formularioEjercicio.es_compuesto,
      disponible_localmente: formularioEjercicio.disponible_localmente,
    }
    try {
      if (editandoEjercicio) {
        await servicioCatalogos.modificarEjercicio(editandoEjercicio, datos, token)
        setAviso(`Se actualizó «${datos.nombre}».`)
      } else {
        await servicioCatalogos.crearEjercicio(datos, token)
        setAviso(`Se agregó «${datos.nombre}» al catálogo.`)
      }
      limpiarEjercicio()
      await cargar()
    } catch (fallo) {
      setError(fallo.message)
    } finally {
      setGuardando(false)
    }
  }

  const editarAlimento = (alimento) => {
    setEditandoAlimento(alimento.id)
    setFormularioAlimento({
      nombre: alimento.nombre,
      categoria: alimento.categoria,
      energia_kcal_100g: String(alimento.energia_kcal_100g),
      proteina_g_100g: String(alimento.proteina_g_100g),
      carbohidrato_g_100g: String(alimento.carbohidrato_g_100g),
      grasa_g_100g: String(alimento.grasa_g_100g),
      costo_aproximado_quetzales:
        alimento.costo_aproximado_quetzales === null
          ? ''
          : String(alimento.costo_aproximado_quetzales),
      medida_casera: alimento.medida_casera ?? '',
      disponible_localmente: alimento.disponible_localmente,
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const editarEjercicio = (ejercicio) => {
    setEditandoEjercicio(ejercicio.id)
    setFormularioEjercicio({
      nombre: ejercicio.nombre,
      grupo_muscular: ejercicio.grupo_muscular,
      nivel_minimo: ejercicio.nivel_minimo,
      equipamiento: ejercicio.equipamiento,
      descripcion: ejercicio.descripcion ?? '',
      es_compuesto: ejercicio.es_compuesto,
      disponible_localmente: ejercicio.disponible_localmente,
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const cambiarDisponibilidad = async (tipo, elemento) => {
    setError(null)
    setAviso(null)
    try {
      if (tipo === 'alimento') {
        await servicioCatalogos.cambiarDisponibilidadAlimento(
          elemento.id,
          !elemento.disponible_localmente,
          token,
        )
      } else {
        await servicioCatalogos.cambiarDisponibilidadEjercicio(
          elemento.id,
          !elemento.disponible_localmente,
          token,
        )
      }
      setAviso(
        elemento.disponible_localmente
          ? `«${elemento.nombre}» dejará de proponerse en los planes nuevos.`
          : `«${elemento.nombre}» vuelve a estar disponible.`,
      )
      await cargar()
    } catch (fallo) {
      setError(fallo.message)
    }
  }

  return (
    <div className="row g-4">
      <div className="col-12">
        <h1 className="h3 mb-1">Catálogos del sistema</h1>
        <p className="texto-ayuda mb-0">
          Los alimentos y los ejercicios que el sistema propone en los planes. Dar de
          baja un elemento no lo borra: deja de proponerse, pero los planes ya generados
          lo conservan.
        </p>
      </div>

      {error && (
        <div className="col-12">
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        </div>
      )}

      {aviso && (
        <div className="col-12">
          <div className="alert alert-success" role="status">
            {aviso}
          </div>
        </div>
      )}

      <div className="col-12">
        <ul className="nav nav-tabs">
          <li className="nav-item">
            <button
              type="button"
              className={`nav-link control-tactil ${pestana === 'alimentos' ? 'active' : ''}`}
              onClick={() => setPestana('alimentos')}
            >
              Alimentos ({alimentos.length})
            </button>
          </li>
          <li className="nav-item">
            <button
              type="button"
              className={`nav-link control-tactil ${pestana === 'ejercicios' ? 'active' : ''}`}
              onClick={() => setPestana('ejercicios')}
            >
              Ejercicios ({ejercicios.length})
            </button>
          </li>
        </ul>
      </div>

      {cargando && (
        <div className="col-12">
          <p className="texto-ayuda">Cargando los catálogos…</p>
        </div>
      )}

      {!cargando && pestana === 'alimentos' && (
        <>
          <div className="col-12 col-xl-4">
            <div className="card shadow-sm">
              <div className="card-body">
                <h2 className="h5 card-title">
                  {editandoAlimento ? 'Modificar alimento' : 'Agregar alimento'}
                </h2>
                <form onSubmit={guardarAlimento} noValidate>
                  <div className="mb-3">
                    <label className="form-label" htmlFor="nombre-alimento">
                      Nombre
                    </label>
                    <input
                      id="nombre-alimento"
                      name="nombre"
                      className="form-control control-tactil"
                      value={formularioAlimento.nombre}
                      onChange={actualizarAlimento}
                      required
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label" htmlFor="categoria-alimento">
                      Categoría
                    </label>
                    <select
                      id="categoria-alimento"
                      name="categoria"
                      className="form-select control-tactil"
                      value={formularioAlimento.categoria}
                      onChange={actualizarAlimento}
                    >
                      {CATEGORIAS.map((opcion) => (
                        <option key={opcion.valor} value={opcion.valor}>
                          {opcion.etiqueta}
                        </option>
                      ))}
                    </select>
                  </div>

                  <p className="texto-ayuda mb-2">Aporte por cada 100 gramos</p>
                  <div className="row g-2 mb-3">
                    {[
                      ['energia_kcal_100g', 'Energía (kcal)'],
                      ['proteina_g_100g', 'Proteína (g)'],
                      ['carbohidrato_g_100g', 'Carbohidrato (g)'],
                      ['grasa_g_100g', 'Grasa (g)'],
                    ].map(([campo, etiqueta]) => (
                      <div className="col-6" key={campo}>
                        <label className="form-label texto-ayuda" htmlFor={campo}>
                          {etiqueta}
                        </label>
                        <input
                          id={campo}
                          name={campo}
                          type="number"
                          step="0.1"
                          min="0"
                          className="form-control control-tactil"
                          value={formularioAlimento[campo]}
                          onChange={actualizarAlimento}
                          required
                        />
                      </div>
                    ))}
                  </div>

                  <div className="mb-3">
                    <label className="form-label" htmlFor="medida_casera">
                      Medida casera
                    </label>
                    <input
                      id="medida_casera"
                      name="medida_casera"
                      className="form-control control-tactil"
                      placeholder="1 taza ≈ 160 g"
                      value={formularioAlimento.medida_casera}
                      onChange={actualizarAlimento}
                    />
                    <div className="form-text">
                      Escríbala como «1 taza ≈ 160 g» para que el sistema calcule las
                      porciones.
                    </div>
                  </div>

                  <div className="mb-3">
                    <label className="form-label" htmlFor="costo_aproximado_quetzales">
                      Costo aproximado (quetzales)
                    </label>
                    <input
                      id="costo_aproximado_quetzales"
                      name="costo_aproximado_quetzales"
                      type="number"
                      step="0.5"
                      min="0"
                      className="form-control control-tactil"
                      value={formularioAlimento.costo_aproximado_quetzales}
                      onChange={actualizarAlimento}
                    />
                  </div>

                  <div className="form-check opcion-tactil mb-3">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      id="disponible-alimento"
                      name="disponible_localmente"
                      checked={formularioAlimento.disponible_localmente}
                      onChange={actualizarAlimento}
                    />
                    <label className="form-check-label" htmlFor="disponible-alimento">
                      Se consigue en el municipio
                    </label>
                  </div>

                  <div className="d-grid gap-2">
                    <button
                      type="submit"
                      className="btn btn-principal control-tactil"
                      disabled={guardando}
                    >
                      {guardando ? 'Guardando…' : editandoAlimento ? 'Guardar cambios' : 'Agregar'}
                    </button>
                    {editandoAlimento && (
                      <button
                        type="button"
                        className="btn btn-outline-secondary control-tactil"
                        onClick={limpiarAlimento}
                      >
                        Cancelar
                      </button>
                    )}
                  </div>
                </form>
              </div>
            </div>
          </div>

          <div className="col-12 col-xl-8">
            <div className="card shadow-sm">
              <div className="card-body">
                <h2 className="h5 card-title">Alimentos registrados</h2>
                <div className="contenedor-tabla">
                  <table className="table table-sm align-middle tabla-cuentas mb-0">
                    <thead>
                      <tr>
                        <th scope="col">Alimento</th>
                        <th scope="col">Categoría</th>
                        <th scope="col" className="text-end">
                          kcal/100 g
                        </th>
                        <th scope="col">Estado</th>
                        <th scope="col">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {alimentos.map((alimento) => (
                        <tr key={alimento.id}>
                          <td>
                            {alimento.nombre}
                            {alimento.medida_casera && (
                              <span className="d-block texto-ayuda">
                                {alimento.medida_casera}
                              </span>
                            )}
                          </td>
                          <td>{alimento.nombre_categoria}</td>
                          <td className="text-end">{alimento.energia_kcal_100g}</td>
                          <td>
                            <span
                              className={`badge ${
                                alimento.disponible_localmente ? 'bg-success' : 'bg-secondary'
                              }`}
                            >
                              {alimento.disponible_localmente ? 'Disponible' : 'De baja'}
                            </span>
                          </td>
                          <td>
                            <div className="d-flex gap-2">
                              <button
                                type="button"
                                className="btn btn-sm btn-outline-secondary control-tactil"
                                onClick={() => editarAlimento(alimento)}
                              >
                                Editar
                              </button>
                              <button
                                type="button"
                                className="btn btn-sm btn-outline-secondary control-tactil"
                                onClick={() => cambiarDisponibilidad('alimento', alimento)}
                              >
                                {alimento.disponible_localmente ? 'Dar de baja' : 'Habilitar'}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {!cargando && pestana === 'ejercicios' && (
        <>
          <div className="col-12 col-xl-4">
            <div className="card shadow-sm">
              <div className="card-body">
                <h2 className="h5 card-title">
                  {editandoEjercicio ? 'Modificar ejercicio' : 'Agregar ejercicio'}
                </h2>
                <form onSubmit={guardarEjercicio} noValidate>
                  <div className="mb-3">
                    <label className="form-label" htmlFor="nombre-ejercicio">
                      Nombre
                    </label>
                    <input
                      id="nombre-ejercicio"
                      name="nombre"
                      className="form-control control-tactil"
                      value={formularioEjercicio.nombre}
                      onChange={actualizarEjercicio}
                      required
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label" htmlFor="grupo_muscular">
                      Grupo muscular
                    </label>
                    <select
                      id="grupo_muscular"
                      name="grupo_muscular"
                      className="form-select control-tactil"
                      value={formularioEjercicio.grupo_muscular}
                      onChange={actualizarEjercicio}
                    >
                      {GRUPOS.map((opcion) => (
                        <option key={opcion.valor} value={opcion.valor}>
                          {opcion.etiqueta}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="mb-3">
                    <label className="form-label" htmlFor="nivel_minimo">
                      Nivel mínimo
                    </label>
                    <select
                      id="nivel_minimo"
                      name="nivel_minimo"
                      className="form-select control-tactil"
                      value={formularioEjercicio.nivel_minimo}
                      onChange={actualizarEjercicio}
                    >
                      {NIVELES.map((opcion) => (
                        <option key={opcion.valor} value={opcion.valor}>
                          {opcion.etiqueta}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="mb-3">
                    <label className="form-label" htmlFor="equipamiento">
                      Equipamiento
                    </label>
                    <input
                      id="equipamiento"
                      name="equipamiento"
                      className="form-control control-tactil"
                      placeholder="Barra y discos"
                      value={formularioEjercicio.equipamiento}
                      onChange={actualizarEjercicio}
                      required
                    />
                  </div>

                  <div className="mb-3">
                    <label className="form-label" htmlFor="descripcion">
                      Cómo se hace
                    </label>
                    <textarea
                      id="descripcion"
                      name="descripcion"
                      rows="3"
                      className="form-control"
                      value={formularioEjercicio.descripcion}
                      onChange={actualizarEjercicio}
                    />
                  </div>

                  <div className="form-check opcion-tactil">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      id="es_compuesto"
                      name="es_compuesto"
                      checked={formularioEjercicio.es_compuesto}
                      onChange={actualizarEjercicio}
                    />
                    <label className="form-check-label" htmlFor="es_compuesto">
                      Es un ejercicio compuesto
                      <span className="d-block texto-ayuda">
                        Involucra varias articulaciones; se prescribe al inicio de la sesión.
                      </span>
                    </label>
                  </div>

                  <div className="form-check opcion-tactil mb-3">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      id="disponible-ejercicio"
                      name="disponible_localmente"
                      checked={formularioEjercicio.disponible_localmente}
                      onChange={actualizarEjercicio}
                    />
                    <label className="form-check-label" htmlFor="disponible-ejercicio">
                      El gimnasio tiene el equipo
                    </label>
                  </div>

                  <div className="d-grid gap-2">
                    <button
                      type="submit"
                      className="btn btn-principal control-tactil"
                      disabled={guardando}
                    >
                      {guardando
                        ? 'Guardando…'
                        : editandoEjercicio
                          ? 'Guardar cambios'
                          : 'Agregar'}
                    </button>
                    {editandoEjercicio && (
                      <button
                        type="button"
                        className="btn btn-outline-secondary control-tactil"
                        onClick={limpiarEjercicio}
                      >
                        Cancelar
                      </button>
                    )}
                  </div>
                </form>
              </div>
            </div>
          </div>

          <div className="col-12 col-xl-8">
            <div className="card shadow-sm">
              <div className="card-body">
                <h2 className="h5 card-title">Ejercicios registrados</h2>
                <div className="contenedor-tabla">
                  <table className="table table-sm align-middle tabla-cuentas mb-0">
                    <thead>
                      <tr>
                        <th scope="col">Ejercicio</th>
                        <th scope="col">Grupo</th>
                        <th scope="col">Equipamiento</th>
                        <th scope="col">Estado</th>
                        <th scope="col">Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ejercicios.map((ejercicio) => (
                        <tr key={ejercicio.id}>
                          <td>
                            {ejercicio.nombre}
                            {ejercicio.es_compuesto && (
                              <span className="badge bg-light text-dark ms-2">Compuesto</span>
                            )}
                          </td>
                          <td>{ejercicio.nombre_grupo}</td>
                          <td>{ejercicio.equipamiento}</td>
                          <td>
                            <span
                              className={`badge ${
                                ejercicio.disponible_localmente ? 'bg-success' : 'bg-secondary'
                              }`}
                            >
                              {ejercicio.disponible_localmente ? 'Disponible' : 'De baja'}
                            </span>
                          </td>
                          <td>
                            <div className="d-flex gap-2">
                              <button
                                type="button"
                                className="btn btn-sm btn-outline-secondary control-tactil"
                                onClick={() => editarEjercicio(ejercicio)}
                              >
                                Editar
                              </button>
                              <button
                                type="button"
                                className="btn btn-sm btn-outline-secondary control-tactil"
                                onClick={() => cambiarDisponibilidad('ejercicio', ejercicio)}
                              >
                                {ejercicio.disponible_localmente ? 'Dar de baja' : 'Habilitar'}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
