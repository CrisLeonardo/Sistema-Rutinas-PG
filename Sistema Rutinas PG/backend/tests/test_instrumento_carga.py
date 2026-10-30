import asyncio
import httpx
import pytest
from prueba_de_carga import Medicion, _medir, informar

def test_p95_por_rango_mas_cercano():
    m=Medicion('Ensayo',100,tiempos=list(range(1,51)))
    assert m.percentil_95==48

def test_un_p95_bueno_no_oculta_una_peticion_lenta():
    m=Medicion('Ensayo',2,tiempos=[.1]*49+[3.1],esperadas=50)
    assert m.percentil_95==.1 and not m.cumple

@pytest.mark.parametrize('cantidad',[0,49])
def test_muestras_incompletas_no_cumplen(cantidad):
    m=Medicion('Ensayo',2,tiempos=[.1]*cantidad,esperadas=50)
    assert not m.cumple

def test_preparacion_parcial_no_acredita_50(capsys):
    assert not informar({'uno':Medicion('Uno',2,tiempos=[.1]*49)},49,.5,50)
    assert 'Preparación incompleta' in capsys.readouterr().out

@pytest.mark.parametrize('estado',[200,503])
def test_mide_tambien_respuestas_fallidas(estado):
    async def respuesta():
        return httpx.Response(estado)
    m=Medicion('Uno',2)
    asyncio.run(_medir(m,respuesta()))
    assert len(m.tiempos)==1 and m.causas=={str(estado):1}
    assert m.fallos==(1 if estado==503 else 0)

def test_excepciones_sin_mensaje_sensible():
    async def fallar():
        raise httpx.ReadTimeout('secreto-que-no-debe-registrarse')
    m=Medicion('Uno',2)
    asyncio.run(_medir(m,fallar()))
    assert len(m.tiempos)==1 and m.fallos==1
    assert m.causas=={'ReadTimeout':1}
