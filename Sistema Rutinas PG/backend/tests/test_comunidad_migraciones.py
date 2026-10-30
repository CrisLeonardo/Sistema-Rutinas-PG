from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from app.nucleo.migraciones import actualizar, diferencias
from app.modelos.usuario import Usuario
from app.esquemas.comunidad import CrearGrupo, ResponderInvitacion
from app.servicios import comunidad
from tests.test_migraciones import conexion_migraciones  # noqa: F401

def test_persistencia_y_consumo_concurrente(conexion_migraciones):
    c=conexion_migraciones
    actualizar(c); assert diferencias(c)==[]
    c.commit()
    fabrica=sessionmaker(bind=c.engine)
    if c.dialect.name=='sqlite':
        # La fixture SQLite mantiene una conexión única y no modela concurrencia.
        pytest.skip('La concurrencia del piloto requiere PostgreSQL.')
    with fabrica() as s:
        cuentas=[Usuario(correo=f'concurrencia{i}@example.com',nombre='Ficticio',contrasena_cifrada='hash') for i in range(3)]
        s.add_all(cuentas);s.commit()
        ids=[u.id for u in cuentas]
        g=comunidad.crear(s,cuentas[0],CrearGrupo(nombre='Grupo ensayo',alias='Sol',consentimiento=True))
        codigo=comunidad.invitar(s,cuentas[0],g['id'])['codigo']
    def aceptar(uid):
        with fabrica() as s:
            try:
                comunidad.responder(s,s.get(Usuario,uid),ResponderInvitacion(codigo=codigo,aceptar=True,alias=f'Luna{uid}',consentimiento=True))
                return 200
            except HTTPException as e:
                return e.status_code
    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        resultados=list(ejecutor.map(aceptar,ids[1:]))
    assert sorted(resultados)==[200,404]
    with fabrica() as s:
        assert len(comunidad.ver(s,s.get(Usuario,ids[0]),g['id'])['miembros'])==2
