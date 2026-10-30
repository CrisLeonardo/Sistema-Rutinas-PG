"""Mide arranque y primer plan sobre la base ficticia de fase 7; proceso propio.

No usa una conexión tomada de .env ni mide producción. Conserva solo tiempos,
estados y origen del cálculo, nunca contraseñas, tokens, cuerpos o medidas.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import subprocess
import sys
import time
import httpx
import argparse

def main():
    base=Path(__file__).resolve().parents[1]
    argumentos=argparse.ArgumentParser(description=__doc__)
    argumentos.add_argument('--salida',type=Path,default=base/'operaciones/evidencias/fase7')
    opciones=argumentos.parse_args()
    salida=opciones.salida
    salida.mkdir(parents=True,exist_ok=True)
    nombre=(base/'operaciones/evidencias/fase7/base-ui.txt').read_text(encoding='utf-8').strip()
    assert nombre.startswith('senda_fase0_validacion_') and nombre.replace('_','').isalnum()
    entorno=os.environ.copy()
    entorno.update(URL_BASE_DATOS='postgresql+psycopg://senda_pruebas:SoloPruebasLocales2026@127.0.0.1:55432/'+nombre,
                   COMUNIDAD_HABILITADA='false')
    url='http://127.0.0.1:18171'
    with httpx.Client(timeout=.5) as cliente:
        try:
            cliente.get(url+'/api/v1/estado')
        except (httpx.ConnectError, httpx.ConnectTimeout):
            pass
        else:
            raise RuntimeError('El puerto de ensayo ya está ocupado; no se tocará ese proceso.')
    inicio=time.perf_counter()
    with (salida/'servidor-arranque.log').open('w',encoding='utf-8') as log:
        proceso=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:aplicacion',
                '--host','127.0.0.1','--port','18171'],cwd=base/'backend',env=entorno,
                stdout=log,stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        try:
            with httpx.Client(base_url=url,timeout=45) as cliente:
                while True:
                    if proceso.poll() is not None: raise RuntimeError('El servidor no arrancó; revisar log de ensayo.')
                    if time.perf_counter()-inicio>40: raise TimeoutError('No hubo respuesta de salud en 40 s.')
                    try:
                        r=cliente.get('/api/v1/estado',timeout=.5)
                        if r.status_code==200: break
                    except httpx.RequestError: pass
                    time.sleep(.05)
                salud=time.perf_counter()-inicio
                r=cliente.post('/api/v1/autenticacion/acceso',json=dict(
                    correo='fase7@example.com',contrasena='PruebaSenda2026!'))
                r.raise_for_status()
                h={'Authorization':'Bearer '+r.json()['token_acceso']}
                registros=[]
                for momento in ('primer_plan','plan_siguiente'):
                    principio=time.perf_counter()
                    r=cliente.post('/api/v1/plan-nutricional',headers=h)
                    registros.append(dict(momento=momento,segundos=time.perf_counter()-principio,
                        estado=r.status_code,origen=r.json().get('origen_calculo')))
                datos=dict(fecha_utc=datetime.now(timezone.utc).isoformat(),
                    escenario='Proceso nuevo local, PostgreSQL existente; caché de archivos del sistema operativo no controlada',
                    salud_desde_creacion_segundos=salud,planes=registros)
                (salida/'arranque.json').write_text(json.dumps(datos,indent=2),encoding='utf-8')
                print(json.dumps(datos,ensure_ascii=False))
        finally:
            proceso.terminate()
            try: proceso.wait(timeout=10)
            except subprocess.TimeoutExpired: proceso.kill();proceso.wait(timeout=5)

if __name__=='__main__': main()
