/**
 * Historial de medidas (historia HU-05).
 *
 * Muestra la evolución de las medidas de la cuenta en sesión, de la medición más
 * reciente a la más antigua. El servidor filtra por el titular de la sesión, de
 * modo que no existe forma de consultar medidas ajenas (regla del negocio RN-06).
 *
 * La tabla de cinco columnas desaparece: en un teléfono se desplazaba de lado y
 * había que arrastrarla para leer el cambio de peso, que es justamente lo que se
 * viene a mirar. Ahora es una lista de filas con la fecha, el peso y el cambio
 * respecto de la medición anterior.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import AvisoDeError from '../componentes/AvisoDeError.jsx'
import Pildoras from '../componentes/Pildoras.jsx'
import { PESTANAS_AVANCE } from '../datos/secciones.js'
import {
  CONDICIONES_MEDICAS,
  NIVELES_ACTIVIDAD,
  NIVELES_EXPERIENCIA,
  OBJETIVOS,
  ZONAS_LESION,
  etiquetaDe,
} from '../datos/catalogos.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioPerfil } from '../servicios/api.js'
import { conSigno, fechaBreve, fechaLarga } from '../utilidades/formatos.js'

/** Diferencia de peso frente a la medición anterior, con su color. */
function describirCambio(actual, anterior) {
  if (anterior === undefined) return { texto: 'Primera medición', clase: 'tinta-4' }
  const diferencia = Math.round((actual - anterior) * 100) / 100
  if (diferencia === 0) return { texto: 'Sin cambio', clase: 'tinta-4' }
  return {
    texto: `${conSigno(diferencia, 2)} kg`,
    clase: diferencia > 0 ? 'tinta-peligro' : 'tinta-ok',
  }
}

/**
 * La clasificación del índice de masa corporal decide su color.
 *
 * El servidor devuelve el texto completo —«Peso normal», «Sobrepeso»— y solo
 * uno de ellos no pide atención.
 */
function claseDeClasificacion(clasificacion) {
  return clasificacion === 'Peso normal' ? 'tinta-ok' : 'tinta-aviso'
}

export default function HistorialMedidas() {
  const { token } = useSesion()

  const [historial, setHistorial] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      setHistorial(await servicioPerfil.consultarHistorial(token))
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
        <span className="solo-lectores">Cargando su historial…</span>
      </div>
    )
  }

  if (error) return <AvisoDeError mensaje={error} alReintentar={cargar} />

  if (historial.length === 0) {
    return (
      <div className="vacio">
        <h1 className="vacio__titulo">Todavía no ha registrado sus medidas</h1>
        <p className="cuerpo">
          Complete su perfil biométrico para que el sistema pueda calcular su plan.
        </p>
        <Link to="/avance/medidas/editar" className="boton boton--principal">
          Registrar mis medidas
        </Link>
      </div>
    )
  }

  const vigente = historial[0]

  return (
    <div className="pila">
      <div className="pila-2">
        <h1 className="titulo-pantalla">Mis medidas</h1>
        <p className="apoyo">Las que el sistema usa para calcular su plan.</p>
      </div>

      <Pildoras etiquetaGrupo="Secciones de avance" opciones={PESTANAS_AVANCE} />

      <div className="tarjeta tarjeta--protagonista">
        <div className="fila--entre">
          <span className="rotulo">Medición vigente</span>
          <span className="chip chip--ok">{fechaBreve(vigente.fecha_registro)}</span>
        </div>

        <div className="rejilla-medidas">
          <div className="pila-2">
            <span className="cifras__valor">{vigente.peso_kg} kg</span>
            <span className="cifras__rotulo">Peso</span>
          </div>
          <div className="pila-2">
            <span className="cifras__valor">{vigente.estatura_cm} cm</span>
            <span className="cifras__rotulo">Estatura</span>
          </div>
          <div className="pila-2">
            <span className="cifras__valor">{vigente.indice_masa_corporal}</span>
            <span className="cifras__rotulo">
              IMC ·{' '}
              <span className={claseDeClasificacion(vigente.clasificacion_masa_corporal)}>
                {vigente.clasificacion_masa_corporal}
              </span>
            </span>
          </div>
          <div className="pila-2">
            <span className="cifras__valor">{vigente.dias_entrenamiento_semana}</span>
            <span className="cifras__rotulo">días por semana</span>
          </div>
        </div>

        <div className="chips">
          <span className="chip">{etiquetaDe(OBJETIVOS, vigente.objetivo)}</span>
          <span className="chip">{etiquetaDe(NIVELES_ACTIVIDAD, vigente.nivel_actividad)}</span>
          <span className="chip">
            {etiquetaDe(NIVELES_EXPERIENCIA, vigente.nivel_experiencia)}
          </span>
          {(vigente.lesiones ?? []).map((zona) => (
            <span key={zona} className="chip">
              Lesión: {etiquetaDe(ZONAS_LESION, zona)}
            </span>
          ))}
        </div>
      </div>

      {vigente.requiere_valoracion_profesional && (
        <div className="aviso aviso--aviso" role="status">
          <p>
            Declaró:{' '}
            {vigente.condiciones
              .map((condicion) => etiquetaDe(CONDICIONES_MEDICAS, condicion).toLowerCase())
              .join(', ')}
            . Con esa condición el sistema no genera planes: consulte a un profesional de la
            salud. Si ya no aplica, actualice sus medidas.
          </p>
        </div>
      )}

      <div className="pila-3">
        <span className="rotulo">
          {historial.length}{' '}
          {historial.length === 1 ? 'medición registrada' : 'mediciones registradas'}
        </span>
        <div className="lista">
          {historial.map((medicion, posicion) => {
            // El historial llega de la más reciente a la más antigua, de modo
            // que la medición previa en el tiempo es la siguiente de la lista.
            const previa = historial[posicion + 1]
            const cambio = describirCambio(medicion.peso_kg, previa?.peso_kg)
            return (
              <div key={medicion.id} className="lista__fila">
                <span className="lista__fecha">{fechaBreve(medicion.fecha_registro)}</span>
                <span className="lista__etiqueta crece">{medicion.peso_kg} kg</span>
                <span className={`lista__valor ${cambio.clase}`}>{cambio.texto}</span>
              </div>
            )
          })}
        </div>
      </div>

      <Link to="/avance/medidas/editar" className="boton boton--secundario">
        Actualizar mis medidas
      </Link>

      <div className="pila-2">
        <p className="nota-al-pie">
          Cada actualización agrega una medición nueva; las anteriores no se borran. La más
          reciente es la que el sistema usa para generar sus planes, y se registró el{' '}
          {fechaLarga(vigente.fecha_registro)}.
        </p>
        <p className="nota-al-pie">
          El índice de masa corporal es una referencia general. Ante cualquier condición de
          salud, consulte a un profesional.
        </p>
      </div>
    </div>
  )
}
