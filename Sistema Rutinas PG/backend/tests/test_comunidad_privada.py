"""Recorridos, privacidad, límites, metas e idempotencia del piloto privado."""
from datetime import datetime, timedelta
import hashlib
import pytest
from sqlalchemy import select
from app.modelos.comunidad import InvitacionPrivada, SemanaPrivada, MiembroPrivado
from app.modelos.entrenamiento import SesionRealizada, SerieRealizada
from app.modelos.usuario import Usuario
from app.servicios import comunidad, plan
from tests.conftest import encabezado
from tests.test_bitacora_entrenamiento import PERFIL

RUTA = "/api/v1/comunidad"

@pytest.fixture(autouse=True)
def piloto_aislado(monkeypatch):
    from app.nucleo.configuracion import configuracion
    monkeypatch.setattr(configuracion, "comunidad_habilitada", True)

@pytest.fixture
def grupo(cliente, token_usuario):
    r = cliente.post(RUTA+'/grupos', headers=encabezado(token_usuario),
        json=dict(nombre="Camino compartido", alias="Sol", consentimiento=True))
    assert r.status_code == 201, r.text
    return r.json()

def invitar(cliente, token, gid):
    r = cliente.post(f'{RUTA}/grupos/{gid}/invitaciones', headers=encabezado(token))
    assert r.status_code == 200, r.text
    return r.json()['codigo']

def aceptar(cliente, token, codigo, **extra):
    return cliente.post(RUTA+'/invitaciones/responder', headers=encabezado(token),
        json=dict(codigo=codigo, aceptar=True, alias="Luna", consentimiento=True, **extra))

def entrar(cliente, token_usuario, token_segundo_usuario, grupo):
    r = aceptar(cliente, token_segundo_usuario, invitar(cliente, token_usuario, grupo['id']))
    assert r.status_code == 200, r.text
    return r.json()

def test_optin_y_campos_desconocidos(cliente, token_usuario):
    for cuerpo in [dict(nombre="Uno", alias="Sol", consentimiento=False),
                   dict(nombre="Uno", alias="Sol", consentimiento=True, puntos=100)]:
        assert cliente.post(RUTA+'/grupos', headers=encabezado(token_usuario), json=cuerpo).status_code == 422
    assert cliente.get(RUTA+'/grupos').status_code == 401

def test_privacidad_e_aislamiento(cliente, token_usuario, token_segundo_usuario, grupo):
    h = encabezado(token_segundo_usuario); gid=grupo['id']
    assert cliente.get(RUTA+'/grupos', headers=h).json() == []
    assert cliente.get(f'{RUTA}/grupos/{gid}', headers=h).status_code == 404
    datos = entrar(cliente, token_usuario, token_segundo_usuario, grupo)
    assert set(datos) == {'id','nombre','soy_propietario','semana','objetivo_colectivo','puntos_colectivos','miembros'}
    assert all(set(m) == {'id','alias','soy_yo','puntos','estado'} for m in datos['miembros'])
    for privado in ['correo','usuario_id','peso_kg','meta','sesiones','calorias','lesiones']:
        assert privado not in str(datos)
    assert cliente.post(f'{RUTA}/grupos/{gid}/invitaciones', headers=h).status_code == 404
    assert cliente.get(f'{RUTA}/grupos/{gid}/denuncias', headers=h).status_code == 404

@pytest.mark.parametrize('accion', ['usar','rechazar','revocar','vencer'])
def test_invitacion_uso_unico_hash_y_vencimiento(cliente, fabrica_sesiones, token_usuario, token_segundo_usuario, grupo, accion):
    codigo = invitar(cliente, token_usuario, grupo['id'])
    with fabrica_sesiones() as s:
        i=s.get(InvitacionPrivada, hashlib.sha256(codigo.encode()).hexdigest())
        assert i is not None and i.id != codigo
        if accion == 'vencer': i.vence=comunidad.ahora()-timedelta(seconds=1); s.commit()
    if accion == 'usar': assert aceptar(cliente, token_segundo_usuario, codigo).status_code == 200
    if accion == 'rechazar':
        assert cliente.post(RUTA+'/invitaciones/responder', headers=encabezado(token_segundo_usuario), json=dict(codigo=codigo, aceptar=False)).status_code == 200
    if accion == 'revocar':
        assert cliente.delete(f"{RUTA}/grupos/{grupo['id']}/invitaciones",headers=encabezado(token_usuario)).status_code == 204
    assert aceptar(cliente, token_segundo_usuario, codigo).status_code == 404

def test_limites_de_grupos_e_invitaciones(cliente, token_usuario, grupo):
    for n in range(10): invitar(cliente, token_usuario, grupo['id'])
    assert cliente.post(f"{RUTA}/grupos/{grupo['id']}/invitaciones", headers=encabezado(token_usuario)).status_code == 409
    for n in range(2):
        assert cliente.post(RUTA+'/grupos', headers=encabezado(token_usuario), json=dict(nombre=f'Grupo {n}',alias='Sol',consentimiento=True)).status_code == 201
    assert cliente.post(RUTA+'/grupos', headers=encabezado(token_usuario), json=dict(nombre='Cuarto',alias='Sol',consentimiento=True)).status_code == 409

def test_bloqueo_bilateral_y_denuncias(cliente, token_usuario, token_segundo_usuario, grupo):
    g=entrar(cliente,token_usuario,token_segundo_usuario,grupo); gid=g['id']
    sol=next(m['id'] for m in g['miembros'] if not m['soy_yo'])
    luna=next(m['id'] for m in g['miembros'] if m['soy_yo'])
    h=encabezado(token_segundo_usuario); ho=encabezado(token_usuario)
    assert cliente.post(f'{RUTA}/grupos/{gid}/denuncias',headers=h,json=dict(miembro_id=sol,motivo='acoso')).status_code == 204
    denuncias=cliente.get(f'{RUTA}/grupos/{gid}/denuncias',headers=ho).json()
    assert set(denuncias[0]) == {'id','miembro_id','motivo','resuelta'}
    assert cliente.post(f"{RUTA}/grupos/{gid}/denuncias/{denuncias[0]['id']}/resolver",headers=ho).status_code == 204
    assert cliente.post(f'{RUTA}/grupos/{gid}/bloqueos/{sol}',headers=h).status_code == 204
    assert cliente.get(f'{RUTA}/grupos/{gid}',headers=h).json()['miembros'] == [dict(id=luna,alias='Luna',soy_yo=True,puntos=None,estado='sin_inscribir')]
    assert len(cliente.get(f'{RUTA}/grupos/{gid}',headers=ho).json()['miembros']) == 1

def test_expulsion_salida_y_cierre(cliente, token_usuario, token_segundo_usuario, grupo):
    g=entrar(cliente,token_usuario,token_segundo_usuario,grupo); gid=g['id']
    mid=next(m['id'] for m in g['miembros'] if m['soy_yo'])
    assert cliente.post(f'{RUTA}/grupos/{gid}/expulsiones/{mid}',headers=encabezado(token_segundo_usuario)).status_code == 404
    assert cliente.post(f'{RUTA}/grupos/{gid}/expulsiones/{mid}',headers=encabezado(token_usuario)).status_code == 204
    assert cliente.get(f'{RUTA}/grupos/{gid}',headers=encabezado(token_segundo_usuario)).status_code == 404
    assert aceptar(cliente,token_segundo_usuario,invitar(cliente,token_usuario,gid)).status_code == 409
    assert cliente.delete(f'{RUTA}/grupos/{gid}/membresia',headers=encabezado(token_usuario)).status_code == 204
    assert cliente.get(RUTA+'/grupos',headers=encabezado(token_usuario)).json() == []

@pytest.fixture
def participante(cliente, fabrica_sesiones, monkeypatch, token_usuario, grupo):
    monkeypatch.setattr(plan, 'obtener_motor', lambda: None)
    h=encabezado(token_usuario)
    assert cliente.post('/api/v1/perfil-biometrico',headers=h,json={**PERFIL,'dias_entrenamiento_semana':3}).status_code == 201
    assert cliente.post('/api/v1/plan-nutricional',headers=h).status_code == 201
    assert cliente.post(f"{RUTA}/grupos/{grupo['id']}/participar",headers=h,json=dict(meta=2,consentimiento=True)).status_code == 200
    return grupo['id'],h

def test_meta_fija_y_pausa_sin_motivo_publico(cliente, participante):
    gid,h=participante
    for meta in [2,3]:
        assert cliente.post(f'{RUTA}/grupos/{gid}/participar',headers=h,json=dict(meta=meta,consentimiento=True)).status_code == 409
    assert cliente.post(f'{RUTA}/grupos/{gid}/pausar',headers=h).status_code == 204
    g=cliente.get(f'{RUTA}/grupos/{gid}',headers=h).json()
    assert g['miembros'][0]['estado']=='pausa' and g['objetivo_colectivo']==0
    assert cliente.post(f'{RUTA}/grupos/{gid}/participar',headers=h,json=dict(meta=2,consentimiento=True)).status_code == 409

def test_meta_no_supera_plan(cliente, participante):
    gid,h=participante
    # Nueva semana, independiente de la inscripción anterior.
    from unittest.mock import patch
    with patch.object(comunidad,'lunes',return_value=comunidad.lunes()+timedelta(days=7)):
        assert cliente.post(f'{RUTA}/grupos/{gid}/participar',headers=h,json=dict(meta=4,consentimiento=True)).status_code == 409
        assert cliente.post(f'{RUTA}/grupos/{gid}/participar',headers=h,json=dict(meta=3,consentimiento=True)).status_code == 200

def test_api_evento_idempotente_sobrevive_regeneracion(cliente, fabrica_sesiones, participante):
    gid,h=participante
    rutina=cliente.get('/api/v1/rutina',headers=h).json()
    sesion=rutina['sesiones'][0]
    # Mantiene el caso reproducible también cuando la suite se ejecuta en domingo.
    with fabrica_sesiones() as s:
        from app.modelos.plan import SesionEntrenamiento
        s.get(SesionEntrenamiento,sesion['id']).dia=comunidad.hoy().weekday()+1
        semana=s.scalar(select(SemanaPrivada))
        semana.sesiones=[{**x,'dia':comunidad.hoy().weekday()+1} if x['id']==sesion['id'] else x for x in semana.sesiones]
        s.commit()
    cuerpo=dict(sesion_id=sesion['id'],fecha=str(comunidad.hoy()),series=[dict(
        ejercicio_id=sesion['ejercicios'][0]['ejercicio_id'],numero_serie=1,repeticiones=8)])
    for _ in range(2):
        r=cliente.post('/api/v1/entrenamiento/sesiones',headers=h,json=cuerpo)
        assert r.status_code==201,r.text
    assert cliente.get(f'{RUTA}/grupos/{gid}',headers=h).json()['miembros'][0]['puntos']==50
    # Los eventos conservan el aporte aun si cambia el plan prescrito.
    assert cliente.post('/api/v1/plan-nutricional',headers=h).status_code==201
    assert cliente.get(f'{RUTA}/grupos/{gid}',headers=h).json()['miembros'][0]['puntos']==50

@pytest.mark.parametrize('caso,esperado', [('duplicado',50),('dos_dias',100),('exceso',100),('anterior',0),('retroactivo',0),('fuera_plan',0),('descanso',0),('vacia',0),('otra_cuenta',0)])
def test_puntos_solo_fechas_validas(cliente, fabrica_sesiones, participante, monkeypatch, caso, esperado):
    gid,h=participante
    # Reloj de ensayo: miércoles. Lunes y miércoles son días de la rutina fijada.
    with fabrica_sesiones() as s:
        semana=s.scalar(select(SemanaPrivada)); m=s.get(MiembroPrivado,semana.miembro_id)
        semana.inicio=datetime(2026,10,26,6)
        semana.lunes=datetime(2026,10,26).date()
        s.commit()
        monkeypatch.setattr(comunidad,'hoy',lambda:datetime(2026,10,30).date())
        monkeypatch.setattr(comunidad,'lunes',lambda:datetime(2026,10,26).date())
        cantidad=2 if caso in ('duplicado','dos_dias') else 3 if caso=='exceso' else 1
        for n in range(cantidad):
            fecha=datetime(2026,10,26)+timedelta(days=(2*n if caso in ('dos_dias','exceso') else 0))
            prescrita=semana.sesiones[min(n,len(semana.sesiones)-1) if caso in ('dos_dias','exceso') else 0]
            if caso=='descanso': fecha+=timedelta(days=1)
            registro=fecha+timedelta(hours=12)
            if caso=='anterior': registro=semana.inicio-timedelta(seconds=1)
            if caso=='retroactivo': registro+=timedelta(days=1)
            uid=m.usuario_id
            if caso=='otra_cuenta':
                otro=Usuario(correo='ficticio@example.com',nombre='Otra',contrasena_cifrada='hash');s.add(otro);s.flush();uid=otro.id
            realizada=SesionRealizada(usuario_id=uid,fecha=fecha.date(),fecha_registro=registro,
                 sesion_id=None if caso=='fuera_plan' else prescrita['id'])
            realizada.series=[SerieRealizada(ejercicio_id=1,numero_serie=1,repeticiones=0 if caso=='vacia' else 8)]
            s.add(realizada)
            s.flush()
            comunidad.registrar_evento(s, realizada)
            comunidad.registrar_evento(s, realizada)
        s.commit()
    for _ in range(2):
        g=cliente.get(f'{RUTA}/grupos/{gid}',headers=h).json()
        assert g['miembros'][0]['puntos']==esperado
