"""Restaura solo la base ficticia de fase 7 en otra base nueva y comprueba huellas."""
from pathlib import Path
from uuid import uuid4
import json
import sys
from time import perf_counter

RAIZ=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(RAIZ/'backend'))
from ensayar_fase0 import docker, huellas, CONTENEDOR
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from app.modelos.usuario import Usuario
from app.nucleo.migraciones import diferencias, revision_actual
from app.api.dependencias import obtener_sesion
from app.main import aplicacion
from fastapi.testclient import TestClient

def main():
    evidencia=RAIZ/'operaciones/evidencias/fase7'
    origen=(evidencia/'base-ui.txt').read_text(encoding='utf-8').strip()
    assert origen.startswith('senda_fase0_validacion_') and origen.replace('_','').isalnum()
    assert docker('inspect','--format','{{ index .Config.Labels "proyecto" }}',CONTENEDOR)=='senda-fase0'
    destino='senda_fase0_restauracion7_'+uuid4().hex[:12]
    prefijo='postgresql+psycopg://senda_pruebas:SoloPruebasLocales2026@127.0.0.1:55432/'
    original=create_engine(prefijo+origen)
    antes=huellas(original)
    contenedor_dump='/tmp/'+destino+'.dump'
    inicio=perf_counter()
    docker('exec',CONTENEDOR,'pg_dump','--username','senda_pruebas','--dbname',origen,
           '--format=custom','--no-owner','--no-acl','--file',contenedor_dump)
    archivo=evidencia/(destino+'.dump')
    docker('cp',CONTENEDOR+':'+contenedor_dump,str(archivo))
    admin=create_engine(prefijo+'senda_fase0',isolation_level='AUTOCOMMIT')
    with admin.connect() as c: c.exec_driver_sql(f'CREATE DATABASE "{destino}"')
    admin.dispose()
    docker('exec',CONTENEDOR,'pg_restore','--username','senda_pruebas','--dbname',destino,
           '--exit-on-error','--single-transaction','--no-owner','--no-acl',contenedor_dump)
    restaurada=create_engine(prefijo+destino)
    despues=huellas(restaurada)
    assert antes==despues,'El contenido restaurado difiere.'
    with restaurada.connect() as c:
        assert diferencias(c)==[]
        revision=revision_actual(c)
    with Session(restaurada) as s:
        mayor=s.scalar(select(func.max(Usuario.id)))
        prueba=Usuario(correo='secuencia-restaurada@example.com',nombre='Ensayo',contrasena_cifrada='hash-ficticio')
        s.add(prueba);s.flush();assert prueba.id>mayor
        s.rollback()  # No conserva una cuenta adicional; la secuencia sí avanza.
    resultados=[]
    def sesion_aislada():
        with Session(restaurada) as s: yield s
    anteriores=dict(aplicacion.dependency_overrides)
    aplicacion.dependency_overrides[obtener_sesion]=sesion_aislada
    cliente=TestClient(aplicacion)  # Sin lifespan: no ejecuta el arranque global.
    try:
        r=cliente.post('/api/v1/autenticacion/acceso',json=dict(
            correo='fase7@example.com',contrasena='PruebaSenda2026!'))
        assert r.status_code==200
        h={'Authorization':'Bearer '+r.json()['token_acceso']}
        for ruta,esperado in [('/plan-nutricional',200),('/rutina',200),
                ('/plan-nutricional/menu',200),('/juego',200),
                ('/entrenamiento/sesiones',200),('/comunidad/grupos',404)]:
            r=cliente.get('/api/v1'+ruta,headers=h)
            assert r.status_code==esperado,(ruta,r.status_code)
            resultados.append(dict(ruta=ruta,estado=r.status_code))
    finally:
        cliente.close()
        aplicacion.dependency_overrides.clear();aplicacion.dependency_overrides.update(anteriores)
    datos=dict(origen=origen,destino=destino,tablas=len(antes),contenido_identico=True,
        revision=revision,secuencia_usuario_correcta=True,respaldo_bytes=archivo.stat().st_size,
        duracion_segundos=perf_counter()-inicio,huellas=despues,comprobaciones=resultados)
    (evidencia/'restauracion.json').write_text(json.dumps(datos,ensure_ascii=False,indent=2),encoding='utf-8')
    original.dispose();restaurada.dispose()
    print(f'Restauración comprobada: {len(antes)} tablas, revisión {revision}.')

if __name__=='__main__': main()
