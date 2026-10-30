import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { peticion } from '../servicios/api.js'
import '../estilos/comunidad.css'

const base = '/comunidad'
const motivos = { acoso: 'Acoso', alias_inapropiado: 'Alias inapropiado', registro_anomalo: 'Registro anómalo', otro: 'Otro' }

export default function ComunidadPrivada() {
  const { token } = useSesion()
  const [grupos, setGrupos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [ocupado, setOcupado] = useState(false)
  const [error, setError] = useState('')
  const [aviso, setAviso] = useState('')
  const [invitacion, setInvitacion] = useState(null)
  const [denuncias, setDenuncias] = useState({})
  const enviando = useRef(false)
  const cargar = useCallback(async () => {
    setGrupos(await peticion(`${base}/grupos`, { token }))
  }, [token])
  useEffect(() => {
    let vigente = true
    peticion(`${base}/grupos`, { token }).then(g => { if (vigente) setGrupos(g) })
      .catch(e => { if (vigente) setError(e.message) }).finally(() => { if (vigente) setCargando(false) })
    return () => { vigente = false }
  }, [token])

  async function actuar(ruta, datos, mensaje, metodo = 'POST', despues) {
    if (enviando.current) return
    enviando.current = true; setOcupado(true); setError(''); setAviso('')
    try {
      const respuesta = await peticion(`${base}${ruta}`, { token, metodo, datos })
      despues?.(respuesta)
      setAviso(mensaje)
      await cargar()
    } catch (e) { setError(e.message) }
    finally { enviando.current = false; setOcupado(false) }
  }

  function crear(e) {
    e.preventDefault()
    const f = new FormData(e.currentTarget)
    actuar('/grupos', { nombre: f.get('nombre'), alias: f.get('alias'), consentimiento: true }, 'Grupo creado. Puedes preparar una invitación.')
  }
  function responder(e) {
    e.preventDefault()
    const f = new FormData(e.currentTarget)
    const aceptar = e.nativeEvent.submitter?.value === 'aceptar'
    actuar('/invitaciones/responder', { codigo: f.get('codigo').trim(), aceptar,
      alias: f.get('alias'), consentimiento: f.get('reglas') === 'on' }, aceptar ? 'Invitación aceptada.' : 'Invitación rechazada.')
  }

  return <div className="pila-5 comunidad-privada">
    <div className="pila-2"><h1 className="titulo-pantalla">Con amigos</h1><p className="apoyo">Un reto privado de constancia, a tu ritmo.</p><Link to="/avance/senda">Mi senda personal ↗</Link></div>
    <details className="tarjeta comunidad-reglas" open><summary>Antes de participar: reglas y privacidad</summary>
      <p>Participar es voluntario. Usa un alias que no revele datos personales. En el grupo se comparten únicamente el alias, el estado de participación y los puntos del reto. No se publican medidas, correo, lesiones, comidas, cargas ni notas.</p>
      <p>El reto va de lunes a domingo, con horario de Guatemala. Al inscribirte eliges una meta de 2 a 5 sesiones, compatible con tu plan. Una fecha de entrenamiento programada aporta como máximo una vez. Solo cuenta lo registrado ese mismo día y después de inscribirte. Actualiza para consultar los nuevos puntos.</p>
      <p>Recibes hasta 100 puntos por semana: cumplir tu meta da el mismo máximo que cumplir otra meta. Entrenar de más no da ventaja. Las sesiones son autodeclaradas; no verifican actividad real. Sin premios monetarios ni mensajería abierta.</p>
      <p>La meta queda fija durante la semana. Puedes pausar sin publicar el motivo; tu aporte se retira del reto actual y puedes volver a inscribirte la semana siguiente. No entrenes durante el descanso ni ante dolor para obtener puntos.</p>
      <p>Respeta a los demás; puedes bloquear, denunciar y salir. El propietario revisa denuncias y puede retirar miembros. Si el propietario sale, el grupo se cierra. En este piloto no hay reingreso tras salir. Los logros personales se conservan.</p>
      <p className="apoyo">Piloto local pendiente de evaluación con participantes. Los datos sociales se conservan para moderación y continuidad; para solicitar eliminación, utiliza <Link to="/ayuda">Ayuda</Link>. Las invitaciones caducan a las 48 horas.</p>
    </details>
    {error && <p role="alert" className="aviso">{error}</p>}
    <p role="status" aria-live="polite">{aviso || (ocupado ? 'Guardando…' : '')}</p>
    {cargando ? <p role="status">Cargando grupos…</p> : <>
      <button className="boton boton--secundario" disabled={ocupado} onClick={() => actuar('/grupos', null, 'Grupos actualizados.', 'GET')}>Actualizar puntos</button>
      <form className="tarjeta pila-3" onSubmit={crear}><h2 className="titulo-tarjeta">Crear un grupo privado</h2><fieldset disabled={ocupado} className="pila-3">
        <label>Nombre del grupo<input name="nombre" required minLength={3} maxLength={60} autoComplete="off" /></label>
        <label>Tu alias en este grupo<input name="alias" required minLength={2} maxLength={30} autoComplete="off" /></label>
        <label className="comunidad-casilla"><input type="checkbox" required />Acepto las reglas y compartir mi alias y progreso del reto con este grupo.</label>
        <button className="boton boton--principal">Crear grupo</button>
      </fieldset></form>
      <form className="tarjeta pila-3" onSubmit={responder}><h2 className="titulo-tarjeta">Responder una invitación</h2><fieldset disabled={ocupado} className="pila-3">
        <label>Código privado<input name="codigo" required minLength={30} maxLength={100} autoComplete="off" spellCheck="false" /></label>
        <label>Alias para aceptar<input name="alias" maxLength={30} autoComplete="off" /></label>
        <label className="comunidad-casilla"><input name="reglas" type="checkbox" />Acepto las reglas y compartir mi alias y progreso con el grupo al que da acceso este código.</label>
        <p className="apoyo">Usa solo códigos recibidos de alguien de confianza. Cada código admite una respuesta.</p>
        <div className="fila"><button name="respuesta" value="aceptar" className="boton boton--principal">Aceptar</button><button name="respuesta" value="rechazar" className="boton boton--secundario">Rechazar</button></div>
      </fieldset></form>
      {grupos.length === 0 && <p className="apoyo">Aún no perteneces a un grupo privado.</p>}
      {grupos.map(g => <section className="tarjeta pila-4" key={g.id} aria-label={g.nombre}>
        <div><h2 className="titulo-tarjeta">{g.nombre}</h2><p className="apoyo">Semana del {g.semana}. Objetivo colectivo entre participantes visibles: {g.puntos_colectivos}/{g.objetivo_colectivo} puntos.</p></div>
        <ul className="comunidad-miembros">{g.miembros.map(m => <li key={m.id} className="pila-2">
          <p><strong>{m.alias}{m.soy_yo ? ' (tú)' : ''}</strong> · {m.puntos == null ? (m.estado === 'pausa' ? 'En pausa' : 'Sin inscribir esta semana') : `${m.puntos}/100 puntos`}</p>
          {!m.soy_yo && <details><summary>Opciones de {m.alias}</summary><div className="pila-3">
            <button disabled={ocupado} className="boton boton--secundario" onClick={() => actuar(`/grupos/${g.id}/bloqueos/${m.id}`, null, 'Bloqueo aplicado. Dejan de verse mutuamente en los grupos compartidos.')}>Bloquear a {m.alias}</button>
            <form onSubmit={e => { e.preventDefault(); actuar(`/grupos/${g.id}/denuncias`, { miembro_id: m.id, motivo: new FormData(e.currentTarget).get('motivo') }, 'Denuncia registrada para revisión del propietario.') }}>
              <label>Motivo de denuncia<select name="motivo" disabled={ocupado}>{Object.entries(motivos).map(([v,t]) => <option key={v} value={v}>{t}</option>)}</select></label>
              <button className="boton boton--secundario" disabled={ocupado}>Denunciar a {m.alias}</button>
            </form>
            {g.soy_propietario && <button disabled={ocupado} className="boton boton--secundario" onClick={() => actuar(`/grupos/${g.id}/expulsiones/${m.id}`, null, 'Participante retirado del grupo.')}>Retirar a {m.alias}</button>}
          </div></details>}
        </li>)}</ul>
        {g.miembros.find(m => m.soy_yo)?.estado === 'sin_inscribir' && <form onSubmit={e => { e.preventDefault(); actuar(`/grupos/${g.id}/participar`, { meta: Number(new FormData(e.currentTarget).get('meta')), consentimiento: true }, 'Meta fijada para esta semana.') }}><fieldset disabled={ocupado} className="pila-3">
          <label>Meta semanal<select name="meta">{[2,3,4,5].map(n => <option key={n} value={n}>{n} sesiones</option>)}</select></label>
          <p className="apoyo">No puede superar las sesiones con ejercicios de tu plan vigente. No cuenta actividad anterior a la inscripción.</p>
          <label className="comunidad-casilla"><input type="checkbox" required />Acepto compartir mi progreso de este reto semanal.</label>
          <button className="boton boton--principal">Participar esta semana</button>
        </fieldset></form>}
        {g.miembros.find(m => m.soy_yo)?.estado === 'participando' && <button disabled={ocupado} className="boton boton--secundario" onClick={() => actuar(`/grupos/${g.id}/pausar`, null, 'Semana pausada. Puedes volver la próxima semana.')}>Pausar esta semana</button>}
        {g.soy_propietario && <div className="pila-3">
          <button disabled={ocupado} className="boton boton--secundario" onClick={() => actuar(`/grupos/${g.id}/invitaciones`, null, 'Código preparado; entrégalo en privado a una sola persona.', 'POST', i => setInvitacion({ ...i, gid: g.id }))}>Preparar invitación</button>
          {invitacion?.gid === g.id && <div className="pila-2"><label>Código para entregar en privado<input readOnly value={invitacion.codigo} onFocus={e => e.target.select()} /></label><p className="apoyo">Vence: {new Date(invitacion.vence).toLocaleString('es-GT')}.</p><button className="boton-texto" onClick={() => setInvitacion(null)}>Ocultar código</button></div>}
          <button disabled={ocupado} className="boton-texto" onClick={() => actuar(`/grupos/${g.id}/invitaciones`, null, 'Invitaciones revocadas.', 'DELETE', () => setInvitacion(null))}>Revocar todas las invitaciones</button>
          <button disabled={ocupado} className="boton-texto" onClick={() => actuar(`/grupos/${g.id}/denuncias`, null, 'Denuncias consultadas.', 'GET', d => setDenuncias(prev => ({ ...prev, [g.id]: d })))}>Revisar denuncias</button>
          {denuncias[g.id]?.map(d => <div key={d.id}><p>{motivos[d.motivo]} · {g.miembros.find(m => m.id === d.miembro_id)?.alias || 'Miembro retirado'} · {d.resuelta ? 'Resuelta' : 'Abierta'}</p>{!d.resuelta && <button disabled={ocupado} className="boton-texto" onClick={() => actuar(`/grupos/${g.id}/denuncias/${d.id}/resolver`, null, 'Denuncia resuelta.', 'POST', () => setDenuncias({}))}>Marcar resuelta</button>}</div>)}
        </div>}
        <details><summary>{g.soy_propietario ? 'Cerrar grupo y salir' : 'Salir del grupo'}</summary><form onSubmit={e => { e.preventDefault(); actuar(`/grupos/${g.id}/membresia`, null, g.soy_propietario ? 'Grupo cerrado.' : 'Has salido del grupo.', 'DELETE', () => { setInvitacion(null); setDenuncias({}) }) }} className="pila-3">
          <p>{g.soy_propietario ? 'Se cerrará el grupo para todos sus integrantes.' : 'Dejarás de compartir tu alias y progreso en este grupo.'} El piloto no permite reingresar después. Tu senda personal se conserva.</p>
          <label className="comunidad-casilla"><input type="checkbox" required disabled={ocupado} />Confirmo que deseo salir.</label>
          <button className="boton boton--secundario" disabled={ocupado}>{g.soy_propietario ? 'Cerrar y salir' : 'Salir'}</button>
        </form></details>
      </section>)}
    </>}
  </div>
}
