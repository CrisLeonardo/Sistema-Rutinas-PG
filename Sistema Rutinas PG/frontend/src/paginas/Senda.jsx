/**
 * «La senda»: en qué nivel está el usuario y qué camino lleva recorrido.
 *
 * La bitácora responde «qué levanté» y los reportes «cuánto he cambiado». Falta
 * una pregunta, y es la que sostiene la constancia: «he avanzado». Un historial
 * de sesiones no la contesta, porque cuarenta filas iguales no se leen como
 * avance aunque lo sean.
 *
 * La pantalla se ordena por lo que cuesta responder, de arriba abajo:
 *
 *  1. Dónde estoy       · el anillo del nivel, con su número y su nombre.
 *  2. Qué falta         · los puntos que quedan para el nivel siguiente.
 *  3. Qué he hecho      · racha, sesiones, volumen, marcas.
 *  4. Qué me falta por  · las insignias, con su pista cuando están bloqueadas.
 *     conseguir
 *  5. De dónde vengo    · el camino, del hito más nuevo al más antiguo.
 *  6. Cómo se gana      · la tabla de motivos. Un sistema de puntos cuyas
 *                         reglas no se pueden leer no motiva: desconcierta.
 */

import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import AnilloNivel from '../componentes/AnilloNivel.jsx'
import AvisoDeError from '../componentes/AvisoDeError.jsx'
import Icono from '../componentes/Icono.jsx'
import Pildoras from '../componentes/Pildoras.jsx'
import { PESTANAS_AVANCE } from '../datos/secciones.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioJuego } from '../servicios/api.js'
import { entero, fechaBreve } from '../utilidades/formatos.js'

/** Icono del punto de cada hito según lo que celebre. */
const ICONO_HITO = {
  nivel: 'award-01',
  logro: 'medal-first-place',
  inicio: 'flag-02',
}

export default function Senda() {
  const { token } = useSesion()

  const [estado, setEstado] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    setCargando(true)
    try {
      setEstado(await servicioJuego.consultarEstado(token))
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
        <span className="solo-lectores">Cargando su senda…</span>
      </div>
    )
  }

  if (error) return <AvisoDeError mensaje={error} alReintentar={cargar} />

  return (
    <div className="pila">
      <div className="pila-2">
        <h1 className="titulo-pantalla">Mi senda</h1>
        <p className="apoyo">Su nivel, sus insignias y el camino que lleva recorrido</p>
      </div>

      <Pildoras etiquetaGrupo="Secciones de avance" opciones={PESTANAS_AVANCE} />

      <Cabecera estado={estado} />
      <Cifras estado={estado} />
      <Insignias logros={estado.logros} conseguidas={estado.logros_obtenidos} />
      <Camino hitos={estado.hitos} />
      <Reglas motivos={estado.motivos} />
    </div>
  )
}

function Cabecera({ estado }) {
  const enElTope = estado.nombre_proximo_nivel === null

  return (
    <div className="pila-3">
      <div className="senda-cabecera">
        <AnilloNivel porcentaje={estado.porcentaje} nivel={estado.nivel} tamano={140} />
        <div className="senda-cabecera__texto">
          <span className="senda-cabecera__nivel">
            Nivel {estado.nivel} de {estado.nivel_maximo}
          </span>
          <h2 className="senda-cabecera__nombre">{estado.nombre_nivel}</h2>
          <p className="senda-cabecera__lema">{estado.lema}</p>
          <span className="apoyo mono">{entero(estado.puntos_totales)} puntos en total</span>
        </div>
      </div>

      {enElTope ? (
        <p className="nota-al-pie centrado">
          Llegó al último nivel. A partir de aquí, la senda la marcan las insignias.
        </p>
      ) : (
        <div className="pila-2">
          <div
            className="barra-nivel"
            role="progressbar"
            aria-valuenow={estado.porcentaje}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Avance hacia el nivel ${estado.nombre_proximo_nivel}`}
          >
            <div className="barra-nivel__relleno" style={{ width: `${estado.porcentaje}%` }} />
          </div>
          <p className="apoyo">
            Le faltan{' '}
            <strong className="mono">{entero(estado.puntos_para_el_proximo)}</strong> puntos
            para ser <strong>{estado.nombre_proximo_nivel}</strong>.
          </p>
        </div>
      )}
    </div>
  )
}

function Cifras({ estado }) {
  const columnas = [
    {
      valor: estado.racha_semanas,
      rotulo: estado.racha_semanas === 1 ? 'semana seguida' : 'semanas seguidas',
    },
    { valor: estado.sesiones_totales, rotulo: 'sesiones' },
    { valor: entero(estado.volumen_acumulado_kg), rotulo: 'kg movidos' },
    { valor: estado.marcas_personales, rotulo: 'marcas' },
  ]

  return (
    <div className="cifras">
      {columnas.map((columna) => (
        <div key={columna.rotulo} className="cifras__columna">
          <span className="cifras__valor">{columna.valor}</span>
          <span className="cifras__rotulo">{columna.rotulo}</span>
        </div>
      ))}
    </div>
  )
}

/**
 * Las insignias, agrupadas por categoría y con las conseguidas primero dentro
 * de cada una. Las bloqueadas no se esconden: su pista es lo que le dice al
 * usuario qué hacer a continuación, y esconderlas dejaría la pantalla vacía el
 * primer día.
 */
function Insignias({ logros, conseguidas }) {
  const categorias = []
  logros.forEach((logro) => {
    let grupo = categorias.find((candidato) => candidato.nombre === logro.categoria)
    if (!grupo) {
      grupo = { nombre: logro.categoria, logros: [] }
      categorias.push(grupo)
    }
    grupo.logros.push(logro)
  })

  return (
    <div className="pila-3">
      <div className="fila--entre">
        <span className="rotulo">Insignias</span>
        <span className="apoyo mono">
          {conseguidas} de {logros.length}
        </span>
      </div>

      {categorias.map((categoria) => (
        <div key={categoria.nombre} className="pila-2">
          <span className="apoyo">{categoria.nombre}</span>
          <div className="insignias">
            {[...categoria.logros]
              .sort((uno, otro) => Number(otro.obtenido) - Number(uno.obtenido))
              .map((logro) => (
                <Insignia key={logro.clave} logro={logro} />
              ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function Insignia({ logro }) {
  return (
    <div
      className={`insignia insignia--${logro.obtenido ? 'obtenida' : 'bloqueada'}`}
    >
      <span className="insignia__marca">
        <Icono nombre={logro.obtenido ? 'medal-first-place' : 'lock-password'} tamano={17} />
      </span>
      <span className="insignia__nombre">{logro.nombre}</span>
      <span className="insignia__texto">
        {logro.obtenido ? logro.descripcion : logro.pista}
      </span>
      <span className="insignia__puntos">
        {logro.obtenido ? fechaBreve(logro.fecha) : `+${logro.puntos} puntos`}
      </span>
    </div>
  )
}

function Camino({ hitos }) {
  return (
    <div className="pila-3">
      <span className="rotulo">Su camino</span>
      <div className="camino">
        {hitos.map((hito, indice) => (
          <div
            key={`${hito.tipo}-${hito.titulo}-${indice}`}
            className={`hito hito--${hito.tipo}`}
          >
            <span className="hito__punto">
              <Icono nombre={ICONO_HITO[hito.tipo] ?? 'circle'} tamano={16} />
            </span>
            <span className="hito__texto">
              <span className="hito__titulo">{hito.titulo}</span>
              <span className="hito__detalle">{hito.detalle}</span>
              <span className="hito__fecha">{fechaBreve(hito.fecha)}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

/**
 * Cómo se ganan los puntos.
 *
 * Los dos motivos variables —el volumen y la racha— se anuncian por su techo y
 * el servidor los marca como tales, para que la pantalla escriba «hasta +40» en
 * ellos y «+100» en los de valor fijo. Y el techo se explica, porque es la
 * decisión de fondo del sistema: no premia entrenar más de lo que la rutina
 * prescribe.
 */
function Reglas({ motivos }) {
  return (
    <div className="tarjeta tarjeta--densa">
      <span className="rotulo">Cómo se ganan los puntos</span>
      <div className="lista lista--desnuda">
        {motivos.map((motivo) => (
          <div key={motivo.motivo} className="lista__fila">
            <span className="cuerpo crece">{motivo.motivo}</span>
            <span className="lista__valor mono">
              {motivo.variable ? `hasta +${motivo.puntos}` : `+${motivo.puntos}`}
            </span>
          </div>
        ))}
      </div>
      <p className="nota-al-pie">
        Los puntos de una sesión tienen techo y solo cuenta la primera del día. El
        sistema premia cumplir el programa, no excederlo: entrenar de más no da más
        puntos, y respetar los días de descanso sí los da.
      </p>
      <Link to="/entrenar" className="boton boton--secundario">
        Ir a mi rutina
      </Link>
    </div>
  )
}
