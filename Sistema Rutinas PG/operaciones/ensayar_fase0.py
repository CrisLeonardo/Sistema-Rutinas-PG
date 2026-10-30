"""Ensayo reproducible con datos ficticios: API, migracion y respaldo PostgreSQL.

Desde backend: python ../operaciones/ensayar_fase0.py
Requiere URL_POSTGRESQL_PRUEBAS y el contenedor senda_fase0_postgres etiquetado
proyecto=senda-fase0. Crea dos bases nuevas y las conserva para inspeccion.
No admite destinos remotos ni utiliza la URL de produccion de la aplicacion.
"""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from uuid import uuid4

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.api.dependencias import obtener_sesion
from app.main import aplicacion
from app.nucleo.alimentos_iniciales import cargar_alimentos
from app.nucleo.base_datos import Base
from app.nucleo.catalogo_inicial import cargar_ejercicios
from app.nucleo.migraciones import actualizar, diferencias, revision_actual
from app.servicios.plan import obtener_motor

CONTENEDOR = "senda_fase0_postgres"
CORREO = "demostracion.fase0@example.com"
CONTRASENA = "Demostracion2026"


def docker(*argumentos):
    return subprocess.run(
        ["docker", *argumentos], check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout.strip()


def huellas(motor):
    resultado = {}
    with motor.connect() as conexion:
        for tabla in Base.metadata.sorted_tables:
            filas = [dict(fila) for fila in conexion.execute(
                select(tabla).order_by(*tabla.primary_key.columns)
            ).mappings()]
            contenido = json.dumps(filas, sort_keys=True, ensure_ascii=False, default=str)
            resultado[tabla.name] = {
                "filas": len(filas), "sha256": hashlib.sha256(contenido.encode()).hexdigest()
            }
    return resultado


def recorrido(motor, crear_datos):
    fabrica = sessionmaker(motor)

    def sesion_aislada():
        with fabrica() as sesion:
            yield sesion

    anteriores = dict(aplicacion.dependency_overrides)
    aplicacion.dependency_overrides[obtener_sesion] = sesion_aislada
    cliente = TestClient(aplicacion)
    comprobaciones = []

    def pedir(metodo, ruta, esperado=200, token=None, **opciones):
        inicio = perf_counter()
        respuesta = cliente.request(
            metodo, f"/api/v1{ruta}",
            headers={"Authorization": f"Bearer {token}"} if token else {}, **opciones
        )
        comprobaciones.append({
            "metodo": metodo, "ruta": ruta, "esperado": esperado,
            "obtenido": respuesta.status_code,
            "segundos": round(perf_counter() - inicio, 4),
        })
        if respuesta.status_code != esperado:
            raise AssertionError(f"{metodo} {ruta}: {respuesta.status_code}, esperado {esperado}")
        return respuesta

    try:
        if crear_datos:
            pedir("POST", "/autenticacion/registro", 201, json={
                "nombre": "Demostracion fase cero", "correo": CORREO, "contrasena": CONTRASENA,
            })
        token = pedir("POST", "/autenticacion/acceso", json={
            "correo": CORREO, "contrasena": CONTRASENA,
        }).json()["token_acceso"]
        if crear_datos:
            perfil = {
                "peso_kg": 78, "estatura_cm": 174, "edad": 28, "sexo": "masculino",
                "nivel_actividad": "moderado", "objetivo": "mantenimiento",
                "nivel_experiencia": "principiante", "dias_entrenamiento_semana": 3,
                "lesiones": [], "condiciones": [],
            }
            pedir("POST", "/perfil-biometrico", 422, token, json={**perfil, "edad": 17})
            pedir("POST", "/perfil-biometrico", 201, token, json=perfil)
            pedir("POST", "/plan-nutricional", 201, token)
        pedir("GET", "/perfil-biometrico", token=token)
        plan = pedir("GET", "/plan-nutricional", token=token).json()
        rutina = pedir("GET", "/rutina", token=token).json()
        pedir("GET", "/plan-nutricional/menu", token=token)
        pedir("GET", "/plan-nutricional/lista-de-compras", token=token)
        sesion = rutina["sesiones"][0]
        pedir("GET", f'/entrenamiento/sesiones/{sesion["id"]}', token=token)
        if crear_datos:
            ejercicio = sesion["ejercicios"][0]
            pedir("POST", "/entrenamiento/sesiones", 201, token, json={
                "sesion_id": sesion["id"], "duracion_minutos": 30, "percepcion_esfuerzo": 6,
                "series": [{"ejercicio_id": ejercicio["ejercicio_id"], "numero_serie": 1,
                            "repeticiones": 10, "peso_kg": 10}],
            })
            pedir("POST", "/progreso", 201, token, json={
                "peso_kg": 78, "sesiones_cumplidas": 1, "adherencia_nutricional": 80,
            })
        pedir("GET", "/entrenamiento/sesiones", token=token)
        pedir("GET", "/progreso/reporte", token=token)
        pedir("GET", "/juego", token=token)
        informes = pedir("GET", "/informes", token=token).json()
        clave = informes[0]["clave"]
        pedir("GET", f"/informes/{clave}", token=token)
        for formato in ("csv", "xlsx", "pdf"):
            archivo = pedir("GET", f"/informes/{clave}/{formato}", token=token)
            assert archivo.content and archivo.headers["cache-control"] == "no-store"
        pedir("GET", "/perfil-biometrico", 401)
        pedir("GET", "/usuarios", 403, token)
        if crear_datos:
            otro = "otra.persona.fase0@example.com"
            pedir("POST", "/autenticacion/registro", 201, json={
                "nombre": "Otra demostracion", "correo": otro, "contrasena": CONTRASENA,
            })
            segundo = pedir("POST", "/autenticacion/acceso", json={
                "correo": otro, "contrasena": CONTRASENA,
            }).json()["token_acceso"]
            pedir("GET", f'/entrenamiento/sesiones/{sesion["id"]}', 404, segundo)
            pedir("POST", "/perfil-biometrico", 201, segundo, json={
                **perfil, "condiciones": ["diabetes"],
            })
            pedir("POST", "/plan-nutricional", 403, segundo)
        return {"comprobaciones": comprobaciones, "origen_calculo": plan["origen_calculo"]}
    finally:
        cliente.close()
        aplicacion.dependency_overrides.clear()
        aplicacion.dependency_overrides.update(anteriores)


def main():
    url = make_url(os.environ["URL_POSTGRESQL_PRUEBAS"])
    if url.host not in {"127.0.0.1", "localhost"} or url.database != "senda_fase0":
        raise RuntimeError("Use exclusivamente la base local senda_fase0.")
    etiqueta = docker("inspect", "--format", '{{ index .Config.Labels "proyecto" }}', CONTENEDOR)
    if etiqueta != "senda-fase0":
        raise RuntimeError("El contenedor no esta identificado como ensayo de Senda.")
    identificador = uuid4().hex[:12]
    origen = f"senda_fase0_origen_{identificador}"
    destino = f"senda_fase0_restaurada_{identificador}"
    administrador = create_engine(url, isolation_level="AUTOCOMMIT")
    with administrador.connect() as conexion:
        for nombre in (origen, destino):
            conexion.exec_driver_sql(f'CREATE DATABASE "{nombre}"')
    administrador.dispose()
    fuente = create_engine(url.set(database=origen))
    recuperada = create_engine(url.set(database=destino))
    with fuente.begin() as conexion:
        actualizar(conexion)
    with sessionmaker(fuente)() as sesion:
        cargar_ejercicios(sesion)
        cargar_alimentos(sesion)
    obtener_motor()  # Calentamiento separado de la medicion de generacion.
    antes = recorrido(fuente, crear_datos=True)
    contenido_original = huellas(fuente)
    archivo_contenedor = f"/tmp/senda_fase0_{identificador}.dump"
    docker("exec", CONTENEDOR, "pg_dump", "--username", url.username, "--dbname", origen,
           "--format=custom", "--no-owner", "--no-acl", "--file", archivo_contenedor)
    evidencia = RAIZ / "operaciones/evidencias/fase0"
    evidencia.mkdir(parents=True, exist_ok=True)
    respaldo = evidencia / "recuperacion-ficticia.dump"
    docker("cp", f"{CONTENEDOR}:{archivo_contenedor}", str(respaldo))
    docker("exec", CONTENEDOR, "pg_restore", "--username", url.username, "--dbname", destino,
           "--exit-on-error", "--single-transaction", "--no-owner", "--no-acl", archivo_contenedor)
    contenido_recuperado = huellas(recuperada)
    assert contenido_original == contenido_recuperado, "La restauracion no conserva el contenido."
    with recuperada.connect() as conexion:
        assert diferencias(conexion) == []
        revision = revision_actual(conexion)
    despues = recorrido(recuperada, crear_datos=False)
    # Comprueba tambien las secuencias; un respaldo con IDs sin secuencias falla al insertar.
    with recuperada.begin() as conexion:
        usuarios = Base.metadata.tables["usuarios"]
        nuevo = conexion.execute(usuarios.insert().values(
            nombre="Prueba de secuencia", correo="secuencia.fase0@example.com",
            contrasena_cifrada="hash-ficticio",
        )).inserted_primary_key[0]
        assert nuevo > contenido_original["usuarios"]["filas"]
    resultado = {
        "fecha_local": __import__("datetime").datetime.now().astimezone().isoformat(),
        "base_origen": origen, "base_restaurada": destino, "revision": revision,
        "contenido_identico": True, "secuencia_verificada": True,
        "tablas": contenido_original, "antes": antes, "despues": despues,
        "tamano_respaldo_bytes": respaldo.stat().st_size,
    }
    (evidencia / "recuperacion-y-recorridos.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    fuente.dispose()
    recuperada.dispose()
    print(json.dumps({k: resultado[k] for k in (
        "base_origen", "base_restaurada", "revision", "contenido_identico", "secuencia_verificada"
    )}, ensure_ascii=False))
    print(f'Comprobaciones HTTP: {len(antes["comprobaciones"]) + len(despues["comprobaciones"])}')


if __name__ == "__main__":
    main()
