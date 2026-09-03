"""Logica de negocio del perfil biometrico (epica E2).

Concentra las reglas de las historias HU-04 y HU-05. Cada actualizacion de
medidas inserta un registro nuevo en lugar de sobrescribir el anterior: de esa
insercion acumulativa nace el historial que exige la historia HU-05 y que
alimentara el reajuste del plan en la Iteracion 5.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.esquemas.perfil import RegistroPerfilBiometrico
from app.modelos.perfil import PerfilBiometrico
from app.modelos.usuario import Usuario


class PerfilNoRegistrado(Exception):
    """El usuario todavia no ha registrado ningun perfil biometrico."""


def registrar_perfil(
    sesion: Session,
    usuario: Usuario,
    datos: RegistroPerfilBiometrico,
) -> PerfilBiometrico:
    """Guarda una medicion nueva asociada a la cuenta en sesion (historia HU-04).

    El identificador del usuario proviene siempre del token verificado y nunca
    del cuerpo de la peticion, de modo que una cuenta no pueda registrar medidas
    a nombre de otra (regla del negocio *f*).
    """
    perfil = PerfilBiometrico(
        usuario_id=usuario.id,
        peso_kg=datos.peso_kg,
        estatura_cm=datos.estatura_cm,
        edad=datos.edad,
        sexo=datos.sexo,
        nivel_actividad=datos.nivel_actividad,
        objetivo=datos.objetivo,
        nivel_experiencia=datos.nivel_experiencia,
        dias_entrenamiento_semana=datos.dias_entrenamiento_semana,
    )
    sesion.add(perfil)
    sesion.commit()
    sesion.refresh(perfil)
    return perfil


def obtener_perfil_vigente(sesion: Session, usuario: Usuario) -> PerfilBiometrico:
    """Devuelve la medicion mas reciente del usuario.

    Es el perfil sobre el que se generan los planes; que exista es la condicion
    que el apartado 4.8.3 impone antes de calcular un requerimiento energetico.
    """
    sentencia = (
        select(PerfilBiometrico)
        .where(PerfilBiometrico.usuario_id == usuario.id)
        .order_by(PerfilBiometrico.fecha_registro.desc(), PerfilBiometrico.id.desc())
        .limit(1)
    )
    perfil = sesion.execute(sentencia).scalar_one_or_none()
    if perfil is None:
        raise PerfilNoRegistrado(usuario.id)
    return perfil


def listar_historial(sesion: Session, usuario: Usuario) -> list[PerfilBiometrico]:
    """Devuelve todas las mediciones del usuario, de la mas reciente a la mas antigua.

    La consulta se filtra por el identificador de la sesion activa, de manera que
    los datos biometricos solo sean visibles para su titular (regla del negocio *f*).
    """
    sentencia = (
        select(PerfilBiometrico)
        .where(PerfilBiometrico.usuario_id == usuario.id)
        .order_by(PerfilBiometrico.fecha_registro.desc(), PerfilBiometrico.id.desc())
    )
    return list(sesion.execute(sentencia).scalars())


def perfil_esta_completo(perfil: PerfilBiometrico | None) -> bool:
    """Indica si el perfil contiene las seis variables que el motor neuronal requiere.

    Los contratos de entrada ya impiden guardar un perfil incompleto; esta
    comprobacion protege ademas frente a registros cargados por otra via.
    """
    if perfil is None:
        return False
    obligatorios = (
        perfil.peso_kg,
        perfil.estatura_cm,
        perfil.edad,
        perfil.sexo,
        perfil.nivel_actividad,
        perfil.objetivo,
    )
    return all(valor is not None for valor in obligatorios)
