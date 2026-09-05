/**
 * «Hoy»: el destino central de la barra y la pantalla principal.
 *
 * Responde a la única pregunta con que alguien abre la aplicación: qué me toca
 * hoy. Antes esta pantalla listaba los módulos del sistema con el número de su
 * iteración y el código de sus historias de usuario —«Historias HU-09 y HU-10 ·
 * Iteración 5»—, que es información del proyecto y no del usuario: quien entrena
 * en el gimnasio no sabe qué es una historia de usuario ni tiene por qué saberlo.
 *
 * Ahora son dos tarjetas y una fila: comer, entrenar y anotar el peso. La
 * tarjeta «Su cuenta» desapareció de aquí: su contenido vive en «Más», que es
 * donde se busca. Y el resumen del avance también, porque tenía su propia
 * sección en la barra y repetirlo en el panel solo alargaba la pantalla.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import AvisoDeError from '../componentes/AvisoDeError.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import {
  ErrorApi,
  servicioEntrenamiento,
  servicioPerfil,
  servicioPlan,
  servicioProgreso,
  servicioRutina,
} from '../servicios/api.js'
import {
  diasDesde,
  entero,
  fechaConDia,
  iniciales,
  quetzales,
} from '../utilidades/formatos.js'

/** Día de la semana con lunes como 1, que es como el sistema numera las sesiones. */
function diaDeLaSemana() {
  const dia = new Date().getDay()
  return dia === 0 ? 7 : dia
}

function saludo() {
  const hora = new Date().getHours()
  if (hora < 12) return 'Buenos días'
  if (hora < 19) return 'Buenas tardes'
  return 'Buenas noches'
}

/** Recupera un recurso tratando el 404 como «todavía no existe», que no es un error. */
async function opcional(promesa) {
  try {
    return await promesa
  } catch (fallo) {
    if (fallo instanceof ErrorApi && (fallo.codigo === 404 || fallo.codigo === 409)) {
      return null
    }
    throw fallo
  }
}

export default function Panel() {
  const { usuario, token } = useSesion()

  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      // Las consultas salen a la vez: en serie, sobre una conexión móvil, el
      // panel tardaría seis veces más en dibujarse.
      const [plan, rutina, menu, reporte, entrenamiento, perfil] = await Promise.all([
        opcional(servicioPlan.consultarVigente(token)),
        opcional(servicioRutina.consultarVigente(token)),
        opcional(servicioPlan.consultarMenu(token)),
        opcional(servicioProgreso.consultarReporte(token)),
        opcional(servicioEntrenamiento.consultarResumen(token)),
        opcional(servicioPerfil.consultarVigente(token)),
      ])
      setDatos({ plan, rutina, menu, reporte, entrenamiento, perfil })
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

  if (cargando) return <PanelCargando />

  if (error) return <AvisoDeError mensaje={error} alReintentar={cargar} />

  const { plan, rutina, menu, reporte, entrenamiento, perfil } = datos
  const hoy = diaDeLaSemana()
  const sesionDeHoy = rutina?.sesiones?.find((sesion) => sesion.dia === hoy) ?? null
  const primerNombre = usuario?.nombre?.split(' ')[0] ?? ''

  if (!plan) return <PrimerDia tienePerfil={Boolean(perfil)} />

  return (
    <div className="pila">
      <div className="saludo">
        <div className="pila-2">
          <h1 className="titulo-pantalla">
            {saludo()}, {primerNombre}
          </h1>
          <p className="apoyo capitalizado">{fechaConDia()}</p>
        </div>
        <Link to="/mas" className="avatar" aria-label="Mi cuenta">
          {iniciales(usuario?.nombre)}
        </Link>
      </div>

      {plan.advertencias_de_salud?.length > 0 && (
        <div className="aviso aviso--aviso" role="alert">
          {plan.advertencias_de_salud.map((advertencia) => (
            <p key={advertencia} className="pila-2">
              {advertencia}
            </p>
          ))}
        </div>
      )}

      <div className="rejilla-doble">
        <TarjetaComer plan={plan} menu={menu} />
        <TarjetaEntrenar sesion={sesionDeHoy} rutina={rutina} entrenamiento={entrenamiento} />
      </div>

      <FilaDelPeso reporte={reporte} />
    </div>
  )
}

/** Esqueletos con la forma del contenido, no la palabra «Cargando» sola. */
function PanelCargando() {
  return (
    <div className="pila" aria-busy="true">
      <div className="esqueleto esqueleto--titulo" />
      <div className="esqueleto esqueleto--tarjeta" />
      <div className="esqueleto esqueleto--tarjeta" />
      <div className="esqueleto esqueleto--fila" />
      <span className="solo-lectores">Cargando su panel…</span>
    </div>
  )
}

/**
 * Primer día: sin plan no hay nada que mostrar, solo un camino que seguir.
 *
 * Cuando las medidas ya están registradas y lo que falta es el plan, el botón
 * cambia de destino en lugar de aparecer un segundo botón: la pantalla sigue
 * teniendo una sola acción.
 */
function PrimerDia({ tienePerfil }) {
  const pasos = [
    'Sus medidas y su objetivo',
    'Su plan de comidas y su rutina',
    'Entrenar y anotar su peso cada semana',
  ]
  const pasoActivo = tienePerfil ? 2 : 1

  return (
    <div className="entrada">
      <div className="pila-3">
        <h1 className="titulo-grande">Empecemos por sus medidas</h1>
        <p className="cuerpo">
          Con su peso, su estatura y su objetivo, el sistema calcula cuánta energía
          necesita al día y arma su rutina.
        </p>
      </div>

      <ol className="pasos-inicio">
        {pasos.map((texto, indice) => (
          <li
            key={texto}
            className={`pasos-inicio__paso${
              indice + 1 === pasoActivo ? ' pasos-inicio__paso--activo' : ''
            }`}
          >
            <span className="pasos-inicio__numero">{indice + 1}</span>
            <span className="cuerpo">{texto}</span>
          </li>
        ))}
      </ol>

      <div className="pila-3">
        {tienePerfil ? (
          <Link to="/comer/plan" className="boton boton--principal">
            Ya las registré: generar mi plan
          </Link>
        ) : (
          <Link to="/avance/medidas/editar" className="boton boton--principal">
            Registrar mis medidas
          </Link>
        )}
        <p className="nota-al-pie centrado">Toma menos de dos minutos</p>
      </div>
    </div>
  )
}

function TarjetaComer({ plan, menu }) {
  const total = plan.macronutrientes.reduce((suma, macro) => suma + macro.porcentaje, 0) || 100

  return (
    <div className="tarjeta">
      <div className="tarjeta__cabecera">
        <span className="rotulo">Comer hoy</span>
        {menu && (
          <span className="apoyo mono">{quetzales(menu.costo_diario_quetzales)}</span>
        )}
      </div>

      <p className="cifra-con-unidad">
        <span className="cifra-tarjeta">{entero(plan.calorias_objetivo)}</span>
        <span className="apoyo">kcal</span>
      </p>

      <div className="macros" role="img" aria-label="Reparto de macronutrientes">
        {plan.macronutrientes.map((macro) => (
          <span
            key={macro.nombre}
            className={`macros__segmento macros__segmento--${clasePorMacro(macro.nombre)}`}
            style={{ width: `${(macro.porcentaje / total) * 100}%` }}
          />
        ))}
      </div>

      <div className="macros__leyenda">
        {plan.macronutrientes.map((macro) => (
          <div key={macro.nombre} className="pila-2">
            <span className="cifra-pequena">{macro.gramos} g</span>
            <span className="cifras__rotulo">{macro.nombre}</span>
          </div>
        ))}
      </div>

      <Link to="/comer" className="boton boton--secundario">
        Ver el menú de hoy
      </Link>
    </div>
  )
}

/** El color de cada macronutriente es el mismo en la barra y en la leyenda. */
function clasePorMacro(nombre) {
  if (nombre === 'Proteína') return 'proteina'
  if (nombre === 'Grasa') return 'grasa'
  return 'carbohidrato'
}

function TarjetaEntrenar({ sesion, rutina, entrenamiento }) {
  const racha = entrenamiento?.racha_semanas ?? 0
  const visibles = sesion?.ejercicios?.slice(0, 2) ?? []
  const restantes = (sesion?.ejercicios?.length ?? 0) - visibles.length

  return (
    <div className={`tarjeta${sesion ? ' tarjeta--destacada' : ''}`}>
      <div className="tarjeta__cabecera">
        <span className="rotulo">Entrenar hoy</span>
        {racha > 0 && (
          <span className="chip chip--ok">
            {racha} {racha === 1 ? 'semana seguida' : 'semanas seguidas'}
          </span>
        )}
      </div>

      {sesion ? (
        <>
          <div className="pila-2">
            <p className="titulo-grupo">{sesion.nombre_grupo}</p>
            <p className="apoyo mono">
              {sesion.ejercicios.length} ejercicios · {sesion.series_totales} series ·{' '}
              {sesion.duracion_estimada_minutos} min
            </p>
          </div>

          <div className="lista lista--desnuda">
            {visibles.map((ejercicio) => (
              <div key={ejercicio.ejercicio_id} className="lista__fila">
                <span className="cuerpo crece">{ejercicio.nombre}</span>
                <span className="lista__valor lista__valor--pequeno">
                  {ejercicio.series}×{ejercicio.repeticiones_min}–{ejercicio.repeticiones_max}
                </span>
              </div>
            ))}
            {restantes > 0 && (
              <Link to="/entrenar" className="lista__fila">
                <span className="apoyo crece">y {restantes} más</span>
                <span className="boton-texto">Ver</span>
              </Link>
            )}
          </div>

          <Link to={`/entrenar/${sesion.id}`} className="boton boton--principal">
            Entrenar ahora
          </Link>
        </>
      ) : (
        <>
          <div className="pila-2">
            <p className="titulo-grupo">Descanso</p>
            <p className="cuerpo">
              {rutina
                ? 'Hoy no le toca sesión. El descanso es parte del programa: es cuando el músculo se repara.'
                : 'Todavía no tiene rutina armada.'}
            </p>
          </div>
          <Link to="/entrenar" className="boton boton--secundario">
            Ver la semana completa
          </Link>
        </>
      )}
    </div>
  )
}

/** La única fila punteada de la pantalla: lo que falta por hacer esta semana. */
function FilaDelPeso({ reporte }) {
  const puntos = reporte?.puntos ?? []
  const ultimo = puntos[puntos.length - 1] ?? null
  const dias = diasDesde(ultimo?.fecha)

  let detalle = 'Todavía no ha anotado ningún peso.'
  if (ultimo) {
    if (dias === 0) detalle = `Último: ${ultimo.peso_kg} kg, hoy`
    else if (dias === 1) detalle = `Último: ${ultimo.peso_kg} kg, hace 1 día`
    else detalle = `Último: ${ultimo.peso_kg} kg, hace ${dias} días`
  }

  return (
    <Link to="/avance" className="fila-punteada">
      <span className="pila-2">
        <span className="lista__titulo">Su peso de la semana</span>
        <span className="lista__detalle">{detalle}</span>
      </span>
      <span className="boton-texto">Anotar</span>
    </Link>
  )
}
