"""Persistencia real y concurrencia con la misma fixture aislada de fase 0."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy

from alembic import command
from fastapi import HTTPException
import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import sessionmaker

from app.esquemas.alimentacion import CambioComida, PreferenciasEntrada
from app.modelos.alimentacion import PreferenciasAlimentarias, SemanaAlimentaria
from app.modelos.usuario import Usuario
from app.modelos.perfil import PerfilBiometrico
from app.nucleo.alimentos_iniciales import cargar_alimentos
from app.nucleo.catalogo_inicial import cargar_ejercicios
from app.nucleo.migraciones import actualizar, configurar, diferencias
from app.servicios import alimentacion, plan
from tests.test_migraciones import conexion_migraciones  # noqa: F401, fixture compartida
from tests.test_plan_nutricional import PERFIL_VALIDO


def test_actualiza_0002_poblada_y_conserva_usuarios(conexion_migraciones):
    c = conexion_migraciones
    command.upgrade(configurar(c), "0002_recuperacion_acceso")
    c.execute(text("INSERT INTO usuarios (correo,nombre,contrasena_cifrada,rol,activo,version_sesion) VALUES ('fase2@example.com','Conservado','hash','usuario',true,7)"))
    actualizar(c)
    assert tuple(c.execute(text("SELECT nombre,version_sesion FROM usuarios")).one()) == ("Conservado", 7)
    assert diferencias(c) == []
    command.downgrade(configurar(c), "0002_recuperacion_acceso")
    assert c.execute(text("SELECT version_sesion FROM usuarios")).scalar_one() == 7
    actualizar(c)
    assert diferencias(c) == []


def preparar_contexto(conexion, monkeypatch):
    actualizar(conexion)
    conexion.commit()
    fabrica = sessionmaker(bind=conexion.engine)
    monkeypatch.setattr(plan, "obtener_motor", lambda: None)
    with fabrica() as s:
        cargar_alimentos(s)
        cargar_ejercicios(s)
        u = Usuario(correo="semana@example.com", nombre="Cuenta ficticia", contrasena_cifrada="hash-ficticio")
        s.add(u); s.flush()
        p = PerfilBiometrico(usuario_id=u.id, **PERFIL_VALIDO)
        s.add(p); s.commit()
        plan.generar_plan(s, u)
        semana = alimentacion.generar(s, u)
        identificador = u.id
    return fabrica, identificador, semana


def test_semana_json_y_restricciones_sobre_esquema_migrado(conexion_migraciones, monkeypatch):
    fabrica, id_usuario, semana = preparar_contexto(conexion_migraciones, monkeypatch)
    with fabrica() as s:
        u = s.get(Usuario, id_usuario)
        assert alimentacion.publicar(alimentacion.consultar(s, u)) == semana
        alimentacion.guardar_preferencias(s, u, PreferenciasEntrada(alergias=["mani"]))
    with fabrica() as s:
        assert s.get(PreferenciasAlimentarias, id_usuario).datos["alergias"] == ["mani"]
        with pytest.raises(HTTPException) as error:
            alimentacion.consultar(s, s.get(Usuario, id_usuario))
        assert error.value.status_code == 409


def test_cambio_concurrente_solo_acepta_una_revision_postgresql(conexion_migraciones, monkeypatch):
    if conexion_migraciones.dialect.name != "postgresql":
        pytest.skip("Concurrencia de filas comprobada en PostgreSQL.")
    fabrica, id_usuario, semana = preparar_contexto(conexion_migraciones, monkeypatch)
    with fabrica() as s:
        opcion = alimentacion.opciones_de_cambio(s, s.get(Usuario, id_usuario), 1, 2)["opciones"][0]
    datos = CambioComida(revision=semana["revision"], dia=1, tiempo=2, receta_id=opcion["receta_id"])
    def intentar(_):
        with fabrica() as s:
            try:
                return alimentacion.cambiar(s, s.get(Usuario, id_usuario), datos)["revision"]
            except HTTPException as error:
                assert error.status_code == 409
                return "rechazado"
    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        resultados = list(ejecutor.map(intentar, range(2)))
    assert resultados.count("rechazado") == 1
    assert resultados.count(semana["revision"] + 1) == 1
    with fabrica() as s:
        assert s.get(SemanaAlimentaria, id_usuario).revision == semana["revision"] + 1
