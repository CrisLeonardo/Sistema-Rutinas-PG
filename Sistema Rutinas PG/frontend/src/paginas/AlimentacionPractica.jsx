import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioAlimentacion as api, servicioCatalogos } from '../servicios/api.js'
import Pildoras from '../componentes/Pildoras.jsx'
import Hoja from '../componentes/Hoja.jsx'
import RespuestaAccion from '../componentes/RespuestaAccion.jsx'
import CambioComidaGuardado from '../componentes/CambioComidaGuardado.jsx'
import { compararComidas } from '../interaccion/respuestas.mjs'
import { PESTANAS_COMER } from '../datos/secciones.js'
import { quetzales } from '../utilidades/formatos.js'
import '../estilos/alimentacion.css'

const TITULOS = { semana: 'Una semana para comer bien', recetas: 'Ideas para su cocina', preferencias: 'Su alimentación, sus límites' }
const costo = valor => valor == null ? 'Precio incompleto' : quetzales(valor)

export default function AlimentacionPractica({ vista }) {
  const { token } = useSesion()
  const [datos, setDatos] = useState(null)
  const [alimentos, setAlimentos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [ocupado, setOcupado] = useState(false)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [dia, setDia] = useState(1)
  const [cambio, setCambio] = useState(null)
  const [consulta, setConsulta] = useState('')
  const [compras, setCompras] = useState(false)
  const [recibo, setRecibo] = useState(null)
  const disparadorCambio = useRef(null)
  const cabecera = useRef(null)
  const restaurarFoco = useRef(false)
  const cerrarCambio = useCallback(() => {
    restaurarFoco.current = true
    setCambio(null)
  }, [])
  useEffect(() => {
    // Después de desmontar Hoja y de volver a habilitar el botón, también si
    // el cierre procede de una respuesta de red y no de una tecla.
    if (!cambio && !ocupado && restaurarFoco.current) {
      restaurarFoco.current = false
      if (disparadorCambio.current?.isConnected) disparadorCambio.current.focus()
      else cabecera.current?.focus()
    }
  }, [cambio, ocupado, recibo])

  const cargar = useCallback(async () => {
    setCargando(true)
    setError('')
    try {
      if (vista === 'preferencias') {
        const [p, a] = await Promise.all([api.preferencias(token), servicioCatalogos.listarAlimentos(token)])
        setDatos(p); setAlimentos(a)
      } else setDatos(await api[vista](token))
    } catch (fallo) {
      setDatos(null)
      if (vista !== 'semana' || fallo.codigo !== 404) setError(fallo.message)
    } finally { setCargando(false) }
  }, [token, vista])
  useEffect(() => { cargar() }, [cargar])

  async function preparar() {
    setOcupado(true); setError(''); setMensaje('')
    try { setDatos(await api.preparar(token)); setRecibo(null); setDia(1); setMensaje('Semana preparada. Las compras suman sus siete días.') }
    catch (fallo) { setError(fallo.message); if ([403, 409].includes(fallo.codigo)) setDatos(null) }
    finally { setOcupado(false) }
  }
  async function verAlternativas(tiempo, disparador) {
    disparadorCambio.current = disparador
    setOcupado(true); setError(''); setMensaje('')
    try { setCambio({ ...(await api.alternativas(dia, tiempo, token)), dia, tiempo }) }
    catch (fallo) { setError(fallo.message); if ([403, 409].includes(fallo.codigo)) { setDatos(null); setRecibo(null) } }
    finally { setOcupado(false) }
  }
  async function elegir(receta) {
    setOcupado(true); setError(''); setMensaje('')
    try {
      const nuevaSemana = await api.cambiar({ dia: cambio.dia, tiempo: cambio.tiempo, receta_id: receta.receta_id, revision: cambio.revision }, token)
      const antes = datos.dias[cambio.dia - 1].tiempos[cambio.tiempo]
      const despues = nuevaSemana.dias[cambio.dia - 1].tiempos[cambio.tiempo]
      setRecibo({ ...compararComidas(antes, despues, cambio.dia, antes.nombre), costoSemanaAntes: datos.compras.costo_quetzales, costoSemanaDespues: nuevaSemana.compras.costo_quetzales })
      setDatos(nuevaSemana)
      cerrarCambio(); setMensaje('Comida cambiada. Porciones, aportes y compras actualizados.')
    } catch (fallo) {
      setError(fallo.message)
      if ([403, 409].includes(fallo.codigo)) { setCambio(null); setDatos(null); setRecibo(null) }
    } finally { setOcupado(false) }
  }
  async function guardar(evento) {
    evento.preventDefault(); setOcupado(true); setError(''); setMensaje('')
    try { await api.guardarPreferencias(datos.preferencias, token); setMensaje('Restricciones guardadas. Prepare otra semana para aplicarlas.') }
    catch (fallo) { setError(fallo.message) }
    finally { setOcupado(false) }
  }
  const actualizar = (clave, valor) => setDatos(d => ({ ...d, preferencias: { ...d.preferencias, [clave]: valor } }))
  const alternar = (clave, valor) => actualizar(clave, datos.preferencias[clave].includes(valor)
    ? datos.preferencias[clave].filter(v => v !== valor) : [...datos.preferencias[clave], valor])
  const actual = datos?.dias?.find(d => d.dia === dia)
  const filtradas = datos?.recetas?.filter(r => r.receta.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().includes(consulta.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase())) ?? []

  return <div className="pila alimentacion">
    <header className="pila-2"><p className="apoyo">ALIMENTACIÓN PRÁCTICA</p><h1 className="titulo-pantalla" ref={cabecera} tabIndex={-1}>{TITULOS[vista]}</h1>
      <p className="apoyo">Comidas sencillas, cantidades claras y una compra para siete días.</p></header>
    <Pildoras etiquetaGrupo="Secciones de alimentación" opciones={PESTANAS_COMER} />
    {error && <div className="tarjeta" role="alert"><p>{error}</p><button className="boton-texto" onClick={cargar} disabled={ocupado}>Volver a consultar</button></div>}
    {mensaje ? <RespuestaAccion mensaje={mensaje} /> : <p role="status" className="solo-lectores" />}
    {cargando ? <p role="status">Cargando…</p> : <>
      {vista === 'preferencias' && datos && <form onSubmit={guardar} className="pila" aria-busy={ocupado}>
        <p className="apoyo">{datos.nota}</p>
        <fieldset disabled={ocupado} className="alimentacion__grupo"><legend>Preferencia de alimentación</legend>
          <label className="alimentacion__campo">Cómo prefiere comer<select value={datos.preferencias.patron} onChange={e => actualizar('patron', e.target.value)}>
            <option value="omnivoro">Incluyo alimentos de origen animal</option><option value="vegetariano">Vegetariana: sin carnes ni pescado</option><option value="vegano">Vegana: sin alimentos de origen animal</option>
          </select></label>
          <p className="nota-al-pie">Esta preferencia se guarda por separado de las alergias.</p>
        </fieldset>
        {[['alergias', 'Alergias declaradas', datos.alergenos], ['intolerancias', 'Intolerancias y exclusión de gluten', datos.intolerancias]].map(([clave, titulo, opciones]) => <fieldset key={clave} disabled={ocupado} className="alimentacion__grupo"><legend>{titulo}</legend>
          <div className="alimentacion__casillas">{Object.entries(opciones).map(([valor, texto]) => <label key={valor}><input type="checkbox" checked={datos.preferencias[clave].includes(valor)} onChange={() => alternar(clave, valor)} />{texto}</label>)}</div>
        </fieldset>)}
        <fieldset disabled={ocupado} className="alimentacion__grupo"><legend>Alimentos que prefiere evitar</legend>
          <p className="nota-al-pie">Se excluyen por su identificador del catálogo. Una alergia debe declararse arriba.</p>
          <details><summary>Elegir alimentos</summary><div className="alimentacion__casillas">{alimentos.map(a => <label key={a.id}><input type="checkbox" checked={datos.preferencias.alimentos_excluidos.includes(a.id)} onChange={() => alternar('alimentos_excluidos', a.id)} />{a.nombre}</label>)}</div></details>
        </fieldset>
        <label className="alimentacion__otra"><input type="checkbox" checked={datos.preferencias.otra_restriccion} disabled={ocupado} onChange={e => actualizar('otra_restriccion', e.target.checked)} />Tengo otra alergia o restricción que no aparece en la lista</label>
        {datos.preferencias.otra_restriccion && <p className="apoyo">La propuesta quedará detenida para solicitar valoración profesional.</p>}
        <button className="boton boton--principal" disabled={ocupado}>{ocupado ? 'Guardando…' : 'Guardar restricciones'}</button>
        <Link className="boton-texto" to="/comer/semana">Ir a mi semana</Link>
      </form>}
      {vista === 'recetas' && datos && <>
        <p className="apoyo">{datos.nota}</p>
        <label className="alimentacion__campo">Buscar entre {datos.recetas.length} recetas compatibles<input type="search" value={consulta} onChange={e => setConsulta(e.target.value)} placeholder="Por ejemplo: frijoles" /></label>
        {!filtradas.length && <p>No hay recetas que coincidan con la búsqueda y sus restricciones.</p>}
        <div className="alimentacion__recetas">{filtradas.map(r => <Comida key={r.receta_id} comida={r} referencia />)}</div>
        <Fuentes fuentes={datos.fuentes} />
      </>}
      {vista === 'semana' && <>
        <div className="tarjeta pila-2"><h2 className="titulo-tarjeta">Primero, lo que necesita evitar</h2><p className="apoyo">Revise alergias, intolerancias y preferencias antes de preparar la semana.</p><Link className="boton-texto" to="/comer/preferencias">Revisar mis restricciones</Link></div>
        <div className="alimentacion__acciones no-imprimir"><button className="boton boton--principal" disabled={ocupado} onClick={preparar}>{ocupado ? 'Calculando…' : datos ? 'Recalcular semana' : 'Preparar mi semana'}</button><Link className="boton-texto" to="/comer/plan">Ver mi plan</Link></div>
        {datos && <>
          {recibo && <CambioComidaGuardado cambio={recibo} alCerrar={() => { restaurarFoco.current = true; setRecibo(null) }} />}
          <p className="nota-al-pie">{datos.nota} El ajuste del piloto admite hasta {datos.tolerancia_porcentaje} % de diferencia en energía y cada macronutriente; requiere revisión profesional.</p>
          <div className="alimentacion__resumen"><strong>{datos.recetas_distintas} recetas distintas</strong><span>{costo(datos.compras.costo_quetzales)} / semana estimada</span></div>
          <div className="alimentacion__dias no-imprimir" role="group" aria-label="Día de la semana">{datos.dias.map(d => <button key={d.dia} className="boton" aria-pressed={dia === d.dia && !compras} onClick={() => { setDia(d.dia); setCompras(false) }} disabled={ocupado}>Día {d.dia}</button>)}</div>
          <div className="alimentacion__acciones no-imprimir"><button className="boton boton--secundario" onClick={() => setCompras(!compras)} aria-pressed={compras}>{compras ? 'Volver a las comidas' : 'Ver compras de los siete días'}</button><button className="boton-texto" onClick={() => window.print()}>Imprimir esta vista</button></div>
          {compras ? <div className="pila"><h2 className="titulo-tarjeta">Compras para esta semana</h2><p className="apoyo">{datos.compras.nota}</p><div className="lista">{datos.compras.renglones.map(r => <div className="lista__fila" key={r.alimento_id}><div className="pila-2 crece"><strong>{r.nombre}</strong><span className="lista__detalle">{r.estado} · {r.gramos_semana} g</span><span className="nota-al-pie">{r.precio_fuente}</span></div><span>{costo(r.costo_quetzales)}</span></div>)}</div><p>Total estimado: <strong>{costo(datos.compras.costo_quetzales)}</strong></p></div>
          : actual && <section className="pila" aria-label={`Comidas del día ${dia}`}><h2 className="titulo-tarjeta">Día {dia}</h2><Aportes datos={actual} />{actual.tiempos.map((t, i) => <Comida key={`${dia}-${i}`} comida={t} ocupado={ocupado} alCambiar={evento => verAlternativas(i, evento.currentTarget)} />)}</section>}
          <Fuentes fuentes={datos.fuentes} />
        </>}
      </>}
    </>}
    {cambio && <Hoja titulo="Cambiar esta comida" descripcion="Cantidades recalculadas. Cada alternativa conserva los aportes de esta comida y del día dentro del margen del piloto." alCerrar={cerrarCambio}>
      {error && <div role="alert" className="aviso aviso--peligro">{error} La comida anterior se conserva. Puede volver a elegir sin perder la semana.</div>}
      {!cambio.opciones.length ? <p>No hay otra receta compatible con estas cantidades y restricciones. Conserve la comida actual; no quite una alergia para obtener alternativas.</p> : <div className="pila">{cambio.opciones.map(r => <div key={r.receta_id} className="pila-2"><Comida comida={r} /><button className="boton boton--principal" disabled={ocupado} onClick={() => elegir(r)}>Elegir {r.receta}</button></div>)}</div>}
    </Hoja>}
  </div>
}

function Aportes({ datos }) {
  return <p className="alimentacion__aportes"><span>{Math.round(datos.energia_kcal)} kcal</span><span>{datos.proteina_g} g proteína</span><span>{datos.carbohidrato_g} g carbohidratos</span><span>{datos.grasa_g} g grasa</span></p>
}

function Comida({ comida: t, alCambiar, ocupado, referencia }) {
  return <article className="tarjeta pila-2">
    <div className="alimentacion__resumen"><span className="apoyo">{referencia ? `${t.rendimiento_porciones} porción de referencia` : t.nombre}</span><span className="apoyo">{t.minutos} min estimados</span></div>
    <h3 className="titulo-tarjeta">{t.receta}</h3><Aportes datos={t} />
    <p className="apoyo">{costo(t.costo_quetzales)} · receta pendiente de revisión</p>
    <details><summary>Ingredientes y preparación</summary><ul className="alimentacion__ingredientes">{t.porciones.map(p => <li key={p.alimento_id}><strong>{p.nombre}: {p.gramos} g</strong><span>{p.estado}{p.cantidad_en_medida_casera ? ` · ≈ ${p.cantidad_en_medida_casera}` : ''}</span></li>)}</ul>
      <ol className="alimentacion__pasos">{t.pasos.map(p => <li key={p}>{p}</li>)}</ol><p className="nota-al-pie">Pese en el estado indicado. Las medidas caseras son aproximadas. Agua de cocción sin aporte; cualquier otro ingrediente cambia el cálculo. El tiempo parte de los ingredientes ya cocidos cuando así se indica.</p>
    </details>
    {alCambiar && <button className="boton-texto no-imprimir" disabled={ocupado} onClick={alCambiar}>Cambiar esta comida</button>}
  </article>
}

function Fuentes({ fuentes }) {
  return <details className="nota-al-pie"><summary>Fuentes y alcance del piloto</summary><p>Recetas y redacción originales de Senda. Composición del catálogo provisional: pendiente de contrastar con registros de alimentos y rendimiento de cocina. No hay precios de campo ni fotografías verificadas.</p><ul>{fuentes?.map(f => <li key={f.url}><a href={f.url} target="_blank" rel="noreferrer">{f.titulo}</a></li>)}</ul></details>
}
