/**
 * Administración de los catálogos maestros (historia HU-11).
 *
 * Reservada al administrador. Permite dar de alta, modificar y dar de baja
 * alimentos y ejercicios. La baja es lógica: el elemento se marca como no
 * disponible y deja de proponerse en los planes nuevos, pero los planes ya
 * generados conservan su referencia.
 *
 * El formulario dejaba fija una columna entera de la pantalla, estuviera o no
 * en uso, y la tabla se quedaba con el resto. Ahora «Agregar» y «Editar» abren
 * un panel lateral que desaparece al cerrarlo, de modo que la tabla —que es a
 * lo que se viene— ocupa el ancho completo.
 *
 * Se añaden dos cosas que la lista larga pedía: un buscador por nombre y unos
 * chips para filtrar por categoría o ver solo lo dado de baja. Con ciento
 * cuarenta alimentos, recorrer la tabla con la vista no es una opción.
 */

import { useCallback, useEffect, useMemo, useState } from 'react'

import ArmazonAdmin from '../componentes/ArmazonAdmin.jsx'
import AvisoDeError from '../componentes/AvisoDeError.jsx'
import Icono from '../componentes/Icono.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioCatalogos } from '../servicios/api.js'
import { quetzales } from '../utilidades/formatos.js'

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

const COLUMNAS_ALIMENTOS = '2.4fr 1.2fr .8fr .8fr .8fr 1fr 1.1fr'
const COLUMNAS_EJERCICIOS = '2.4fr 1fr 1fr 1.2fr 1fr 1.1fr'

function etiquetaDeLista(opciones, valor) {
  return opciones.find((opcion) => opcion.valor === valor)?.etiqueta ?? valor
}

/** Compara sin acentos ni mayúsculas: se busca «guisquil» y aparece «güisquil». */
function normalizar(texto) {
  return (texto ?? '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

export default function AdministracionCatalogos() {
  const { token } = useSesion()

  const [pestana, setPestana] = useState('alimentos')
  const [alimentos, setAlimentos] = useState([])
  const [ejercicios, setEjercicios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [aviso, setAviso] = useState(null)
  const [busqueda, setBusqueda] = useState('')
  const [filtro, setFiltro] = useState('todos')

  const [formularioAlimento, setFormularioAlimento] = useState(ALIMENTO_VACIO)
  const [formularioEjercicio, setFormularioEjercicio] = useState(EJERCICIO_VACIO)
  const [editandoAlimento, setEditandoAlimento] = useState(null)
  const [editandoEjercicio, setEditandoEjercicio] = useState(null)
  const [panelAbierto, setPanelAbierto] = useState(false)
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

  // Al cambiar de pestaña, el filtro de la anterior no tiene sentido en la nueva.
  const cambiarPestana = (siguiente) => {
    setPestana(siguiente)
    setFiltro('todos')
    setBusqueda('')
    setPanelAbierto(false)
  }

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

  const cerrarPanel = () => {
    setPanelAbierto(false)
    setFormularioAlimento(ALIMENTO_VACIO)
    setFormularioEjercicio(EJERCICIO_VACIO)
    setEditandoAlimento(null)
    setEditandoEjercicio(null)
  }

  const abrirParaAgregar = () => {
    setFormularioAlimento(ALIMENTO_VACIO)
    setFormularioEjercicio(EJERCICIO_VACIO)
    setEditandoAlimento(null)
    setEditandoEjercicio(null)
    setPanelAbierto(true)
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
      cerrarPanel()
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
      cerrarPanel()
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
    setPanelAbierto(true)
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
    setPanelAbierto(true)
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

  const esAlimentos = pestana === 'alimentos'
  const elementos = esAlimentos ? alimentos : ejercicios
  const opcionesDeFiltro = esAlimentos ? CATEGORIAS : GRUPOS
  const campoDeFiltro = esAlimentos ? 'categoria' : 'grupo_muscular'

  const deBaja = elementos.filter((elemento) => !elemento.disponible_localmente).length

  const visibles = useMemo(() => {
    const texto = normalizar(busqueda)
    return elementos.filter((elemento) => {
      if (texto && !normalizar(elemento.nombre).includes(texto)) return false
      if (filtro === 'todos') return true
      if (filtro === 'de_baja') return !elemento.disponible_localmente
      return elemento[campoDeFiltro] === filtro
    })
  }, [elementos, busqueda, filtro, campoDeFiltro])

  return (
    <ArmazonAdmin
      titulo="Catálogos"
      explicacion="Los alimentos y los ejercicios que el sistema propone en los planes. Dar de baja un elemento no lo borra: deja de proponerse, pero los planes ya generados lo conservan."
      accion={
        <button
          type="button"
          className="boton boton--principal boton--compacto"
          onClick={abrirParaAgregar}
        >
          {esAlimentos ? 'Agregar alimento' : 'Agregar ejercicio'}
        </button>
      }
      subbarra={
        <>
          <button
            type="button"
            className={`admin__pestana${esAlimentos ? ' admin__pestana--activa' : ''}`}
            onClick={() => cambiarPestana('alimentos')}
            aria-pressed={esAlimentos}
          >
            Alimentos · {alimentos.length}
          </button>
          <button
            type="button"
            className={`admin__pestana${!esAlimentos ? ' admin__pestana--activa' : ''}`}
            onClick={() => cambiarPestana('ejercicios')}
            aria-pressed={!esAlimentos}
          >
            Ejercicios · {ejercicios.length}
          </button>
        </>
      }
    >
      {error && <AvisoDeError mensaje={error} alReintentar={cargar} />}
      {aviso && (
        <p className="aviso aviso--ok" role="status">
          {aviso}
        </p>
      )}

      <div className="buscador">
        <Icono nombre="search-01" tamano={15} className="tinta-4" />
        <input
          type="search"
          className="buscador__campo"
          placeholder={esAlimentos ? 'Buscar un alimento' : 'Buscar un ejercicio'}
          value={busqueda}
          onChange={(evento) => setBusqueda(evento.target.value)}
          aria-label="Buscar en el catálogo"
        />
      </div>

      <div className="pildoras">
        <button
          type="button"
          className={`chip${filtro === 'todos' ? ' chip--activo' : ''}`}
          onClick={() => setFiltro('todos')}
        >
          Todos
        </button>
        {opcionesDeFiltro.map((opcion) => (
          <button
            key={opcion.valor}
            type="button"
            className={`chip${filtro === opcion.valor ? ' chip--activo' : ''}`}
            onClick={() => setFiltro(opcion.valor)}
          >
            {opcion.etiqueta}
          </button>
        ))}
        {deBaja > 0 && (
          <button
            type="button"
            className={`chip${filtro === 'de_baja' ? ' chip--activo' : ''}`}
            onClick={() => setFiltro('de_baja')}
          >
            De baja · {deBaja}
          </button>
        )}
      </div>

      {cargando ? (
        <div className="pila-3" aria-busy="true">
          <div className="esqueleto esqueleto--fila" />
          <div className="esqueleto esqueleto--fila" />
          <div className="esqueleto esqueleto--fila" />
          <span className="solo-lectores">Cargando los catálogos…</span>
        </div>
      ) : visibles.length === 0 ? (
        <div className="vacio">
          <h2 className="vacio__titulo">No hay nada que coincida</h2>
          <p className="cuerpo">Pruebe con otro nombre o quite el filtro de categoría.</p>
        </div>
      ) : (
        <div className="tabla">
          <div className="tabla__desplazamiento">
            {esAlimentos ? (
              <TablaAlimentos
                alimentos={visibles}
                alEditar={editarAlimento}
                alCambiarDisponibilidad={(alimento) => cambiarDisponibilidad('alimento', alimento)}
              />
            ) : (
              <TablaEjercicios
                ejercicios={visibles}
                alEditar={editarEjercicio}
                alCambiarDisponibilidad={(ejercicio) =>
                  cambiarDisponibilidad('ejercicio', ejercicio)
                }
              />
            )}
          </div>
        </div>
      )}

      {panelAbierto && (
        <>
          <div className="velo no-imprimir" onClick={cerrarPanel} aria-hidden="true" />
          <div
            className="panel-lateral no-imprimir"
            role="dialog"
            aria-modal="true"
            aria-label={esAlimentos ? 'Alimento del catálogo' : 'Ejercicio del catálogo'}
          >
            <div className="hoja-inferior__cabecera">
              <h2 className="titulo-tarjeta">
                {esAlimentos
                  ? editandoAlimento
                    ? 'Modificar alimento'
                    : 'Agregar alimento'
                  : editandoEjercicio
                    ? 'Modificar ejercicio'
                    : 'Agregar ejercicio'}
              </h2>
              <button
                type="button"
                className="boton boton--circular"
                onClick={cerrarPanel}
                aria-label="Cerrar"
              >
                <Icono nombre="cancel-01" tamano={18} />
              </button>
            </div>

            {esAlimentos ? (
              <FormularioAlimento
                formulario={formularioAlimento}
                alCambiar={actualizarAlimento}
                alEnviar={guardarAlimento}
                guardando={guardando}
                editando={Boolean(editandoAlimento)}
                alCancelar={cerrarPanel}
              />
            ) : (
              <FormularioEjercicio
                formulario={formularioEjercicio}
                alCambiar={actualizarEjercicio}
                alEnviar={guardarEjercicio}
                guardando={guardando}
                editando={Boolean(editandoEjercicio)}
                alCancelar={cerrarPanel}
              />
            )}
          </div>
        </>
      )}
    </ArmazonAdmin>
  )
}

function TablaAlimentos({ alimentos, alEditar, alCambiarDisponibilidad }) {
  const columnas = { gridTemplateColumns: COLUMNAS_ALIMENTOS }

  return (
    <>
      <div className="tabla__cabecera" style={columnas}>
        <span>Alimento</span>
        <span>Categoría</span>
        <span className="tabla__numero">kcal</span>
        <span className="tabla__numero">Prot.</span>
        <span className="tabla__numero">Costo</span>
        <span>Estado</span>
        <span className="tabla__numero">Acciones</span>
      </div>
      {alimentos.map((alimento) => (
        <div
          key={alimento.id}
          className={`tabla__fila${alimento.disponible_localmente ? '' : ' tabla__fila--baja'}`}
          style={columnas}
        >
          <span className="tabla__nombre">
            <span>{alimento.nombre}</span>
            {alimento.medida_casera && (
              <span className="tabla__detalle">{alimento.medida_casera}</span>
            )}
          </span>
          <span className="tinta-2">{etiquetaDeLista(CATEGORIAS, alimento.categoria)}</span>
          <span className="tabla__numero">{alimento.energia_kcal_100g}</span>
          <span className="tabla__numero">{alimento.proteina_g_100g} g</span>
          <span className="tabla__numero">
            {alimento.costo_aproximado_quetzales === null
              ? '—'
              : quetzales(alimento.costo_aproximado_quetzales)}
          </span>
          <span>
            <span className={`chip ${alimento.disponible_localmente ? 'chip--ok' : 'chip--neutro'}`}>
              {alimento.disponible_localmente ? 'Disponible' : 'De baja'}
            </span>
          </span>
          <span className="tabla__acciones">
            <button type="button" className="boton-texto" onClick={() => alEditar(alimento)}>
              Editar
            </button>
            <button
              type="button"
              className="boton-texto boton-texto--tenue"
              onClick={() => alCambiarDisponibilidad(alimento)}
            >
              {alimento.disponible_localmente ? 'Dar de baja' : 'Habilitar'}
            </button>
          </span>
        </div>
      ))}
    </>
  )
}

function TablaEjercicios({ ejercicios, alEditar, alCambiarDisponibilidad }) {
  const columnas = { gridTemplateColumns: COLUMNAS_EJERCICIOS }

  return (
    <>
      <div className="tabla__cabecera" style={columnas}>
        <span>Ejercicio</span>
        <span>Grupo</span>
        <span>Nivel</span>
        <span>Equipamiento</span>
        <span>Estado</span>
        <span className="tabla__numero">Acciones</span>
      </div>
      {ejercicios.map((ejercicio) => (
        <div
          key={ejercicio.id}
          className={`tabla__fila${ejercicio.disponible_localmente ? '' : ' tabla__fila--baja'}`}
          style={columnas}
        >
          <span className="tabla__nombre">
            <span>{ejercicio.nombre}</span>
            {ejercicio.es_compuesto && <span className="tabla__detalle">Compuesto</span>}
          </span>
          <span className="tinta-2">{etiquetaDeLista(GRUPOS, ejercicio.grupo_muscular)}</span>
          <span className="tinta-2">{etiquetaDeLista(NIVELES, ejercicio.nivel_minimo)}</span>
          <span className="tinta-2">{ejercicio.equipamiento}</span>
          <span>
            <span
              className={`chip ${ejercicio.disponible_localmente ? 'chip--ok' : 'chip--neutro'}`}
            >
              {ejercicio.disponible_localmente ? 'Disponible' : 'De baja'}
            </span>
          </span>
          <span className="tabla__acciones">
            <button type="button" className="boton-texto" onClick={() => alEditar(ejercicio)}>
              Editar
            </button>
            <button
              type="button"
              className="boton-texto boton-texto--tenue"
              onClick={() => alCambiarDisponibilidad(ejercicio)}
            >
              {ejercicio.disponible_localmente ? 'Dar de baja' : 'Habilitar'}
            </button>
          </span>
        </div>
      ))}
    </>
  )
}

const APORTES = [
  ['energia_kcal_100g', 'Energía (kcal)'],
  ['proteina_g_100g', 'Proteína (g)'],
  ['carbohidrato_g_100g', 'Carbohidrato (g)'],
  ['grasa_g_100g', 'Grasa (g)'],
]

function FormularioAlimento({ formulario, alCambiar, alEnviar, guardando, editando, alCancelar }) {
  return (
    <form onSubmit={alEnviar} noValidate className="pila-4">
      <label className="campo">
        <span className="campo__etiqueta">Nombre</span>
        <input
          name="nombre"
          type="text"
          className="campo__control"
          value={formulario.nombre}
          onChange={alCambiar}
          required
        />
      </label>

      <label className="campo">
        <span className="campo__etiqueta">Categoría</span>
        <select
          name="categoria"
          className="campo__control"
          value={formulario.categoria}
          onChange={alCambiar}
        >
          {CATEGORIAS.map((opcion) => (
            <option key={opcion.valor} value={opcion.valor}>
              {opcion.etiqueta}
            </option>
          ))}
        </select>
      </label>

      <div className="pila-3">
        <span className="rotulo">Aporte por cada 100 gramos</span>
        <div className="campos-par">
          {APORTES.map(([campo, etiqueta]) => (
            <label className="campo" key={campo}>
              <span className="campo__etiqueta">{etiqueta}</span>
              <input
                name={campo}
                type="number"
                step="0.1"
                min="0"
                className="campo__control campo__control--numero"
                value={formulario[campo]}
                onChange={alCambiar}
                required
              />
            </label>
          ))}
        </div>
      </div>

      <label className="campo">
        <span className="campo__etiqueta">Medida casera</span>
        <input
          name="medida_casera"
          type="text"
          className="campo__control"
          value={formulario.medida_casera}
          onChange={alCambiar}
        />
      </label>

      <label className="campo">
        <span className="campo__etiqueta">Costo aproximado (Q)</span>
        <input
          name="costo_aproximado_quetzales"
          type="number"
          step="0.5"
          min="0"
          className="campo__control campo__control--numero"
          value={formulario.costo_aproximado_quetzales}
          onChange={alCambiar}
        />
      </label>

      <div className="lista">
        <label className="lista__fila">
          <input
            type="checkbox"
            name="disponible_localmente"
            checked={formulario.disponible_localmente}
            onChange={alCambiar}
          />
          <span className="lista__etiqueta crece">Se consigue en el municipio</span>
        </label>
      </div>

      <button type="submit" className="boton boton--principal" disabled={guardando}>
        {guardando ? 'Guardando…' : editando ? 'Guardar cambios' : 'Agregar'}
      </button>
      <button type="button" className="boton boton--secundario" onClick={alCancelar}>
        Cancelar
      </button>
    </form>
  )
}

function FormularioEjercicio({ formulario, alCambiar, alEnviar, guardando, editando, alCancelar }) {
  return (
    <form onSubmit={alEnviar} noValidate className="pila-4">
      <label className="campo">
        <span className="campo__etiqueta">Nombre</span>
        <input
          name="nombre"
          type="text"
          className="campo__control"
          value={formulario.nombre}
          onChange={alCambiar}
          required
        />
      </label>

      <div className="campos-par">
        <label className="campo">
          <span className="campo__etiqueta">Grupo muscular</span>
          <select
            name="grupo_muscular"
            className="campo__control"
            value={formulario.grupo_muscular}
            onChange={alCambiar}
          >
            {GRUPOS.map((opcion) => (
              <option key={opcion.valor} value={opcion.valor}>
                {opcion.etiqueta}
              </option>
            ))}
          </select>
        </label>

        <label className="campo">
          <span className="campo__etiqueta">Nivel mínimo</span>
          <select
            name="nivel_minimo"
            className="campo__control"
            value={formulario.nivel_minimo}
            onChange={alCambiar}
          >
            {NIVELES.map((opcion) => (
              <option key={opcion.valor} value={opcion.valor}>
                {opcion.etiqueta}
              </option>
            ))}
          </select>
        </label>
      </div>

      <label className="campo">
        <span className="campo__etiqueta">Equipamiento</span>
        <input
          name="equipamiento"
          type="text"
          className="campo__control"
          value={formulario.equipamiento}
          onChange={alCambiar}
          required
        />
      </label>

      <label className="campo">
        <span className="campo__etiqueta">Descripción</span>
        <textarea
          name="descripcion"
          rows="3"
          className="campo__control"
          value={formulario.descripcion}
          onChange={alCambiar}
        />
      </label>

      <div className="lista">
        <label className="lista__fila">
          <input
            type="checkbox"
            name="es_compuesto"
            checked={formulario.es_compuesto}
            onChange={alCambiar}
          />
          <span className="pila-2 crece">
            <span className="lista__etiqueta">Es un ejercicio compuesto</span>
            <span className="lista__detalle">
              Involucra varias articulaciones; se prescribe al inicio de la sesión.
            </span>
          </span>
        </label>
        <label className="lista__fila">
          <input
            type="checkbox"
            name="disponible_localmente"
            checked={formulario.disponible_localmente}
            onChange={alCambiar}
          />
          <span className="lista__etiqueta crece">El gimnasio tiene el equipo</span>
        </label>
      </div>

      <button type="submit" className="boton boton--principal" disabled={guardando}>
        {guardando ? 'Guardando…' : editando ? 'Guardar cambios' : 'Agregar'}
      </button>
      <button type="button" className="boton boton--secundario" onClick={alCancelar}>
        Cancelar
      </button>
    </form>
  )
}
