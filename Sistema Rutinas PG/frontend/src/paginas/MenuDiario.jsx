/**
 * Menú del día (historia HU-08).
 *
 * Presenta el reparto del plan en los cinco tiempos de comida, con las
 * cantidades en gramos y también en medidas caseras, porque la mayoría de los
 * hogares del municipio no dispone de báscula de cocina.
 *
 * Dos cosas cambian respecto de la versión anterior. Los tiempos pequeños se
 * pliegan en una sola fila: quien abre esta pantalla a las siete de la mañana
 * quiere el desayuno, no las cinco comidas del día a la vez. Y el sustituto
 * deja de ser un desplegable dentro de cada porción —cinco botones repartidos
 * por la tarjeta— para ser un enlace al pie del tiempo que abre una hoja con
 * todos los cambios posibles de esa comida.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import AvisoDeError from '../componentes/AvisoDeError.jsx'
import Hoja from '../componentes/Hoja.jsx'
import Icono from '../componentes/Icono.jsx'
import Pildoras from '../componentes/Pildoras.jsx'
import { PESTANAS_COMER } from '../datos/secciones.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPlan } from '../servicios/api.js'
import { entero, quetzales, quetzalesEnteros } from '../utilidades/formatos.js'

export default function MenuDiario() {
  const { token } = useSesion()

  const [menu, setMenu] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [tiempoConSustitutos, setTiempoConSustitutos] = useState(null)
  const [restoDesplegado, setRestoDesplegado] = useState(false)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      setMenu(await servicioPlan.consultarMenu(token))
      setError(null)
    } catch (fallo) {
      if (fallo instanceof ErrorApi && fallo.codigo === 404) {
        setMenu(null)
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

  if (cargando) {
    return (
      <div className="pila" aria-busy="true">
        <div className="esqueleto esqueleto--titulo" />
        <div className="esqueleto esqueleto--fila" />
        <div className="esqueleto esqueleto--tarjeta" />
        <span className="solo-lectores">Cargando su menú…</span>
      </div>
    )
  }

  if (error) return <AvisoDeError mensaje={error} alReintentar={cargar} />

  if (!menu) {
    return (
      <div className="vacio">
        <h1 className="vacio__titulo">Todavía no tiene menú</h1>
        <p className="cuerpo">Su menú se arma junto con su plan de alimentación.</p>
        <Link to="/comer/plan" className="boton boton--principal">
          Generar mi plan
        </Link>
      </div>
    )
  }

  // Los tiempos que llegan al promedio del día se muestran abiertos; los que
  // quedan por debajo —las refacciones— se pliegan en una sola fila que se
  // despliega al tocarla. El criterio sale de los datos y no de una lista fija
  // de nombres: el reparto de tiempos lo decide el servidor.
  const energiaTotal = menu.tiempos.reduce((suma, tiempo) => suma + tiempo.energia_kcal, 0)
  const promedio = menu.tiempos.length ? energiaTotal / menu.tiempos.length : 0
  const abiertos = menu.tiempos.filter((tiempo) => tiempo.energia_kcal >= promedio)
  const plegados = menu.tiempos.filter((tiempo) => tiempo.energia_kcal < promedio)
  const energiaPlegada = plegados.reduce((suma, tiempo) => suma + tiempo.energia_kcal, 0)

  const visibles = restoDesplegado ? menu.tiempos : abiertos

  return (
    <div className="pila">
      <div className="fila--entre">
        <div className="pila-2">
          <h1 className="titulo-pantalla">Qué comer hoy</h1>
          <p className="apoyo">Cinco tiempos · gramos y medida de cocina</p>
        </div>
        <button
          type="button"
          className="boton boton--circular no-imprimir"
          onClick={() => window.print()}
          aria-label="Imprimir el menú"
        >
          <Icono nombre="printer" tamano={19} />
        </button>
      </div>

      <Pildoras etiquetaGrupo="Secciones de alimentación" opciones={PESTANAS_COMER} />

      <div className="cifras">
        <div className="cifras__columna">
          <span className="cifras__valor">{entero(menu.energia_kcal)}</span>
          <span className="cifras__rotulo">kcal del menú</span>
        </div>
        <div className="cifras__columna">
          <span className="cifras__valor">{menu.proteina_g} g</span>
          <span className="cifras__rotulo">proteína</span>
        </div>
        <div className="cifras__columna">
          <span className="cifras__valor">{quetzales(menu.costo_diario_quetzales)}</span>
          <span className="cifras__rotulo">cuesta el día</span>
        </div>
      </div>

      {visibles.map((tiempo) => (
        <TiempoDeComida
          key={tiempo.nombre}
          tiempo={tiempo}
          alVerCambios={() => setTiempoConSustitutos(tiempo)}
        />
      ))}

      {plegados.length > 0 && !restoDesplegado && (
        <button
          type="button"
          className="fila-punteada no-imprimir"
          onClick={() => setRestoDesplegado(true)}
        >
          <span className="apoyo crece">{plegados.map((tiempo) => tiempo.nombre).join(' · ')}</span>
          <span className="apoyo mono">{entero(energiaPlegada)} kcal</span>
        </button>
      )}

      <div className="pila-2">
        <p className="nota-al-pie">
          El menú queda a {menu.desviacion_energia_porcentaje} % de lo que su plan pide, con{' '}
          {menu.alimentos_distintos} alimentos distintos. Esa diferencia viene de redondear las
          porciones a cantidades que se puedan servir. Seguirlo cuesta cerca de{' '}
          {quetzalesEnteros(menu.costo_mensual_quetzales)} al mes con los precios del catálogo.
          {menu.porciones_sin_precio > 0 &&
            ` ${menu.porciones_sin_precio} porciones todavía no tienen precio registrado, de modo que el total se queda corto.`}
        </p>
        <p className="nota-al-pie">
          <strong>Importante.</strong> Este menú es una propuesta, no una obligación. Puede
          intercambiar alimentos de una misma categoría respetando las cantidades. Ante
          cualquier condición de salud, consulte a un profesional.
        </p>
      </div>

      {tiempoConSustitutos && (
        <Hoja
          titulo={`Cambios en ${tiempoConSustitutos.nombre.toLowerCase()}`}
          descripcion="Cada alternativa aporta prácticamente lo mismo que el alimento que sustituye."
          alCerrar={() => setTiempoConSustitutos(null)}
        >
          <div className="lista">
            {tiempoConSustitutos.porciones
              .filter((porcion) => porcion.sustituto)
              .map((porcion) => (
                <div key={porcion.alimento_id} className="lista__fila">
                  <span className="pila-2 crece">
                    <span className="lista__titulo">{porcion.nombre}</span>
                    <span className="lista__detalle">
                      Puede cambiarlo por {porcion.sustituto.nombre}, {porcion.sustituto.gramos} g
                      {porcion.sustituto.medida_casera
                        ? ` (${porcion.sustituto.medida_casera})`
                        : ''}
                    </span>
                  </span>
                </div>
              ))}
          </div>
        </Hoja>
      )}
    </div>
  )
}

function TiempoDeComida({ tiempo, alVerCambios }) {
  const tieneSustitutos = tiempo.porciones.some((porcion) => porcion.sustituto)

  return (
    <div className="tarjeta tarjeta--densa">
      <div className="tarjeta__cabecera">
        <h2 className="titulo-tarjeta">{tiempo.nombre}</h2>
        <span className="apoyo mono">{entero(tiempo.energia_kcal)} kcal</span>
      </div>

      <div className="lista lista--desnuda">
        {tiempo.porciones.map((porcion) => (
          <div key={porcion.alimento_id} className="lista__fila">
            <span className="pila-2 crece">
              <span className="lista__etiqueta">{porcion.nombre}</span>
              {porcion.cantidad_en_medida_casera && (
                <span className="lista__detalle">{porcion.cantidad_en_medida_casera}</span>
              )}
            </span>
            <span className="lista__valor">{porcion.gramos} g</span>
          </div>
        ))}
      </div>

      {tieneSustitutos && (
        <button type="button" className="boton-texto no-imprimir" onClick={alVerCambios}>
          ¿No consiguió algo? Ver cambios
        </button>
      )}
    </div>
  )
}
