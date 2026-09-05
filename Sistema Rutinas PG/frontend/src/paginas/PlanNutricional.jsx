/**
 * Mi plan de alimentación (historia HU-06).
 *
 * Cada cifra técnica va acompañada de una explicación en lenguaje sencillo, tal
 * como exige el requerimiento no funcional 4.5.3, y todo plan muestra el aviso
 * de consulta profesional de la regla del negocio *e*.
 *
 * La pantalla tenía cinco tarjetas y dos tablas, y la cifra que de verdad
 * importa —cuánta energía comer— competía con la comparación contra las
 * fórmulas clínicas. Ahora la energía diaria es la tarjeta protagonista; la
 * comprobación se resume en una línea y su tabla completa vive en una hoja, y
 * la explicación de cada macronutriente se abre desde su propia fila.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import AvisoDeError from '../componentes/AvisoDeError.jsx'
import CabeceraPantalla from '../componentes/CabeceraPantalla.jsx'
import Hoja from '../componentes/Hoja.jsx'
import Icono from '../componentes/Icono.jsx'
import Pildoras from '../componentes/Pildoras.jsx'
import { PESTANAS_COMER } from '../datos/secciones.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPlan } from '../servicios/api.js'
import { entero, fechaYHora } from '../utilidades/formatos.js'

/** El color de cada macronutriente es el mismo en la barra y en la leyenda. */
const CLASES_MACRO = {
  Proteína: 'proteina',
  Carbohidrato: 'carbohidrato',
  Grasa: 'grasa',
}

export default function PlanNutricional() {
  const { token } = useSesion()

  const [plan, setPlan] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [generando, setGenerando] = useState(false)
  const [error, setError] = useState(null)
  const [sinPerfil, setSinPerfil] = useState(false)
  const [hojaAbierta, setHojaAbierta] = useState(null)
  const [macroAbierto, setMacroAbierto] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      setPlan(await servicioPlan.consultarVigente(token))
      setError(null)
    } catch (fallo) {
      // Que todavía no exista un plan no es un error: es el estado inicial.
      if (fallo instanceof ErrorApi && fallo.codigo === 404) {
        setPlan(null)
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

  const generar = async () => {
    setGenerando(true)
    setError(null)
    setSinPerfil(false)
    try {
      setPlan(await servicioPlan.generar(token))
    } catch (fallo) {
      // El servidor responde 409 cuando el perfil biométrico está incompleto
      // (apartado 4.8.3): en ese caso se ofrece el camino para completarlo.
      if (fallo instanceof ErrorApi && fallo.codigo === 409) setSinPerfil(true)
      setError(fallo.message)
    } finally {
      setGenerando(false)
    }
  }

  if (cargando) {
    return (
      <div className="pila" aria-busy="true">
        <div className="esqueleto esqueleto--titulo" />
        <div className="esqueleto esqueleto--tarjeta" />
        <div className="esqueleto esqueleto--fila" />
        <span className="solo-lectores">Cargando su plan…</span>
      </div>
    )
  }

  if (!plan) {
    return (
      <div className="pila">
        <Pildoras etiquetaGrupo="Secciones de alimentación" opciones={PESTANAS_COMER} />
        {error && <AvisoDeError mensaje={error} />}
        <div className="vacio">
          <h1 className="vacio__titulo">Todavía no ha generado su plan</h1>
          <p className="cuerpo">Con sus medidas ya registradas, el cálculo toma unos segundos.</p>
          {sinPerfil ? (
            <Link to="/avance/medidas/editar" className="boton boton--principal">
              Registrar mis medidas
            </Link>
          ) : (
            <button
              type="button"
              className="boton boton--principal"
              onClick={generar}
              disabled={generando}
            >
              {generando ? 'Calculando…' : 'Generar mi plan'}
            </button>
          )}
        </div>
      </div>
    )
  }

  const macros = plan.macronutrientes
  const totalPorcentaje = macros.reduce((suma, macro) => suma + macro.porcentaje, 0) || 100

  return (
    <div className="pila">
      <CabeceraPantalla
        titulo="Mi plan de alimentación"
        hacia="/comer"
        compacta
        accion={
          <button
            type="button"
            className="boton boton--circular no-imprimir"
            onClick={() => window.print()}
            aria-label="Imprimir el plan"
          >
            <Icono nombre="printer" tamano={19} />
          </button>
        }
      />

      <Pildoras etiquetaGrupo="Secciones de alimentación" opciones={PESTANAS_COMER} />

      {plan.advertencias_de_salud?.length > 0 && (
        <div className="aviso aviso--aviso" role="alert">
          {plan.advertencias_de_salud.map((advertencia) => (
            <p key={advertencia}>{advertencia}</p>
          ))}
        </div>
      )}

      <div className="tarjeta tarjeta--protagonista">
        <span className="rotulo">Su energía diaria</span>
        <p className="cifra-con-unidad">
          <span className="cifra-protagonista">{entero(plan.calorias_objetivo)}</span>
          <span className="apoyo">kcal</span>
        </p>
        <p className="cuerpo">{plan.explicacion_objetivo}</p>
      </div>

      <div className="lista">
        <div className="lista__fila">
          <span className="lista__etiqueta crece">Gasto en reposo</span>
          <span className="lista__valor">{entero(plan.tasa_metabolica_basal)} kcal</span>
        </div>
        <div className="lista__fila">
          <span className="lista__etiqueta crece">Gasto con su actividad</span>
          <span className="lista__valor">{entero(plan.gasto_energetico_total)} kcal</span>
        </div>
        <div className="lista__fila">
          <span className="lista__etiqueta crece">Agua sugerida</span>
          <span className="lista__valor">{(plan.agua_ml / 1000).toFixed(1)} litros</span>
        </div>
      </div>

      <div className="tarjeta tarjeta--densa">
        <span className="rotulo">Cómo repartirla</span>

        <div className="macros" role="img" aria-label="Reparto de macronutrientes">
          {macros.map((macro) => (
            <span
              key={macro.nombre}
              className={`macros__segmento macros__segmento--${CLASES_MACRO[macro.nombre] ?? 'carbohidrato'}`}
              style={{ width: `${(macro.porcentaje / totalPorcentaje) * 100}%` }}
            />
          ))}
        </div>

        <div className="lista lista--desnuda">
          {macros.map((macro) => (
            <button
              key={macro.nombre}
              type="button"
              className="lista__fila"
              onClick={() => setMacroAbierto(macro)}
            >
              <span
                className={`macros__punto macros__segmento--${CLASES_MACRO[macro.nombre] ?? 'carbohidrato'}`}
              />
              <span className="lista__etiqueta crece">{macro.nombre}</span>
              <span className="lista__valor">
                {macro.gramos} g · {macro.porcentaje} %
              </span>
            </button>
          ))}
        </div>

        <p className="nota-al-pie">
          Los tres suman {entero(plan.energia_de_los_macronutrientes)} kcal, que es exactamente
          su energía diaria.
        </p>
      </div>

      <button
        type="button"
        className={`aviso ${plan.dentro_del_margen_admitido ? 'aviso--ok' : 'aviso--aviso'} centrado`}
        onClick={() => setHojaAbierta('comprobacion')}
      >
        Comprobado contra Mifflin-St Jeor y Harris-Benedict:{' '}
        {plan.margen_error_porcentaje.toFixed(2)} % de diferencia.
      </button>

      {plan.correcciones_de_seguridad?.length > 0 && (
        <div className="tarjeta tarjeta--densa">
          <span className="rotulo">Ajustes que hizo el sistema</span>
          <p className="apoyo">
            Su plan no es el resultado crudo del cálculo. Estas son las correcciones que se le
            aplicaron para que sea seguro seguirlo, y por qué.
          </p>
          <div className="lista lista--desnuda">
            {plan.correcciones_de_seguridad.map((correccion) => (
              <div key={correccion} className="lista__fila">
                <span className="cuerpo">{correccion}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && <AvisoDeError mensaje={error} />}

      <div className="pila-2">
        <p className="nota-al-pie">
          <strong>Importante.</strong> {plan.aviso_profesional}
        </p>
        <p className="nota-al-pie">
          Plan generado el {fechaYHora(plan.fecha_generacion)} · Si actualiza sus medidas, vuelva
          a calcularlo para que se ajuste a su peso actual.
        </p>
      </div>

      <button
        type="button"
        className="boton boton--secundario no-imprimir"
        onClick={generar}
        disabled={generando}
      >
        {generando ? 'Calculando…' : 'Volver a calcular'}
      </button>

      {hojaAbierta === 'comprobacion' && (
        <Hoja
          titulo="Cómo se comprobó"
          descripcion={`El plan lo calculó ${
            plan.origen_calculo === 'red_neuronal'
              ? 'el modelo de red neuronal del sistema'
              : 'la fórmula de referencia del sistema'
          }, y se comparó con dos fórmulas usadas en nutrición clínica.`}
          alCerrar={() => setHojaAbierta(null)}
        >
          <div className="lista">
            <div className="lista__fila">
              <span className="lista__etiqueta crece">Fórmula de Mifflin-St Jeor</span>
              <span className="lista__valor">{entero(plan.referencia_mifflin)} kcal</span>
            </div>
            <div className="lista__fila">
              <span className="lista__etiqueta crece">Fórmula de Harris-Benedict</span>
              <span className="lista__valor">
                {entero(plan.referencia_harris_benedict)} kcal
              </span>
            </div>
            <div className="lista__fila">
              <span className="lista__etiqueta crece">Su plan</span>
              <span className="lista__valor">{entero(plan.calorias_objetivo)} kcal</span>
            </div>
            <div className="lista__fila">
              <span className="lista__etiqueta crece">Diferencia con su plan</span>
              <span
                className={`lista__valor ${
                  plan.dentro_del_margen_admitido ? 'tinta-ok' : 'tinta-peligro'
                }`}
              >
                {plan.margen_error_porcentaje.toFixed(2)} %
              </span>
            </div>
          </div>
          <p className="apoyo">
            {plan.dentro_del_margen_admitido
              ? 'Dentro del margen admitido del 5 %'
              : 'Fuera del margen admitido del 5 %'}
          </p>
        </Hoja>
      )}

      {macroAbierto && (
        <Hoja
          titulo={macroAbierto.nombre}
          descripcion={`${macroAbierto.gramos} g al día · ${macroAbierto.porcentaje} % de su energía · ${entero(macroAbierto.kilocalorias)} kcal`}
          alCerrar={() => setMacroAbierto(null)}
        >
          <p className="cuerpo">{macroAbierto.explicacion}</p>
        </Hoja>
      )}
    </div>
  )
}
