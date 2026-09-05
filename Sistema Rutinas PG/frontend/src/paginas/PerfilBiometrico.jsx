/**
 * Mis medidas (historia HU-04).
 *
 * El formulario se divide en tres pasos cortos, conforme al requerimiento no
 * funcional 4.5.3. Las validaciones que se aplican aquí son un apoyo a la
 * experiencia de uso: el servidor las vuelve a verificar en su totalidad, según
 * exige el apartado 4.8.3.
 *
 * El indicador de pasos deja de ser una fila de tres círculos con su nombre
 * —que en 390 px se aprieta hasta no leerse— y pasa a ser una barra de tres
 * tramos junto a la flecha de volver, con «Paso 1 de 3» al lado.
 *
 * Los radios desaparecen: el sexo son dos botones, los días de la semana son
 * siete, y la actividad, el objetivo y la experiencia son filas de 56 px con su
 * explicación debajo. Un radio de 20 px es un blanco difícil para el pulgar, y
 * la explicación que va al lado es lo que decide la respuesta.
 */

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import AvisoDeError from '../componentes/AvisoDeError.jsx'
import Icono from '../componentes/Icono.jsx'
import {
  NIVELES_ACTIVIDAD,
  NIVELES_EXPERIENCIA,
  OBJETIVOS,
  RANGOS,
  SEXOS,
  etiquetaDe,
} from '../datos/catalogos.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { ErrorApi, servicioPerfil } from '../servicios/api.js'

const PASOS = [
  { numero: 1, titulo: 'Sus medidas', ayuda: 'Datos con los que se calcula su gasto energético.' },
  {
    numero: 2,
    titulo: 'Su actividad',
    ayuda: 'Cuánto se mueve durante la semana y qué busca lograr.',
  },
  {
    numero: 3,
    titulo: 'Su entrenamiento',
    ayuda: 'Con esto se ajusta el volumen de la rutina.',
  },
]

const FORMULARIO_INICIAL = {
  peso_kg: '',
  estatura_cm: '',
  edad: '',
  sexo: '',
  nivel_actividad: '',
  objetivo: '',
  nivel_experiencia: 'principiante',
  dias_entrenamiento_semana: '3',
}

/** Traduce el índice de masa corporal a una lectura sencilla, igual que el servidor. */
function clasificarIndice(indice) {
  if (indice < 18.5) return 'Peso por debajo de lo normal'
  if (indice < 25) return 'Peso normal'
  if (indice < 30) return 'Sobrepeso'
  return 'Obesidad'
}

/** Calcula el índice mientras el usuario escribe, para dar retroalimentación inmediata. */
function calcularIndice(peso, estatura) {
  const kilogramos = Number(peso)
  const metros = Number(estatura) / 100
  if (!kilogramos || !metros) return null
  return Math.round((kilogramos / metros ** 2) * 100) / 100
}

export default function PerfilBiometrico() {
  const { token } = useSesion()
  const navegar = useNavigate()

  const [formulario, setFormulario] = useState(FORMULARIO_INICIAL)
  const [paso, setPaso] = useState(1)
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)
  const [cargando, setCargando] = useState(true)
  const [teniaPerfil, setTeniaPerfil] = useState(false)

  // Precarga la última medición para que actualizar los datos no obligue a
  // escribirlo todo de nuevo. Aun así, al guardar se crea un registro nuevo y el
  // anterior se conserva (historia HU-05).
  useEffect(() => {
    let vigente = true
    servicioPerfil
      .consultarVigente(token)
      .then((perfil) => {
        if (!vigente) return
        setTeniaPerfil(true)
        setFormulario({
          peso_kg: String(perfil.peso_kg),
          estatura_cm: String(perfil.estatura_cm),
          edad: String(perfil.edad),
          sexo: perfil.sexo,
          nivel_actividad: perfil.nivel_actividad,
          objetivo: perfil.objetivo,
          nivel_experiencia: perfil.nivel_experiencia,
          dias_entrenamiento_semana: String(perfil.dias_entrenamiento_semana),
        })
      })
      .catch(() => {
        // Sin perfil previo se conserva el formulario vacío.
      })
      .finally(() => {
        if (vigente) setCargando(false)
      })
    return () => {
      vigente = false
    }
  }, [token])

  const actualizar = (evento) => {
    const { name, value } = evento.target
    setFormulario((anterior) => ({ ...anterior, [name]: value }))
    setError(null)
  }

  const elegir = (campo, valor) => {
    setFormulario((anterior) => ({ ...anterior, [campo]: valor }))
    setError(null)
  }

  /** Reproduce en la interfaz las reglas que el servidor vuelve a verificar. */
  const validarPaso = (numero) => {
    if (numero === 1) {
      const peso = Number(formulario.peso_kg)
      const estatura = Number(formulario.estatura_cm)
      const edad = Number(formulario.edad)

      if (!formulario.peso_kg || peso < RANGOS.pesoMinimo || peso > RANGOS.pesoMaximo) {
        return `El peso debe estar entre ${RANGOS.pesoMinimo} y ${RANGOS.pesoMaximo} kilogramos.`
      }
      if (
        !formulario.estatura_cm ||
        estatura < RANGOS.estaturaMinima ||
        estatura > RANGOS.estaturaMaxima
      ) {
        return `La estatura debe estar entre ${RANGOS.estaturaMinima} y ${RANGOS.estaturaMaxima} centímetros.`
      }
      if (!formulario.edad || edad < RANGOS.edadMinima) {
        return 'El sistema solo genera planes para personas mayores de dieciocho años.'
      }
      if (edad > RANGOS.edadMaxima) {
        return `La edad no puede superar los ${RANGOS.edadMaxima} años.`
      }
      if (!formulario.sexo) {
        return 'Indique su sexo; las fórmulas de referencia lo requieren.'
      }
    }

    if (numero === 2) {
      if (!formulario.nivel_actividad) return 'Seleccione su nivel de actividad física.'
      if (!formulario.objetivo) return 'Seleccione el objetivo que desea alcanzar.'
    }

    if (numero === 3) {
      const dias = Number(formulario.dias_entrenamiento_semana)
      if (!formulario.nivel_experiencia) return 'Seleccione su nivel de experiencia.'
      if (dias < RANGOS.diasMinimos || dias > RANGOS.diasMaximos) {
        return `Los días de entrenamiento deben estar entre ${RANGOS.diasMinimos} y ${RANGOS.diasMaximos} por semana.`
      }
    }

    return null
  }

  const avanzar = () => {
    const problema = validarPaso(paso)
    if (problema) {
      setError(problema)
      return
    }
    setError(null)
    setPaso((actual) => Math.min(actual + 1, PASOS.length))
  }

  const retroceder = () => {
    setError(null)
    setPaso((actual) => Math.max(actual - 1, 1))
  }

  const enviar = async (evento) => {
    evento.preventDefault()
    for (const numero of [1, 2, 3]) {
      const problema = validarPaso(numero)
      if (problema) {
        setPaso(numero)
        setError(problema)
        return
      }
    }

    setError(null)
    setEnviando(true)
    try {
      await servicioPerfil.registrar(
        {
          peso_kg: Number(formulario.peso_kg),
          estatura_cm: Number(formulario.estatura_cm),
          edad: Number(formulario.edad),
          sexo: formulario.sexo,
          nivel_actividad: formulario.nivel_actividad,
          objetivo: formulario.objetivo,
          nivel_experiencia: formulario.nivel_experiencia,
          dias_entrenamiento_semana: Number(formulario.dias_entrenamiento_semana),
        },
        token,
      )
      navegar('/avance/medidas', { replace: true })
    } catch (fallo) {
      setError(fallo instanceof ErrorApi ? fallo.message : 'No fue posible guardar sus medidas.')
    } finally {
      setEnviando(false)
    }
  }

  const indice = calcularIndice(formulario.peso_kg, formulario.estatura_cm)

  if (cargando) {
    return (
      <div className="pila" aria-busy="true">
        <div className="esqueleto esqueleto--titulo" />
        <div className="esqueleto esqueleto--fila" />
        <div className="esqueleto esqueleto--fila" />
        <span className="solo-lectores">Cargando sus datos…</span>
      </div>
    )
  }

  return (
    <div className="pila-5">
      <div className="cabecera-pantalla">
        {paso === 1 ? (
          <Link to="/avance/medidas" className="cabecera-pantalla__volver" aria-label="Volver">
            <Icono nombre="arrow-left-01" tamano={18} />
          </Link>
        ) : (
          <button
            type="button"
            className="cabecera-pantalla__volver"
            onClick={retroceder}
            aria-label="Volver al paso anterior"
          >
            <Icono nombre="arrow-left-01" tamano={18} />
          </button>
        )}
        <div className="tramos" role="progressbar" aria-valuenow={paso} aria-valuemin={1} aria-valuemax={3}>
          {PASOS.map((definicion) => (
            <span
              key={definicion.numero}
              className={`tramos__tramo${
                definicion.numero <= paso ? ' tramos__tramo--activo' : ''
              }`}
            />
          ))}
        </div>
      </div>

      <div className="pila-2">
        <p className="apoyo mono">Paso {paso} de {PASOS.length}</p>
        <h1 className="titulo-pantalla">{PASOS[paso - 1].titulo}</h1>
        <p className="apoyo">
          {paso === 1 && teniaPerfil
            ? 'Sus medidas anteriores se conservan; esta actualización se agrega a su historial.'
            : PASOS[paso - 1].ayuda}
        </p>
      </div>

      {error && <AvisoDeError mensaje={error} />}

      <form onSubmit={enviar} noValidate className="pila-5">
        {paso === 1 && (
          <>
            <div className="pila-3">
              <div className="campos-par">
                <label className="campo">
                  <span className="campo__etiqueta">Peso (kg)</span>
                  <input
                    name="peso_kg"
                    type="number"
                    inputMode="decimal"
                    step="0.1"
                    min={RANGOS.pesoMinimo}
                    max={RANGOS.pesoMaximo}
                    className="campo__control campo__control--numero"
                    value={formulario.peso_kg}
                    onChange={actualizar}
                    required
                  />
                  <span className="campo__ayuda">
                    Entre {RANGOS.pesoMinimo} y {RANGOS.pesoMaximo} kilogramos.
                  </span>
                </label>

                <label className="campo">
                  <span className="campo__etiqueta">Estatura (cm)</span>
                  <input
                    name="estatura_cm"
                    type="number"
                    inputMode="numeric"
                    min={RANGOS.estaturaMinima}
                    max={RANGOS.estaturaMaxima}
                    className="campo__control campo__control--numero"
                    value={formulario.estatura_cm}
                    onChange={actualizar}
                    required
                  />
                  <span className="campo__ayuda">
                    Por ejemplo, 1.70 metros se escribe como 170.
                  </span>
                </label>
              </div>

              <div className="campos-par">
                <label className="campo">
                  <span className="campo__etiqueta">Edad</span>
                  <input
                    name="edad"
                    type="number"
                    inputMode="numeric"
                    min={RANGOS.edadMinima}
                    max={RANGOS.edadMaxima}
                    className="campo__control campo__control--numero"
                    value={formulario.edad}
                    onChange={actualizar}
                    required
                  />
                  <span className="campo__ayuda">
                    El sistema atiende únicamente a personas mayores de edad.
                  </span>
                </label>

                <fieldset className="campo">
                  <legend className="campo__etiqueta">Sexo</legend>
                  <div className="opciones-fila">
                    {SEXOS.map((opcion) => (
                      <button
                        key={opcion.valor}
                        type="button"
                        className={`opcion-boton opcion-boton--grande${
                          formulario.sexo === opcion.valor ? ' opcion-boton--seleccionada' : ''
                        }`}
                        onClick={() => elegir('sexo', opcion.valor)}
                        aria-pressed={formulario.sexo === opcion.valor}
                      >
                        {opcion.etiqueta}
                      </button>
                    ))}
                  </div>
                  <span className="campo__ayuda">
                    Las fórmulas de Mifflin-St Jeor y Harris-Benedict lo utilizan para calcular
                    su gasto de energía en reposo.
                  </span>
                </fieldset>
              </div>
            </div>

            {indice !== null && (
              <div className="tarjeta tarjeta--densa" role="status">
                <div className="fila--entre">
                  <span className="pila-2 crece">
                    <span className="lista__titulo">Índice de masa corporal</span>
                    <span className="lista__detalle">
                      Referencia general, no un diagnóstico médico.
                    </span>
                  </span>
                  <span className="pila-2 a-la-derecha">
                    <span className="cifra-indice">{indice}</span>
                    <span
                      className={`cifras__rotulo ${
                        clasificarIndice(indice) === 'Peso normal' ? 'tinta-ok' : 'tinta-aviso'
                      }`}
                    >
                      {clasificarIndice(indice)}
                    </span>
                  </span>
                </div>
              </div>
            )}
          </>
        )}

        {paso === 2 && (
          <>
            <GrupoDeOpciones
              titulo="¿Qué tan activo es en su día a día?"
              opciones={NIVELES_ACTIVIDAD}
              valor={formulario.nivel_actividad}
              alElegir={(valor) => elegir('nivel_actividad', valor)}
            />
            <GrupoDeOpciones
              titulo="¿Qué desea lograr?"
              opciones={OBJETIVOS}
              valor={formulario.objetivo}
              alElegir={(valor) => elegir('objetivo', valor)}
            />
          </>
        )}

        {paso === 3 && (
          <>
            <GrupoDeOpciones
              titulo="¿Cuánta experiencia tiene entrenando?"
              opciones={NIVELES_EXPERIENCIA}
              valor={formulario.nivel_experiencia}
              alElegir={(valor) => elegir('nivel_experiencia', valor)}
            />

            <div className="pila-3">
              <span className="lista__titulo">Días que puede entrenar por semana</span>
              <div className="opciones-fila">
                {[1, 2, 3, 4, 5, 6, 7].map((dias) => (
                  <button
                    key={dias}
                    type="button"
                    className={`opcion-boton mono${
                      Number(formulario.dias_entrenamiento_semana) === dias
                        ? ' opcion-boton--seleccionada'
                        : ''
                    }`}
                    onClick={() => elegir('dias_entrenamiento_semana', String(dias))}
                    aria-pressed={Number(formulario.dias_entrenamiento_semana) === dias}
                  >
                    {dias}
                  </button>
                ))}
              </div>
              <p className="campo__ayuda">Su rutina tendrá exactamente esta cantidad de sesiones.</p>
            </div>

            <div className="pila-3">
              <span className="rotulo">Resumen de lo que va a guardar</span>
              <div className="lista">
                <FilaResumen nombre="Peso" valor={`${formulario.peso_kg} kg`} />
                <FilaResumen nombre="Estatura" valor={`${formulario.estatura_cm} cm`} />
                <FilaResumen nombre="Edad" valor={`${formulario.edad} años`} />
                <FilaResumen nombre="Sexo" valor={etiquetaDe(SEXOS, formulario.sexo)} />
                <FilaResumen
                  nombre="Actividad"
                  valor={etiquetaDe(NIVELES_ACTIVIDAD, formulario.nivel_actividad)}
                />
                <FilaResumen nombre="Objetivo" valor={etiquetaDe(OBJETIVOS, formulario.objetivo)} />
                <FilaResumen
                  nombre="Experiencia"
                  valor={etiquetaDe(NIVELES_EXPERIENCIA, formulario.nivel_experiencia)}
                />
                <FilaResumen
                  nombre="Días por semana"
                  valor={formulario.dias_entrenamiento_semana}
                />
                <FilaResumen nombre="Índice de masa corporal" valor={indice ?? '—'} />
              </div>
            </div>
          </>
        )}

        {paso < PASOS.length ? (
          <button type="button" className="boton boton--principal" onClick={avanzar}>
            Continuar
          </button>
        ) : (
          <button type="submit" className="boton boton--principal" disabled={enviando}>
            {enviando ? 'Guardando…' : 'Guardar mis medidas'}
          </button>
        )}
      </form>

      <p className="nota-al-pie centrado">Sus medidas son privadas: nadie más las consulta.</p>
    </div>
  )
}

/** Un grupo de opciones excluyentes, como filas grandes con su explicación. */
function GrupoDeOpciones({ titulo, opciones, valor, alElegir }) {
  return (
    <div className="pila-3">
      <span className="lista__titulo">{titulo}</span>
      <div className="lista">
        {opciones.map((opcion) => (
          <button
            key={opcion.valor}
            type="button"
            className={`lista__fila${valor === opcion.valor ? ' lista__fila--seleccionada' : ''}`}
            onClick={() => alElegir(opcion.valor)}
            aria-pressed={valor === opcion.valor}
          >
            <span className="pila-2 crece">
              <span className="lista__titulo">{opcion.etiqueta}</span>
              {opcion.detalle && <span className="lista__detalle">{opcion.detalle}</span>}
            </span>
            {valor === opcion.valor && (
              <Icono nombre="tick-02" tamano={18} className="tinta-acento" />
            )}
          </button>
        ))}
      </div>
    </div>
  )
}

function FilaResumen({ nombre, valor }) {
  return (
    <div className="lista__fila">
      <span className="lista__etiqueta crece">{nombre}</span>
      <span className="lista__valor">{valor}</span>
    </div>
  )
}
