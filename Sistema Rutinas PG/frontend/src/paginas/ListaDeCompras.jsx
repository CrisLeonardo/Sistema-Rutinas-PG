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
 *
 * La casilla deja de ser la del navegador y pasa a ser un cuadrado de 24 px con
 * su fila entera como área de toque: se marca de pie en un puesto, con una mano
 * ocupada.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import AvisoDeError from '../componentes/AvisoDeError.jsx'
import CabeceraPantalla from '../componentes/CabeceraPantalla.jsx'
import Icono from '../componentes/Icono.jsx'
import Pildoras from '../componentes/Pildoras.jsx'
import { PESTANAS_COMER } from '../datos/secciones.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPlan } from '../servicios/api.js'
import { quetzales, quetzalesEnteros } from '../utilidades/formatos.js'

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
    return (
      <div className="pila" aria-busy="true">
        <div className="esqueleto esqueleto--titulo" />
        <div className="esqueleto esqueleto--tarjeta" />
        <div className="esqueleto esqueleto--tarjeta" />
        <span className="solo-lectores">Cargando su lista…</span>
      </div>
    )
  }

  if (error) return <AvisoDeError mensaje={error} alReintentar={cargar} />

  if (!lista) {
    return (
      <div className="vacio">
        <h1 className="vacio__titulo">Todavía no tiene lista de compras</h1>
        <p className="cuerpo">La lista se arma con el menú de su plan de alimentación.</p>
        <Link to="/comer/plan" className="boton boton--principal">
          Generar mi plan
        </Link>
      </div>
    )
  }

  const totalRenglones = lista.alimentos_distintos
  const completados = lista.grupos.reduce(
    (suma, grupo) =>
      suma + grupo.renglones.filter((renglon) => marcados.has(renglon.alimento_id)).length,
    0,
  )
  const porcentaje = totalRenglones ? Math.round((completados / totalRenglones) * 100) : 0

  return (
    <div className="pila">
      <CabeceraPantalla
        titulo="Lista de compras"
        hacia="/comer"
        compacta
        accion={
          <button
            type="button"
            className="boton boton--circular no-imprimir"
            onClick={() => window.print()}
            aria-label="Imprimir la lista"
          >
            <Icono nombre="printer" tamano={19} />
          </button>
        }
      />

      <Pildoras etiquetaGrupo="Secciones de alimentación" opciones={PESTANAS_COMER} />

      <div className="tarjeta tarjeta--protagonista">
        <div className="fila--entre fila--abajo">
          <div className="pila-2">
            <span className="rotulo">Semana completa</span>
            <span className="cifra-costo">{quetzales(lista.costo_total_quetzales)}</span>
          </div>
          <span className="apoyo mono a-la-derecha">
            {quetzalesEnteros(lista.costo_mensual_quetzales)}
            <br />
            al mes
          </span>
        </div>

        <div className="pila-2 no-imprimir">
          <div className="fila--entre">
            <span className="apoyo">
              {completados} de {totalRenglones} comprados
            </span>
            <span className="apoyo mono">{porcentaje} %</span>
          </div>
          <div
            className="progreso"
            role="progressbar"
            aria-label="Avance de la compra"
            aria-valuenow={completados}
            aria-valuemin={0}
            aria-valuemax={totalRenglones}
          >
            <div className="progreso__relleno" style={{ width: `${porcentaje}%` }} />
          </div>
        </div>
      </div>

      {lista.grupos.map((grupo) => (
        <div className="tarjeta tarjeta--densa" key={grupo.categoria}>
          <div className="tarjeta__cabecera">
            <h2 className="titulo-tarjeta">{grupo.nombre_categoria}</h2>
            <span className="apoyo mono">{quetzales(grupo.costo_quetzales)}</span>
          </div>

          <div className="lista lista--desnuda">
            {grupo.renglones.map((renglon) => {
              const comprado = marcados.has(renglon.alimento_id)
              return (
                <button
                  key={renglon.alimento_id}
                  type="button"
                  className={`lista__fila${comprado ? ' renglon-comprado' : ''}`}
                  onClick={() => alternar(renglon.alimento_id)}
                  aria-pressed={comprado}
                >
                  <span className={`casilla${comprado ? ' casilla--marcada' : ''}`} aria-hidden="true">
                    {comprado && <Icono nombre="tick-02" tamano={15} />}
                  </span>
                  <span className="lista__titulo crece">{renglon.nombre}</span>
                  <span className="lista__valor">{renglon.cantidad_de_mercado}</span>
                </button>
              )
            })}
          </div>
        </div>
      ))}

      {completados > 0 && (
        <button type="button" className="boton boton--secundario no-imprimir" onClick={limpiar}>
          Desmarcar todo
        </button>
      )}

      <div className="pila-2">
        <p className="nota-al-pie">{lista.aviso_costo}</p>
        <p className="nota-al-pie">
          <strong>Cómo usarla.</strong> Marque cada alimento conforme lo compre. Las cantidades
          alcanzan para siete días siguiendo el menú completo; si comparte la comida con su
          familia, multiplique por las personas que van a comer lo mismo.
        </p>
      </div>
    </div>
  )
}
