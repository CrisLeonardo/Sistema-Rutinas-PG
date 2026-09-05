/**
 * Mi evolución (historia HU-10).
 *
 * Presenta lo que ha cambiado desde que empezó: el peso, la constancia y el
 * contraste entre el plan inicial y el vigente. Los agregados llegan calculados
 * del servidor, de modo que esta pantalla solo dibuja.
 *
 * Tenía cuatro gráficas y una tabla de comparación, todas al mismo nivel. Ahora
 * el peso es la tarjeta protagonista —es la cifra por la que se abre la
 * pantalla—, la constancia queda en una fila de cifras y las barras de sesiones,
 * y la comparación de planes se reduce a una fila que abre su tabla en una hoja.
 * Las gráficas de adherencia y de cintura pasan también a esa hoja: son datos de
 * respaldo, no la respuesta.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import AvisoDeError from '../componentes/AvisoDeError.jsx'
import GraficaBarras from '../componentes/GraficaBarras.jsx'
import GraficaLineas from '../componentes/GraficaLineas.jsx'
import Hoja from '../componentes/Hoja.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioProgreso } from '../servicios/api.js'
import { conSigno, entero, fechaLarga } from '../utilidades/formatos.js'

export default function Reportes() {
  const { token } = useSesion()

  const [reporte, setReporte] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [hojaAbierta, setHojaAbierta] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      setReporte(await servicioProgreso.consultarReporte(token))
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

  if (cargando) {
    return (
      <div className="pila" aria-busy="true">
        <div className="esqueleto esqueleto--titulo" />
        <div className="esqueleto esqueleto--tarjeta" />
        <div className="esqueleto esqueleto--fila" />
        <span className="solo-lectores">Cargando su evolución…</span>
      </div>
    )
  }

  if (error) return <AvisoDeError mensaje={error} alReintentar={cargar} />

  const puntos = reporte?.puntos ?? []
  const comparacion = reporte?.comparacion_planes

  if (puntos.length === 0) {
    return (
      <div className="vacio">
        <h1 className="vacio__titulo">Todavía no ha registrado ningún avance</h1>
        <p className="cuerpo">
          Sus gráficas aparecerán aquí en cuanto registre su primera semana.
        </p>
        <Link to="/avance" className="boton boton--principal">
          Registrar mi avance
        </Link>
      </div>
    )
  }

  const puntosPeso = puntos.map((punto) => ({ etiqueta: punto.fecha, valor: punto.peso_kg }))
  const puntosSesiones = puntos.map((punto) => ({
    etiqueta: punto.fecha,
    valor: punto.sesiones_cumplidas,
  }))
  const puntosAdherencia = puntos
    .filter((punto) => punto.adherencia_nutricional !== null)
    .map((punto) => ({ etiqueta: punto.fecha, valor: punto.adherencia_nutricional }))
  const conCintura = puntos.filter((punto) => punto.perimetro_cintura_cm !== null)
  const puntosCintura = conCintura.map((punto) => ({
    etiqueta: punto.fecha,
    valor: punto.perimetro_cintura_cm,
  }))

  // El cambio de cintura no viene calculado del servidor: es la diferencia
  // entre la primera y la última medición que lo traen.
  const cambioCintura =
    conCintura.length >= 2
      ? Math.round(
          (conCintura[conCintura.length - 1].perimetro_cintura_cm -
            conCintura[0].perimetro_cintura_cm) *
            10,
        ) / 10
      : null

  const baja = reporte.cambio_total_kg !== null && reporte.cambio_total_kg < 0

  return (
    <div className="pila">
      <div className="pila-2">
        <h1 className="titulo-pantalla">Mi evolución</h1>
        <p className="apoyo">Lo que ha cambiado desde que empezó, semana a semana.</p>
      </div>

      <div className="tarjeta tarjeta--protagonista">
        <div className="fila--entre fila--abajo">
          <div className="pila-2">
            <span className="rotulo">Peso</span>
            <span className="cifra-con-unidad">
              <span className="cifra-evolucion">{reporte.peso_actual}</span>
              <span className="apoyo">kg</span>
            </span>
          </div>
          {reporte.cambio_total_kg !== null && (
            <div className="pila-2 a-la-derecha">
              <span className={`cifra-pequena ${baja ? 'tinta-ok' : 'tinta-peligro'}`}>
                {conSigno(reporte.cambio_total_kg, 1)} kg
              </span>
              <span className="cifras__rotulo">desde {reporte.peso_inicial} kg</span>
            </div>
          )}
        </div>
        <GraficaLineas
          puntos={puntosPeso}
          etiquetaValor="kg"
          descripcion="Evolución de su peso registrado"
        />
      </div>

      <div className="cifras">
        <div className="cifras__columna">
          <span className="cifras__valor">{reporte.sesiones_totales}</span>
          <span className="cifras__rotulo">sesiones</span>
        </div>
        <div className="cifras__columna">
          <span className="cifras__valor">
            {reporte.adherencia_promedio === null ? '—' : `${reporte.adherencia_promedio} %`}
          </span>
          <span className="cifras__rotulo">del plan</span>
        </div>
        <div className="cifras__columna">
          <span className={`cifras__valor ${cambioCintura < 0 ? 'tinta-ok' : ''}`}>
            {cambioCintura === null ? '—' : `${conSigno(cambioCintura, 1)} cm`}
          </span>
          <span className="cifras__rotulo">cintura</span>
        </div>
      </div>

      <div className="tarjeta tarjeta--densa">
        <span className="rotulo">Sesiones por semana</span>
        <GraficaBarras
          puntos={puntosSesiones}
          etiquetaValor="sesiones"
          descripcion="Sesiones de entrenamiento cumplidas por semana"
        />
        <p className="nota-al-pie">
          {reporte.sesiones_totales} sesiones en total · {reporte.semanas_registradas} semanas
          registradas
        </p>
      </div>

      {(puntosAdherencia.length > 0 || puntosCintura.length > 0) && (
        <button
          type="button"
          className="fila-punteada"
          onClick={() => setHojaAbierta('detalle')}
        >
          <span className="apoyo">Adherencia y cintura, semana a semana</span>
          <span className="boton-texto">Ver</span>
        </button>
      )}

      {comparacion && (
        <button
          type="button"
          className="fila-resumen"
          onClick={() => setHojaAbierta('planes')}
        >
          <span className="apoyo crece">Plan inicial frente al de ahora</span>
          <span className="apoyo mono">
            {comparacion.hubo_cambio
              ? `${conSigno(Math.round(comparacion.diferencia_calorias), 0)} kcal`
              : 'sin cambios'}
          </span>
        </button>
      )}

      <Link to="/avance" className="boton boton--principal">
        Registrar mi avance
      </Link>

      {hojaAbierta === 'detalle' && (
        <Hoja
          titulo="Adherencia y cintura"
          descripcion="Los dos datos opcionales del registro semanal, si los ha ido anotando."
          alCerrar={() => setHojaAbierta(null)}
        >
          {puntosAdherencia.length > 0 && (
            <div className="pila-2">
              <span className="rotulo">Cumplimiento del plan</span>
              <GraficaLineas
                puntos={puntosAdherencia}
                etiquetaValor="%"
                descripcion="Porcentaje de cumplimiento del plan de comidas"
              />
            </div>
          )}
          {puntosCintura.length > 0 && (
            <div className="pila-2">
              <span className="rotulo">Perímetro de cintura</span>
              <GraficaLineas
                puntos={puntosCintura}
                etiquetaValor="cm"
                descripcion="Evolución del perímetro de cintura"
              />
            </div>
          )}
        </Hoja>
      )}

      {hojaAbierta === 'planes' && comparacion && (
        <Hoja
          titulo="Su plan inicial frente al de ahora"
          descripcion={
            comparacion.hubo_cambio
              ? 'Su plan se recalculó conforme cambiaron sus medidas. Así quedó.'
              : `Su plan todavía no ha cambiado: sigue vigente el que se generó el ${fechaLarga(comparacion.fecha_inicial)}.`
          }
          alCerrar={() => setHojaAbierta(null)}
        >
          <div className="lista">
            <div className="lista__fila">
              <span className="lista__detalle crece">Dato</span>
              <span className="lista__detalle lista__valor--fijo">Inicial</span>
              <span className="lista__detalle lista__valor--fijo">Ahora</span>
            </div>
            <FilaComparacion
              nombre="Energía diaria"
              inicial={`${entero(comparacion.calorias_inicial)} kcal`}
              vigente={`${entero(comparacion.calorias_vigente)} kcal`}
            />
            <FilaComparacion
              nombre="Proteína"
              inicial={`${entero(comparacion.proteina_inicial)} g`}
              vigente={`${entero(comparacion.proteina_vigente)} g`}
            />
            <FilaComparacion
              nombre="Carbohidrato"
              inicial={`${entero(comparacion.carbohidrato_inicial)} g`}
              vigente={`${entero(comparacion.carbohidrato_vigente)} g`}
            />
            <FilaComparacion
              nombre="Grasa"
              inicial={`${entero(comparacion.grasa_inicial)} g`}
              vigente={`${entero(comparacion.grasa_vigente)} g`}
            />
          </div>
          {comparacion.hubo_cambio && (
            <p className="apoyo">
              Diferencia de energía:{' '}
              {conSigno(Math.round(comparacion.diferencia_calorias), 0)} kcal al día.
            </p>
          )}
        </Hoja>
      )}
    </div>
  )
}

function FilaComparacion({ nombre, inicial, vigente }) {
  return (
    <div className="lista__fila">
      <span className="lista__etiqueta crece">{nombre}</span>
      <span className="lista__valor lista__valor--fijo lista__valor--tenue">{inicial}</span>
      <span className="lista__valor lista__valor--fijo">{vigente}</span>
    </div>
  )
}
