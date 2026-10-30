"""Prepara una base PostgreSQL NUEVA y ficticia para revisar la fase 4.

Desde backend, con URL_POSTGRESQL_PRUEBAS local de fase 0:
python ../operaciones/ensayar_fase4.py --servir --puerto 18140
No usa la conexión configurada de producción ni reemplaza bases existentes.
"""
import argparse
import json
import os
from pathlib import Path
import sys
from uuid import uuid4

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))


def main():
    from sqlalchemy import create_engine
    from sqlalchemy.engine import make_url
    from sqlalchemy.orm import sessionmaker

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--servir", action="store_true")
    parser.add_argument("--puerto", type=int, default=18140)
    args = parser.parse_args()
    url = make_url(os.environ["URL_POSTGRESQL_PRUEBAS"])
    if url.host not in {"localhost", "127.0.0.1"} or not (url.database or "").startswith("senda_fase0"):
        raise RuntimeError("Solo se admite el PostgreSQL local de pruebas de fase 0.")
    nombre = f"senda_fase0_fase4_{uuid4().hex[:12]}"
    administrador = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with administrador.connect() as c:
        c.exec_driver_sql(f'CREATE DATABASE "{nombre}"')
    administrador.dispose()
    destino = url.set(database=nombre)
    os.environ["URL_BASE_DATOS"] = destino.render_as_string(hide_password=False)
    os.environ["ORIGENES_PERMITIDOS"] = "http://127.0.0.1:15174"

    from app.nucleo.migraciones import actualizar, diferencias
    from app.nucleo.alimentos_iniciales import cargar_alimentos
    from app.nucleo.catalogo_inicial import cargar_ejercicios
    from app.esquemas.usuario import RegistroUsuario
    from app.esquemas.perfil import RegistroPerfilBiometrico
    from app.servicios import autenticacion, perfil, plan, alimentacion

    motor = create_engine(destino)
    with motor.begin() as c:
        revision = actualizar(c)
        assert diferencias(c) == []
    with sessionmaker(bind=motor)() as s:
        cargar_alimentos(s); cargar_ejercicios(s)
        usuario = autenticacion.registrar_usuario(s, RegistroUsuario(
            correo="demostracion.fase4@example.com", nombre="Demostración fase 4", contrasena="Demostracion2026"))
        perfil.registrar_perfil(s, usuario, RegistroPerfilBiometrico(
            peso_kg=78, estatura_cm=174, edad=28, sexo="masculino", nivel_actividad="moderado",
            objetivo="mantenimiento", nivel_experiencia="intermedio", dias_entrenamiento_semana=4))
        plan.generar_plan(s, usuario)
        semana = alimentacion.generar(s, usuario)
    evidencia = RAIZ / "operaciones/evidencias/fase4"
    evidencia.mkdir(parents=True, exist_ok=True)
    (evidencia / "entorno-visual.json").write_text(json.dumps({
        "base_ficticia": nombre, "revision": revision, "recetas_distintas": semana["recetas_distintas"],
        "url_api": f"http://127.0.0.1:{args.puerto}/api/v1", "cuenta": "demostracion.fase4@example.com",
    }, indent=2), encoding="utf-8")
    print(f"Base ficticia nueva: {nombre}; revisión: {revision}; semana de siete días preparada.", flush=True)
    if args.servir:
        import uvicorn
        from app.main import aplicacion
        uvicorn.run(aplicacion, host="127.0.0.1", port=args.puerto)


if __name__ == "__main__":
    main()
