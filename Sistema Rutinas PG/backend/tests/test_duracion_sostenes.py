from sqlalchemy import select, text
from alembic import command
import pytest
from app.modelos.catalogo import Ejercicio
from app.modelos.entrenamiento import SerieRealizada, SesionRealizada
from app.modelos.usuario import Usuario
from app.nucleo.migraciones import actualizar, configurar, diferencias
from app.servicios import plan
from tests.conftest import encabezado
from tests.test_bitacora_entrenamiento import PERFIL
from tests.test_migraciones import conexion_migraciones  # noqa: F401

@pytest.fixture
def plancha(cliente,fabrica_sesiones,token_usuario,monkeypatch):
    monkeypatch.setattr(plan,'obtener_motor',lambda:None)
    h=encabezado(token_usuario)
    cliente.post('/api/v1/perfil-biometrico',headers=h,json={**PERFIL,'dias_entrenamiento_semana':6})
    assert cliente.post('/api/v1/plan-nutricional',headers=h).status_code==201
    rutina=cliente.get('/api/v1/rutina',headers=h).json()
    x=next((s,e) for s in rutina['sesiones'] for e in s['ejercicios'] if e['nombre']=='Plancha frontal')
    return h,x[0]['id'],x[1]

def test_prescripcion_registro_e_historial(cliente,plancha):
    h,sid,e=plancha
    assert (e['duracion_segundos_min'],e['duracion_segundos_max'])==(20,30)
    assert e['repeticiones_min']==e['repeticiones_max']==0
    assert 'segundos' in e['prescripcion'] and 'repeticiones' not in e['prescripcion']
    r=cliente.post('/api/v1/entrenamiento/sesiones',headers=h,json=dict(sesion_id=sid,series=[dict(ejercicio_id=e['ejercicio_id'],numero_serie=1,duracion_segundos=25)]))
    assert r.status_code==201,r.text
    assert r.json()['sesion']['duracion_total_segundos']==25
    assert r.json()['sesion']['volumen_kg']==r.json()['sesion']['repeticiones_totales']==0
    abierta=cliente.get(f'/api/v1/entrenamiento/sesiones/{sid}',headers=h).json()
    p=next(x for x in abierta['ejercicios'] if x['nombre']=='Plancha frontal')
    assert p['ultima_vez'][0]['duracion_segundos']==25
    assert p['recomendacion']['decision']=='mantener' and p['recomendacion']['carga_sugerida_kg'] is None
    hist=cliente.get(f"/api/v1/entrenamiento/ejercicios/{e['ejercicio_id']}",headers=h).json()
    assert hist['puntos'][0]['duracion_total_segundos']==25
    assert hist['marca']['carga_maxima_kg'] is None

@pytest.mark.parametrize('datos', [dict(repeticiones=12),dict(duracion_segundos=20,repeticiones=8),dict(duracion_segundos=20,peso_kg=10),dict(duracion_segundos=20,repeticiones_en_reserva=3),dict(duracion_segundos=0),dict(duracion_segundos=3601)])
def test_rechaza_unidades_ambiguas(cliente,plancha,datos):
    h,sid,e=plancha
    assert cliente.post('/api/v1/entrenamiento/sesiones',headers=h,json=dict(sesion_id=sid,series=[dict(ejercicio_id=e['ejercicio_id'],numero_serie=1,**datos)])).status_code==422

def test_ejercicio_dinamico_no_admite_segundos(cliente,token_usuario):
    assert cliente.post('/api/v1/entrenamiento/sesiones',headers=encabezado(token_usuario),json=dict(series=[dict(ejercicio_id=1,numero_serie=1,duracion_segundos=20)])).status_code==422

def test_migracion_conserva_repeticiones_historicas(conexion_migraciones):
    c=conexion_migraciones
    command.upgrade(configurar(c),'0003_alimentacion_practica')
    c.execute(text("INSERT INTO usuarios (id,correo,nombre,contrasena_cifrada,rol,activo,version_sesion) VALUES (1,'pasado@example.com','Anterior','hash','usuario',true,1)"))
    c.execute(text("INSERT INTO ejercicios (id,nombre,grupo_muscular,nivel_minimo,equipamiento,es_compuesto,disponible_localmente) VALUES (1,'Plancha frontal','abdomen','principiante','Peso corporal',false,true)"))
    c.execute(text("INSERT INTO sesiones_realizadas (id,usuario_id,fecha) VALUES (1,1,'2026-10-20')"))
    c.execute(text("INSERT INTO series_realizadas (sesion_realizada_id,ejercicio_id,numero_serie,repeticiones) VALUES (1,1,1,12)"))
    actualizar(c)
    assert tuple(c.execute(text('SELECT repeticiones,duracion_segundos FROM series_realizadas')).one())==(12,None)
    assert diferencias(c)==[]
    c.execute(text('UPDATE series_realizadas SET duracion_segundos=20,repeticiones=0'))
    with pytest.raises(RuntimeError,match='duraciones'):
        command.downgrade(configurar(c),'0003_alimentacion_practica')
