"""Comprobación pública de solo lectura: API directa y reenvío de la interfaz.

No inicia sesión, no envía credenciales, no consulta cuentas ni certifica la BD.
Los tiempos incluyen el arranque si ocurre durante esta ejecución.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def origen(valor):
    partes = urlsplit(valor)
    if (partes.scheme not in ('http', 'https') or not partes.hostname
            or partes.username or partes.password or partes.query or partes.fragment
            or partes.path not in ('', '/')):
        raise argparse.ArgumentTypeError('Use solo el origen HTTP(S), sin credenciales, ruta ni parámetros.')
    return valor.rstrip('/')


def comprobar(nombre, base, ruta, timeout):
    inicio = time.perf_counter()
    resultado = dict(destino=nombre, ruta=ruta, estado_http=None, json=False)
    try:
        solicitud = Request(base + ruta, headers={'Accept': 'application/json', 'Cache-Control': 'no-cache'}, method='GET')
        try:
            respuesta = urlopen(solicitud, timeout=timeout)
        except HTTPError as error:
            respuesta = error
        with respuesta:
            resultado['estado_http'] = respuesta.status
            resultado['tipo'] = respuesta.headers.get_content_type()
            cuerpo = respuesta.read(4096)
        if resultado['tipo'] == 'application/json':
            try:
                datos = json.loads(cuerpo)
                resultado['json'] = True
                if ruta.endswith('/estado'):
                    resultado['salud_confirmada'] = resultado['estado_http'] == 200 and datos.get('estado') == 'disponible'
            except (ValueError, AttributeError):
                pass
    except (URLError, TimeoutError, OSError):
        resultado['fallo'] = 'No se completó la conexión dentro del plazo o falló la red.'
    resultado['segundos'] = round(time.perf_counter() - inicio, 3)
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interfaz', type=origen, default='https://senda-gt.onrender.com')
    parser.add_argument('--servicios', type=origen, default='https://rutinas-servicios.onrender.com')
    parser.add_argument('--timeout', type=float, default=75)
    parser.add_argument('--salida', type=Path)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout debe ser positivo')
    pruebas = [comprobar(nombre, base, ruta, args.timeout)
               for nombre, base in [('api-directa', args.servicios), ('reenvio-interfaz', args.interfaz)]
               for ruta in ['/api/v1/estado', '/api/v1/autenticacion/opciones-publicas', '/api/v1/catalogos/ejercicios']]
    informe = dict(fecha_utc=datetime.now(timezone.utc).isoformat(),
        alcance='Lecturas públicas puntuales. Un 401 en catálogo sin token es esperado; no prueba acceso autenticado ni conexión con la BD.',
        destinos=dict(interfaz=args.interfaz, servicios=args.servicios), comprobaciones=pruebas)
    texto = json.dumps(informe, ensure_ascii=False, indent=2)
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        # Conservar todos los ensayos: no sobrescribir un resultado anterior.
        with args.salida.open('x', encoding='utf-8') as archivo:
            archivo.write(texto + '\n')
    print(texto)
    return 0 if all(p['json'] and p['estado_http'] == (401 if p['ruta'].endswith('/ejercicios') else 200)
                    and (not p['ruta'].endswith('/estado') or p.get('salud_confirmada')) for p in pruebas) else 1


if __name__ == '__main__':
    raise SystemExit(main())
