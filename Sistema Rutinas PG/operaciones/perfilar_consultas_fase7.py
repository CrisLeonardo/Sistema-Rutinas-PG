"""Perfilado local de consultas; conserva tiempos, conteos y huellas, sin datos."""
from pathlib import Path
from collections import Counter
from time import perf_counter
import hashlib
import json
import sys

RAIZ=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(RAIZ/'backend'))
from sqlalchemy import create_engine,event
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.main import aplicacion
from app.api.dependencias import obtener_sesion

def main():
    salida=RAIZ/'operaciones/evidencias/fase7-revision'
    salida.mkdir(parents=True,exist_ok=True)
    nombre=(RAIZ/'operaciones/evidencias/fase7/base-ui.txt').read_text(encoding='utf-8').strip()
    assert nombre.startswith('senda_fase0_validacion_') and nombre.replace('_','').isalnum()
    motor=create_engine('postgresql+psycopg://senda_pruebas:SoloPruebasLocales2026@127.0.0.1:55432/'+nombre)
    tiempos=[];tipos=Counter()
    def antes(c,cur,sentencia,parametros,contexto,muchos): contexto.inicio_ensayo=perf_counter()
    def despues(c,cur,sentencia,parametros,contexto,muchos):
        tiempos.append(perf_counter()-contexto.inicio_ensayo)
        tipos[sentencia.split()[0].upper()]+=1
    def sesion_prueba():
        with Session(motor) as s: yield s
    previas=dict(aplicacion.dependency_overrides)
    aplicacion.dependency_overrides[obtener_sesion]=sesion_prueba
    cliente=TestClient(aplicacion)
    try:
        r=cliente.post('/api/v1/autenticacion/acceso',json=dict(correo='fase7@example.com',contrasena='PruebaSenda2026!'))
        r.raise_for_status();h={'Authorization':'Bearer '+r.json()['token_acceso']}
        event.listen(motor,'before_cursor_execute',antes);event.listen(motor,'after_cursor_execute',despues)
        resultados=[]
        for ruta in ['/rutina','/plan-nutricional/menu','/plan-nutricional/lista-de-compras','/progreso/reporte','/perfil-biometrico/historial','/juego']:
            tiempos.clear();tipos.clear();inicio=perf_counter()
            r=cliente.get('/api/v1'+ruta,headers=h)
            assert r.status_code==200,(ruta,r.status_code)
            resultados.append(dict(ruta=ruta,total_segundos=perf_counter()-inicio,
                sql_segundos=sum(tiempos),consultas=len(tiempos),tipos=dict(tipos),
                sha256=hashlib.sha256(r.content).hexdigest()))
        (salida/'perfil-consultas.json').write_text(json.dumps(resultados,indent=2),encoding='utf-8')
        print(json.dumps(resultados,indent=2))
    finally:
        cliente.close();aplicacion.dependency_overrides.clear();aplicacion.dependency_overrides.update(previas);motor.dispose()

if __name__=='__main__': main()
