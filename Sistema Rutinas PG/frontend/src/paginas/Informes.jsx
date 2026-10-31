/**
 * Informes: consulta en pantalla, descarga en Excel, CSV y PDF, e impresión.
 *
 * Una sola pantalla sirve a los dos públicos. El deportista la encuentra en su
 * sección «Avance» y solo ve sus informes personales; el administrador la
 * encuentra en su armazón de escritorio y ve los de administración. Qué
 * informes ve cada uno no lo decide esta pantalla sino el servidor, que vuelve
 * a comprobar el rol en cada descarga.
 *
 * La tabla de la pantalla y los tres archivos se arman en el servidor a partir
 * del mismo informe, de modo que la cifra que el usuario ve aquí es la misma
 * que encontrará en el archivo que descargue.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import ArmazonAdmin from '../componentes/ArmazonAdmin.jsx'
import AvisoDeError from '../componentes/AvisoDeError.jsx'
import Icono from '../componentes/Icono.jsx'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioInformes } from '../servicios/api.js'
import { entero, fechaYHora, quetzales } from '../utilidades/formatos.js'

const DESCARGAS = [
  { formato: 'xlsx', etiqueta: 'Excel', icono: 'xls-02' },
  { formato: 'csv', etiqueta: 'CSV', icono: 'csv-02' },
  { formato: 'pdf', etiqueta: 'PDF', icono: 'pdf-02' },
]

const COLUMNAS_NUMERICAS = new Set(['entero', 'decimal', 'porcentaje', 'moneda'])

/**
 * Fecha sin hora, leída en la zona del usuario.
 *
 * `new Date('2026-09-07')` interpreta la cadena como medianoche en UTC, que en
 * Guatemala es todavía el 6 de septiembre: el informe mostraría cada registro
 * un día antes de cuando se hizo.
 */
function fechaCorta(valor) {
  const [anio, mes, dia] = String(valor).slice(0, 10).split('-').map(Number)
  return new Date(anio, mes - 1, dia).toLocaleDateString('es-GT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

/** Texto de una celda según el tipo de su columna. */
function textoDeCelda(valor, columna) {
  if (valor === null || valor === undefined || valor === '') return '—'
  switch (columna.tipo) {
    case 'fecha':
      return fechaCorta(valor)
    case 'entero':
      return entero(valor)
    case 'decimal':
      return Number(valor).toLocaleString('es-GT', {
        minimumFractionDigits: columna.decimales,
        maximumFractionDigits: columna.decimales,
      })
    case 'porcentaje':
      return `${Math.round(valor)} %`
    case 'moneda':
      return quetzales(valor)
    default:
      return String(valor)
  }
}

export default function Informes({ ambito = 'personal' }) {
  const { token } = useSesion()
  const esAdministracion = ambito === 'administracion'

  const [catalogo, setCatalogo] = useState([])
  const [clave, setClave] = useState(null)
  const [informe, setInforme] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [descargando, setDescargando] = useState(null)
  const [aviso, setAviso] = useState(null)
  const cargaVigente = useRef(0)

  const cargarCatalogo = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      const disponibles = (await servicioInformes.listar(token)).filter(
        (entrada) => entrada.ambito === ambito,
      )
      setCatalogo(disponibles)
      setClave((actual) => actual ?? disponibles[0]?.clave ?? null)
      if (disponibles.length === 0) setCargando(false)
    } catch (fallo) {
      setError(fallo.message)
      setCargando(false)
    }
  }, [token, ambito])

  const cargarInforme = useCallback(async () => {
    if (!clave) return
    const carga = ++cargaVigente.current
    setCargando(true)
    setInforme(null)
    setError(null)
    setAviso(null)
    try {
      const resultado = await servicioInformes.consultar(clave, token)
      if (carga === cargaVigente.current) setInforme(resultado)
    } catch (fallo) {
      if (carga === cargaVigente.current) setError(fallo.message)
    } finally {
      if (carga === cargaVigente.current) setCargando(false)
    }
  }, [clave, token])

  useEffect(() => {
    cargarCatalogo()
  }, [cargarCatalogo])

  useEffect(() => {
    cargarInforme()
    return () => { cargaVigente.current++ }
  }, [cargarInforme])

  const descargar = async (formato) => {
    setDescargando(formato)
    setError(null)
    setAviso(null)
    try {
      const nombre = await servicioInformes.descargar(clave, formato, token)
      setAviso(`Se descargó el archivo ${nombre}.`)
    } catch (fallo) {
      setError(fallo.message)
    } finally {
      setDescargando(null)
    }
  }

  const sinFilas = informe && informe.filas.length === 0

  const contenido = (
    <>
      <div className="selector-informes no-imprimir" role="group" aria-label="Informe">
        {catalogo.map((entrada) => (
          <button
            key={entrada.clave}
            type="button"
            aria-pressed={entrada.clave === clave}
            disabled={descargando !== null}
            className={`selector-informes__opcion${
              entrada.clave === clave ? ' selector-informes__opcion--activa' : ''
            }`}
            onClick={() => setClave(entrada.clave)}
          >
            <span className="lista__etiqueta">{entrada.titulo}</span>
            <span className="lista__detalle">{entrada.descripcion}</span>
          </button>
        ))}
      </div>

      <div className="acciones-informe no-imprimir">
        {DESCARGAS.map((descarga) => (
          <button
            key={descarga.formato}
            type="button"
            className="boton boton--secundario boton--compacto"
            onClick={() => descargar(descarga.formato)}
            disabled={!informe || cargando || descargando !== null}
          >
            <Icono nombre={descarga.icono} tamano={17} />
            {descargando === descarga.formato ? 'Preparando…' : descarga.etiqueta}
          </button>
        ))}
        <button
          type="button"
          className="boton boton--secundario boton--compacto"
          onClick={() => window.print()}
          disabled={!informe || cargando}
        >
          <Icono nombre="printer" tamano={17} />
          Imprimir
        </button>
      </div>

      {aviso && (
        <p className="aviso aviso--ok no-imprimir" role="status">
          {aviso}
        </p>
      )}
      {error && <AvisoDeError mensaje={error} alReintentar={clave ? cargarInforme : cargarCatalogo} />}
      {!cargando && !error && !catalogo.length && <p className="aviso" role="status">No hay informes disponibles para esta cuenta.</p>}

      {cargando && !informe ? (
        <div className="pila-3" aria-busy="true">
          <div className="esqueleto esqueleto--tarjeta" />
          <div className="esqueleto esqueleto--fila" />
          <span className="solo-lectores">Preparando el informe…</span>
        </div>
      ) : (
        informe && (
          <article className="informe" aria-busy={cargando}>
            <header className="informe__encabezado">
              <span className="rotulo">Sistema de rutinas y planes nutricionales</span>
              <h2 className="informe__titulo">{informe.titulo}</h2>
              <p className="apoyo">{informe.descripcion}</p>
              <p className="nota-al-pie">
                {informe.titular} · generado el {fechaYHora(informe.generado)}
              </p>
            </header>

            {informe.resumen.length > 0 && (
              <dl className="informe__resumen">
                {informe.resumen.map((indicador) => (
                  <div key={indicador.rotulo} className="informe__indicador">
                    <dt className="cifras__rotulo">{indicador.rotulo}</dt>
                    <dd className="informe__valor">{indicador.valor}</dd>
                  </div>
                ))}
              </dl>
            )}

            {sinFilas ? (
              <p className="aviso aviso--neutro">
                El informe todavía no tiene registros. Aparecerán aquí en cuanto los haya.
              </p>
            ) : (
              <div className="informe__desplazamiento">
                <table className="informe__tabla">
                  <caption className="solo-lectores">{informe.titulo}</caption>
                  <thead>
                    <tr>
                      {informe.columnas.map((columna) => (
                        <th
                          key={columna.clave}
                          scope="col"
                          className={COLUMNAS_NUMERICAS.has(columna.tipo) ? 'numero' : ''}
                        >
                          {columna.titulo}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {informe.filas.map((fila, indice) => (
                      <tr key={indice}>
                        {informe.columnas.map((columna) => (
                          <td
                            key={columna.clave}
                            className={COLUMNAS_NUMERICAS.has(columna.tipo) ? 'numero' : ''}
                          >
                            {textoDeCelda(fila[columna.clave], columna)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {informe.nota && <p className="nota-al-pie informe__nota">{informe.nota}</p>}
          </article>
        )
      )}
    </>
  )

  if (esAdministracion) {
    return (
      <ArmazonAdmin
        titulo="Informes"
        explicacion="Consulte los informes del sistema y descárguelos en Excel, CSV o PDF."
      >
        {contenido}
      </ArmazonAdmin>
    )
  }

  return (
    <div className="pila">
      <div className="pila-2 no-imprimir">
        <h1 className="titulo-pantalla">Mis informes</h1>
        <p className="apoyo">Consulte su información y llévesela en el formato que necesite.</p>
      </div>



      {contenido}
    </div>
  )
}
