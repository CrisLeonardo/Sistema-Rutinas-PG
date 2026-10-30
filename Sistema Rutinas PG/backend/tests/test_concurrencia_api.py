import asyncio
import pytest
from app.nucleo.concurrencia import LimiteSolicitudesBD

def test_espera_sin_bloquear_estado_y_conserva_respuestas():
    async def ensayo():
        activas=0;maximo=0
        liberar=asyncio.Event();entraron=asyncio.Event();estado=asyncio.Event()
        async def app(scope,receive,send):
            nonlocal activas,maximo
            if scope['path'].endswith('/estado'):
                estado.set();return
            activas+=1;maximo=max(maximo,activas)
            if activas==2: entraron.set()
            await liberar.wait()
            await send({'type':'http.response.start','status':201})
            await send({'type':'http.response.body','body':b'guardado'})
            activas-=1
        middleware=LimiteSolicitudesBD(app,capacidad=2)
        respuestas=[]
        async def enviar(m): respuestas.append(m)
        async def recibir(): return {'type':'http.request','body':b''}
        tareas=[asyncio.create_task(middleware(dict(type='http',path='/api/v1/entrenamiento/sesiones',method='POST'),recibir,enviar)) for _ in range(12)]
        await asyncio.wait_for(entraron.wait(),1)
        await middleware(dict(type='http',path='/api/v1/estado',method='GET'),recibir,enviar)
        assert estado.is_set() and maximo==2
        liberar.set();await asyncio.wait_for(asyncio.gather(*tareas),2)
        assert maximo==2
        assert sum(m.get('status')==201 for m in respuestas)==12
        assert sum(m.get('body')==b'guardado' for m in respuestas)==12
    asyncio.run(ensayo())

@pytest.mark.parametrize('cancelar',[False,True])
def test_libera_permiso_ante_error_o_cancelacion(cancelar):
    async def ensayo():
        entro=asyncio.Event();llamadas=0
        async def app(scope,receive,send):
            nonlocal llamadas
            llamadas+=1
            if llamadas==1:
                entro.set()
                if cancelar: await asyncio.Future()
                raise RuntimeError('fallo de ensayo')
        middleware=LimiteSolicitudesBD(app,capacidad=1)
        async def no_op(*args): pass
        scope=dict(type='http',path='/api/v1/prueba',method='GET')
        primera=asyncio.create_task(middleware(scope,no_op,no_op))
        await entro.wait()
        if cancelar: primera.cancel()
        with pytest.raises(asyncio.CancelledError if cancelar else RuntimeError): await primera
        await asyncio.wait_for(middleware(scope,no_op,no_op),1)
        assert llamadas==2
    asyncio.run(ensayo())
