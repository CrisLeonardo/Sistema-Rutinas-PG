"""La entrega individual conserva Mi senda y cierra el piloto social."""
import pytest
from app.nucleo.configuracion import Configuracion, configuracion
from app.servicios import comunidad
from tests.conftest import encabezado

def test_configuracion_individual_por_omision():
    assert Configuracion(_env_file=None).comunidad_habilitada is False

@pytest.mark.parametrize('metodo,ruta,cuerpo', [
    ('GET','/grupos',None), ('POST','/grupos',dict(nombre='Ensayo',alias='Sol',consentimiento=True)),
    ('GET','/grupos/inexistente',None),
    ('POST','/invitaciones/responder',dict(codigo='a'*43,aceptar=False)),
])
def test_comunidad_no_disponible(cliente,token_usuario,metodo,ruta,cuerpo,monkeypatch):
    monkeypatch.setattr(configuracion,'comunidad_habilitada',False)
    r=cliente.request(metodo,'/api/v1/comunidad'+ruta,headers=encabezado(token_usuario),json=cuerpo)
    assert r.status_code==404

def test_senda_individual_sin_eventos_sociales(cliente,token_usuario,token_segundo_usuario,monkeypatch):
    monkeypatch.setattr(configuracion,'comunidad_habilitada',False)
    def no_ejecutar(*args):
        raise AssertionError('El registro individual no debe invocar el piloto social.')
    monkeypatch.setattr(comunidad,'registrar_evento',no_ejecutar)
    h=encabezado(token_usuario)
    r=cliente.post('/api/v1/entrenamiento/sesiones',headers=h,json=dict(series=[dict(
        ejercicio_id=1,numero_serie=1,repeticiones=8,peso_kg=20)]))
    assert r.status_code==201,r.text
    puntos=r.json()['recompensa']['puntos_totales']
    assert puntos>0
    estado=cliente.get('/api/v1/juego',headers=h).json()
    assert estado['puntos_totales']==puntos
    assert cliente.get('/api/v1/juego',headers=encabezado(token_segundo_usuario)).json()['puntos_totales']==0
    assert cliente.get('/api/v1/juego').status_code==401

def test_documentacion_no_ofrece_piloto_social(cliente):
    assert not any('/comunidad/' in ruta for ruta in cliente.get('/openapi.json').json()['paths'])
