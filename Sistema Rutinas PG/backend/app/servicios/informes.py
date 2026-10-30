"""Informes del sistema: consulta en pantalla y exportacion (apartado 6.4).

Hasta ahora cada pantalla dibujaba sus propios datos y solo tres de ellas
podian imprimirse. El usuario no tenia forma de llevarse su avance a otro lugar
—a la consulta con un nutricionista, por ejemplo— y el administrador no podia
sacar del sistema el catalogo que mantiene ni un resumen de su uso.

Este modulo arma cada informe una sola vez, como una tabla con sus columnas
tipadas y un resumen de cifras. La pantalla, el libro de Excel, el archivo CSV
y el documento PDF leen esa misma estructura, de modo que las cifras no pueden
diferir de un formato a otro: si difirieran, el usuario no sabria a cual creer.

Los informes personales leen unicamente los datos de la cuenta que inicio
sesion, por la regla del negocio RN-06 del apartado 4.3.4. Los de
administracion no exponen ningun dato biometrico individual: los indicadores de
uso se entregan agregados y anonimos.
"""

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.esquemas.catalogo import NOMBRES_CATEGORIA
from app.esquemas.plan import AVISO_PROFESIONAL
from app.esquemas.rutina import NOMBRES_GRUPO
from app.modelos.catalogo import Alimento, Ejercicio
from app.modelos.entrenamiento import SesionRealizada
from app.modelos.enumeraciones import (
    NivelActividad,
    NivelExperiencia,
    Objetivo,
    RolUsuario,
    Sexo,
)
from app.modelos.perfil import PerfilBiometrico, RegistroProgreso
from app.modelos.plan import ComidaPlan, Plan, SesionEntrenamiento
from app.modelos.usuario import Usuario
from app.servicios import perfil as servicio_perfil
from app.servicios import plan as servicio_plan
from app.servicios import progreso as servicio_progreso

NOMBRES_OBJETIVO = {
    Objetivo.PERDIDA_GRASA: "Perder grasa",
    Objetivo.MANTENIMIENTO: "Mantener el peso",
    Objetivo.GANANCIA_MUSCULAR: "Ganar músculo",
}

NOMBRES_ACTIVIDAD = {
    NivelActividad.SEDENTARIO: "Sedentario",
    NivelActividad.LIGERO: "Ligero",
    NivelActividad.MODERADO: "Moderado",
    NivelActividad.ALTO: "Alto",
    NivelActividad.MUY_ALTO: "Muy alto",
}

NOMBRES_EXPERIENCIA = {
    NivelExperiencia.PRINCIPIANTE: "Principiante",
    NivelExperiencia.INTERMEDIO: "Intermedio",
    NivelExperiencia.AVANZADO: "Avanzado",
}

NOMBRES_SEXO = {Sexo.MASCULINO: "Masculino", Sexo.FEMENINO: "Femenino"}

NOMBRES_ROL = {
    RolUsuario.USUARIO: "Usuario deportista",
    RolUsuario.ADMINISTRADOR: "Administrador",
}

ORIGENES_DEL_CALCULO = {
    servicio_plan.ORIGEN_RED_NEURONAL: "Red neuronal",
    servicio_plan.ORIGEN_FORMULA: "Fórmula de referencia",
}


class TipoDato(StrEnum):
    """Tipo de una columna: decide cómo se alinea, se formatea y se exporta."""

    TEXTO = "texto"
    ENTERO = "entero"
    DECIMAL = "decimal"
    PORCENTAJE = "porcentaje"
    MONEDA = "moneda"
    FECHA = "fecha"


class Ambito(StrEnum):
    """A quién está destinado un informe."""

    PERSONAL = "personal"
    ADMINISTRACION = "administracion"


@dataclass(frozen=True)
class Columna:
    """Una columna del informe, con el tipo de dato que contiene."""

    clave: str
    titulo: str
    tipo: TipoDato = TipoDato.TEXTO
    decimales: int = 0


@dataclass(frozen=True)
class Indicador:
    """Cifra del resumen, ya redactada para leerse tal cual en cualquier formato."""

    rotulo: str
    valor: str


@dataclass
class Informe:
    """Contenido de un informe, independiente del formato en que se entregue."""

    clave: str
    titulo: str
    descripcion: str
    titular: str
    columnas: list[Columna]
    filas: list[dict]
    resumen: list[Indicador] = field(default_factory=list)
    nota: str | None = None
    generado: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class DefinicionInforme:
    """Entrada del catálogo de informes."""

    clave: str
    titulo: str
    descripcion: str
    ambito: Ambito
    construir: Callable[[Session, Usuario], Informe]


class InformeNoEncontrado(Exception):
    """La clave solicitada no corresponde a ningún informe del catálogo."""


class InformeReservado(Exception):
    """El informe es de administración y la cuenta no tiene ese rol."""


# --------------------------------------------------------------------------
# Formato de las cifras del resumen
# --------------------------------------------------------------------------


def _cifra(valor: float | None, decimales: int = 1, unidad: str = "") -> str:
    """Cifra con separador de millares y su unidad, o un guion si falta."""
    if valor is None:
        return "—"
    texto = f"{valor:,.{decimales}f}"
    return f"{texto} {unidad}".strip()


def _con_signo(valor: float, decimales: int = 1, unidad: str = "") -> str:
    """Cambio con signo explícito: −0.4 kg, +1.2 kg."""
    signo = "+" if valor > 0 else "−" if valor < 0 else ""
    return f"{signo}{abs(valor):,.{decimales}f} {unidad}".strip()


def _fecha(valor: datetime) -> str:
    return valor.strftime("%d/%m/%Y")


def _decimal(valor) -> float | None:
    return float(valor) if valor is not None else None


# --------------------------------------------------------------------------
# Informes personales
# --------------------------------------------------------------------------


def informe_evolucion(sesion: Session, usuario: Usuario) -> Informe:
    """Avance semanal registrado por el usuario (historias HU-09 y HU-10)."""
    registros = servicio_progreso.listar_progreso(sesion, usuario)

    filas = [
        {
            "fecha": registro.fecha_registro.date(),
            "peso_kg": float(registro.peso_kg),
            "perimetro_cintura_cm": _decimal(registro.perimetro_cintura_cm),
            "sesiones_cumplidas": registro.sesiones_cumplidas,
            "adherencia_nutricional": registro.adherencia_nutricional,
        }
        for registro in registros
    ]

    resumen = [Indicador("Semanas registradas", str(len(registros)))]
    if registros:
        inicial = float(registros[0].peso_kg)
        actual = float(registros[-1].peso_kg)
        adherencias = [
            r.adherencia_nutricional for r in registros if r.adherencia_nutricional is not None
        ]
        resumen += [
            Indicador("Peso inicial", _cifra(inicial, 1, "kg")),
            Indicador("Peso actual", _cifra(actual, 1, "kg")),
            Indicador("Cambio total", _con_signo(round(actual - inicial, 1), 1, "kg")),
            Indicador(
                "Sesiones cumplidas",
                str(sum(r.sesiones_cumplidas for r in registros)),
            ),
            Indicador(
                "Adherencia promedio",
                _cifra(sum(adherencias) / len(adherencias), 0, "%") if adherencias else "—",
            ),
        ]

    return Informe(
        clave="evolucion",
        titulo="Evolución del progreso",
        descripcion="Peso, cintura, sesiones y cumplimiento del plan, semana a semana.",
        titular=usuario.nombre,
        columnas=[
            Columna("fecha", "Fecha", TipoDato.FECHA),
            Columna("peso_kg", "Peso (kg)", TipoDato.DECIMAL, 1),
            Columna("perimetro_cintura_cm", "Cintura (cm)", TipoDato.DECIMAL, 1),
            Columna("sesiones_cumplidas", "Sesiones cumplidas", TipoDato.ENTERO),
            Columna("adherencia_nutricional", "Cumplimiento del plan", TipoDato.PORCENTAJE),
        ],
        filas=filas,
        resumen=resumen,
    )


def informe_medidas(sesion: Session, usuario: Usuario) -> Informe:
    """Historial de medidas biométricas, de la más antigua a la vigente (HU-05)."""
    perfiles = list(reversed(servicio_perfil.listar_historial(sesion, usuario)))

    filas = [
        {
            "fecha": perfil.fecha_registro.date(),
            "peso_kg": float(perfil.peso_kg),
            "estatura_cm": float(perfil.estatura_cm),
            "indice_masa_corporal": perfil.indice_masa_corporal,
            "edad": perfil.edad,
            "nivel_actividad": NOMBRES_ACTIVIDAD[perfil.nivel_actividad],
            "objetivo": NOMBRES_OBJETIVO[perfil.objetivo],
            "nivel_experiencia": NOMBRES_EXPERIENCIA[perfil.nivel_experiencia],
            "dias_entrenamiento_semana": perfil.dias_entrenamiento_semana,
        }
        for perfil in perfiles
    ]

    resumen = [Indicador("Mediciones registradas", str(len(perfiles)))]
    if perfiles:
        vigente = perfiles[-1]
        resumen += [
            Indicador("Peso vigente", _cifra(float(vigente.peso_kg), 1, "kg")),
            Indicador("Índice de masa corporal", _cifra(vigente.indice_masa_corporal, 1)),
            Indicador("Objetivo vigente", NOMBRES_OBJETIVO[vigente.objetivo]),
        ]

    return Informe(
        clave="medidas",
        titulo="Historial de medidas biométricas",
        descripcion="Cada actualización del perfil, con el índice de masa corporal calculado.",
        titular=usuario.nombre,
        columnas=[
            Columna("fecha", "Fecha", TipoDato.FECHA),
            Columna("peso_kg", "Peso (kg)", TipoDato.DECIMAL, 1),
            Columna("estatura_cm", "Estatura (cm)", TipoDato.DECIMAL, 1),
            Columna("indice_masa_corporal", "IMC", TipoDato.DECIMAL, 1),
            Columna("edad", "Edad", TipoDato.ENTERO),
            Columna("nivel_actividad", "Actividad"),
            Columna("objetivo", "Objetivo"),
            Columna("nivel_experiencia", "Experiencia"),
            Columna("dias_entrenamiento_semana", "Días por semana", TipoDato.ENTERO),
        ],
        filas=filas,
        resumen=resumen,
    )


def informe_plan(sesion: Session, usuario: Usuario) -> Informe:
    """Plan nutricional vigente, desglosado por tiempo de comida (HU-06 y HU-08)."""
    plan = servicio_plan.obtener_plan_vigente(sesion, usuario)

    filas: list[dict] = []
    resumen: list[Indicador] = []
    if plan is not None:
        porciones = sesion.execute(
            select(ComidaPlan, Alimento)
            .join(Alimento, ComidaPlan.alimento_id == Alimento.id)
            .where(ComidaPlan.plan_id == plan.id)
            .order_by(ComidaPlan.id)
        ).all()
        for porcion, alimento in porciones:
            gramos = float(porcion.cantidad_g)
            factor = gramos / 100
            filas.append(
                {
                    "tiempo_comida": porcion.tiempo_comida,
                    "alimento": alimento.nombre,
                    "gramos": round(gramos),
                    "energia_kcal": round(float(alimento.energia_kcal_100g) * factor),
                    "proteina_g": round(float(alimento.proteina_g_100g) * factor, 1),
                    "carbohidrato_g": round(float(alimento.carbohidrato_g_100g) * factor, 1),
                    "grasa_g": round(float(alimento.grasa_g_100g) * factor, 1),
                }
            )
        resumen = [
            Indicador("Energía diaria", _cifra(float(plan.calorias_objetivo), 0, "kcal")),
            Indicador("Proteína", _cifra(float(plan.proteina_g), 0, "g")),
            Indicador("Carbohidrato", _cifra(float(plan.carbohidrato_g), 0, "g")),
            Indicador("Grasa", _cifra(float(plan.grasa_g), 0, "g")),
            Indicador(
                "Margen frente a las fórmulas",
                _cifra(float(plan.margen_error_porcentaje), 2, "%"),
            ),
            Indicador(
                "Origen del cálculo",
                ORIGENES_DEL_CALCULO.get(plan.origen_calculo, plan.origen_calculo),
            ),
            Indicador("Generado el", _fecha(plan.fecha_generacion)),
        ]

    return Informe(
        clave="plan",
        titulo="Plan nutricional vigente",
        descripcion="Porciones del menú diario con su aporte de energía y macronutrientes.",
        titular=usuario.nombre,
        columnas=[
            Columna("tiempo_comida", "Tiempo de comida"),
            Columna("alimento", "Alimento"),
            Columna("gramos", "Cantidad (g)", TipoDato.ENTERO),
            Columna("energia_kcal", "Energía (kcal)", TipoDato.ENTERO),
            Columna("proteina_g", "Proteína (g)", TipoDato.DECIMAL, 1),
            Columna("carbohidrato_g", "Carbohidrato (g)", TipoDato.DECIMAL, 1),
            Columna("grasa_g", "Grasa (g)", TipoDato.DECIMAL, 1),
        ],
        filas=filas,
        resumen=resumen,
        # Regla del negocio RN-05: todo plan se entrega con el aviso de consulta
        # profesional, y un informe impreso es justamente el que circula fuera
        # del sistema, donde la pantalla ya no puede mostrarlo.
        nota=AVISO_PROFESIONAL,
    )


def informe_entrenamiento(sesion: Session, usuario: Usuario) -> Informe:
    """Bitácora de las sesiones de entrenamiento realizadas."""
    realizadas = list(
        sesion.execute(
            select(SesionRealizada)
            .where(SesionRealizada.usuario_id == usuario.id)
            .options(selectinload(SesionRealizada.series))
            .order_by(SesionRealizada.fecha, SesionRealizada.id)
        ).scalars()
    )

    grupos: dict[int, str] = {}
    identificadores = {r.sesion_id for r in realizadas if r.sesion_id is not None}
    if identificadores:
        for prescrita in sesion.execute(
            select(SesionEntrenamiento).where(SesionEntrenamiento.id.in_(identificadores))
        ).scalars():
            grupos[prescrita.id] = NOMBRES_GRUPO[prescrita.grupo_muscular]

    filas = [
        {
            "fecha": realizada.fecha,
            "sesion": grupos.get(realizada.sesion_id, "Sesión libre"),
            "series": realizada.series_totales,
            "repeticiones": realizada.repeticiones_totales,
            "volumen_kg": realizada.volumen_kg,
            "duracion_minutos": realizada.duracion_minutos,
            "percepcion_esfuerzo": realizada.percepcion_esfuerzo,
        }
        for realizada in realizadas
    ]

    resumen = [Indicador("Sesiones registradas", str(len(realizadas)))]
    if realizadas:
        resumen += [
            Indicador("Series totales", str(sum(r.series_totales for r in realizadas))),
            Indicador(
                "Volumen total levantado",
                _cifra(sum(r.volumen_kg for r in realizadas), 0, "kg"),
            ),
        ]

    return Informe(
        clave="entrenamiento",
        titulo="Bitácora de entrenamiento",
        descripcion="Sesiones realizadas, con sus series, repeticiones y volumen de carga.",
        titular=usuario.nombre,
        columnas=[
            Columna("fecha", "Fecha", TipoDato.FECHA),
            Columna("sesion", "Sesión"),
            Columna("series", "Series", TipoDato.ENTERO),
            Columna("repeticiones", "Repeticiones", TipoDato.ENTERO),
            Columna("volumen_kg", "Volumen (kg)", TipoDato.DECIMAL, 1),
            Columna("duracion_minutos", "Duración (min)", TipoDato.ENTERO),
            Columna("percepcion_esfuerzo", "Esfuerzo (1 a 10)", TipoDato.ENTERO),
        ],
        filas=filas,
        resumen=resumen,
    )


# --------------------------------------------------------------------------
# Informes de administración
# --------------------------------------------------------------------------


def informe_cuentas(sesion: Session, usuario: Usuario) -> Informe:
    """Cuentas registradas, con su rol y su estado (historia HU-03)."""
    cuentas = list(sesion.execute(select(Usuario).order_by(Usuario.fecha_registro)).scalars())

    filas = [
        {
            "nombre": cuenta.nombre,
            "correo": cuenta.correo,
            "rol": NOMBRES_ROL[cuenta.rol],
            "estado": "Activa" if cuenta.activo else "Desactivada",
            "fecha_registro": cuenta.fecha_registro.date(),
            "ultimo_acceso": cuenta.ultimo_acceso.date() if cuenta.ultimo_acceso else None,
        }
        for cuenta in cuentas
    ]

    return Informe(
        clave="cuentas",
        titulo="Cuentas registradas",
        descripcion="Cuentas del sistema con su rol, su estado y su último acceso.",
        titular=usuario.nombre,
        columnas=[
            Columna("nombre", "Nombre"),
            Columna("correo", "Correo"),
            Columna("rol", "Rol"),
            Columna("estado", "Estado"),
            Columna("fecha_registro", "Registro", TipoDato.FECHA),
            Columna("ultimo_acceso", "Último acceso", TipoDato.FECHA),
        ],
        filas=filas,
        resumen=[
            Indicador("Cuentas registradas", str(len(cuentas))),
            Indicador("Activas", str(sum(1 for c in cuentas if c.activo))),
            Indicador(
                "Administradores",
                str(sum(1 for c in cuentas if c.rol == RolUsuario.ADMINISTRADOR)),
            ),
        ],
    )


def informe_alimentos(sesion: Session, usuario: Usuario) -> Informe:
    """Catálogo local de alimentos con su aporte y su costo (historia HU-11)."""
    alimentos = list(
        sesion.execute(select(Alimento).order_by(Alimento.categoria, Alimento.nombre)).scalars()
    )

    filas = [
        {
            "nombre": alimento.nombre,
            "categoria": NOMBRES_CATEGORIA[alimento.categoria],
            "energia_kcal_100g": float(alimento.energia_kcal_100g),
            "proteina_g_100g": float(alimento.proteina_g_100g),
            "carbohidrato_g_100g": float(alimento.carbohidrato_g_100g),
            "grasa_g_100g": float(alimento.grasa_g_100g),
            "costo_aproximado_quetzales": _decimal(alimento.costo_aproximado_quetzales),
            "disponible": "Sí" if alimento.disponible_localmente else "No",
        }
        for alimento in alimentos
    ]

    return Informe(
        clave="alimentos",
        titulo="Catálogo de alimentos",
        descripcion="Aporte nutricional por cada 100 gramos y costo aproximado en el mercado local.",
        titular=usuario.nombre,
        columnas=[
            Columna("nombre", "Alimento"),
            Columna("categoria", "Categoría"),
            Columna("energia_kcal_100g", "Energía (kcal)", TipoDato.DECIMAL, 0),
            Columna("proteina_g_100g", "Proteína (g)", TipoDato.DECIMAL, 1),
            Columna("carbohidrato_g_100g", "Carbohidrato (g)", TipoDato.DECIMAL, 1),
            Columna("grasa_g_100g", "Grasa (g)", TipoDato.DECIMAL, 1),
            Columna("costo_aproximado_quetzales", "Costo (Q)", TipoDato.MONEDA, 2),
            Columna("disponible", "Disponible"),
        ],
        filas=filas,
        resumen=[
            Indicador("Alimentos en el catálogo", str(len(alimentos))),
            Indicador(
                "Disponibles en el municipio",
                str(sum(1 for a in alimentos if a.disponible_localmente)),
            ),
        ],
    )


def informe_ejercicios(sesion: Session, usuario: Usuario) -> Informe:
    """Catálogo de ejercicios con el equipamiento que requieren (historia HU-11)."""
    ejercicios = list(
        sesion.execute(
            select(Ejercicio).order_by(Ejercicio.grupo_muscular, Ejercicio.nombre)
        ).scalars()
    )

    filas = [
        {
            "nombre": ejercicio.nombre,
            "grupo_muscular": NOMBRES_GRUPO[ejercicio.grupo_muscular],
            "nivel_minimo": NOMBRES_EXPERIENCIA[ejercicio.nivel_minimo],
            "equipamiento": ejercicio.equipamiento,
            "tipo": "Compuesto" if ejercicio.es_compuesto else "Aislado",
            "disponible": "Sí" if ejercicio.disponible_localmente else "No",
        }
        for ejercicio in ejercicios
    ]

    return Informe(
        clave="ejercicios",
        titulo="Catálogo de ejercicios",
        descripcion="Ejercicios ejecutables con el equipamiento registrado del gimnasio.",
        titular=usuario.nombre,
        columnas=[
            Columna("nombre", "Ejercicio"),
            Columna("grupo_muscular", "Grupo muscular"),
            Columna("nivel_minimo", "Nivel mínimo"),
            Columna("equipamiento", "Equipamiento"),
            Columna("tipo", "Tipo"),
            Columna("disponible", "Disponible"),
        ],
        filas=filas,
        resumen=[
            Indicador("Ejercicios en el catálogo", str(len(ejercicios))),
            Indicador(
                "Disponibles en el gimnasio",
                str(sum(1 for e in ejercicios if e.disponible_localmente)),
            ),
        ],
    )


def informe_indicadores(sesion: Session, usuario: Usuario) -> Informe:
    """Indicadores de uso agregados y anónimos (regla del negocio RN-06).

    El administrador necesita saber cómo se usa el sistema —cuántos planes se
    generan, qué objetivos persiguen los usuarios, qué tanto cumplen—, pero la
    regla RN-06 le prohíbe ver los datos biométricos de una persona. Por eso
    cada fila es un conteo o un promedio sobre todas las cuentas, nunca un
    registro individual.
    """

    def contar(entidad) -> int:
        return sesion.execute(select(func.count()).select_from(entidad)).scalar_one()

    cuentas_deportistas = sesion.execute(
        select(func.count()).select_from(Usuario).where(Usuario.rol == RolUsuario.USUARIO)
    ).scalar_one()
    con_perfil = sesion.execute(
        select(func.count(func.distinct(PerfilBiometrico.usuario_id)))
    ).scalar_one()
    con_plan = sesion.execute(
        select(func.count(func.distinct(Plan.usuario_id))).where(Plan.activo.is_(True))
    ).scalar_one()
    adherencia = sesion.execute(
        select(func.avg(RegistroProgreso.adherencia_nutricional))
    ).scalar_one()
    margen = sesion.execute(
        select(func.avg(Plan.margen_error_porcentaje)).where(Plan.activo.is_(True))
    ).scalar_one()

    # El objetivo de cada usuario es el de su medición más reciente.
    ultimas = (
        select(PerfilBiometrico.usuario_id, func.max(PerfilBiometrico.id).label("ultimo"))
        .group_by(PerfilBiometrico.usuario_id)
        .subquery()
    )
    objetivos = Counter(
        sesion.execute(
            select(PerfilBiometrico.objetivo).join(
                ultimas, PerfilBiometrico.id == ultimas.c.ultimo
            )
        ).scalars()
    )

    filas = [
        {"indicador": "Cuentas de usuario deportista", "valor": cuentas_deportistas},
        {"indicador": "Usuarios con perfil biométrico", "valor": con_perfil},
        {"indicador": "Usuarios con plan vigente", "valor": con_plan},
        {"indicador": "Planes generados en total", "valor": contar(Plan)},
        {"indicador": "Registros de avance semanal", "valor": contar(RegistroProgreso)},
        {"indicador": "Sesiones de entrenamiento registradas", "valor": contar(SesionRealizada)},
    ]
    filas += [
        {"indicador": f"Usuarios con objetivo «{nombre}»", "valor": objetivos.get(objetivo, 0)}
        for objetivo, nombre in NOMBRES_OBJETIVO.items()
    ]

    return Informe(
        clave="indicadores",
        titulo="Indicadores de uso",
        descripcion="Conteos y promedios sobre todas las cuentas; ningún dato individual.",
        titular=usuario.nombre,
        columnas=[
            Columna("indicador", "Indicador"),
            Columna("valor", "Valor", TipoDato.ENTERO),
        ],
        filas=filas,
        resumen=[
            Indicador(
                "Adherencia promedio",
                _cifra(float(adherencia), 0, "%") if adherencia is not None else "—",
            ),
            Indicador(
                "Margen medio frente a las fórmulas",
                _cifra(float(margen), 2, "%") if margen is not None else "—",
            ),
        ],
        nota=(
            "Información agregada y anónima, conforme a la regla del negocio RN-06: "
            "el informe no contiene datos biométricos de ninguna persona."
        ),
    )


# --------------------------------------------------------------------------
# Catálogo
# --------------------------------------------------------------------------

_DEFINICIONES = (
    DefinicionInforme(
        "evolucion",
        "Evolución del progreso",
        "Su avance semana a semana: peso, cintura, sesiones y cumplimiento.",
        Ambito.PERSONAL,
        informe_evolucion,
    ),
    DefinicionInforme(
        "plan",
        "Plan nutricional vigente",
        "Su menú diario con la energía y los macronutrientes de cada porción.",
        Ambito.PERSONAL,
        informe_plan,
    ),
    DefinicionInforme(
        "medidas",
        "Historial de medidas",
        "Cada actualización de su perfil biométrico, con su índice de masa corporal.",
        Ambito.PERSONAL,
        informe_medidas,
    ),
    DefinicionInforme(
        "entrenamiento",
        "Bitácora de entrenamiento",
        "Las sesiones que ha registrado, con sus series y su volumen de carga.",
        Ambito.PERSONAL,
        informe_entrenamiento,
    ),
    DefinicionInforme(
        "indicadores",
        "Indicadores de uso",
        "Cifras agregadas y anónimas sobre el uso del sistema.",
        Ambito.ADMINISTRACION,
        informe_indicadores,
    ),
    DefinicionInforme(
        "cuentas",
        "Cuentas registradas",
        "Cuentas del sistema con su rol, su estado y su último acceso.",
        Ambito.ADMINISTRACION,
        informe_cuentas,
    ),
    DefinicionInforme(
        "alimentos",
        "Catálogo de alimentos",
        "Aporte nutricional y costo de los alimentos del mercado local.",
        Ambito.ADMINISTRACION,
        informe_alimentos,
    ),
    DefinicionInforme(
        "ejercicios",
        "Catálogo de ejercicios",
        "Ejercicios del gimnasio con su grupo muscular y su equipamiento.",
        Ambito.ADMINISTRACION,
        informe_ejercicios,
    ),
)

CATALOGO_INFORMES: dict[str, DefinicionInforme] = {d.clave: d for d in _DEFINICIONES}


def informes_disponibles(usuario: Usuario) -> list[DefinicionInforme]:
    """Informes que la cuenta puede consultar, según su rol."""
    return [
        definicion
        for definicion in _DEFINICIONES
        if definicion.ambito == Ambito.PERSONAL or usuario.es_administrador
    ]


def construir_informe(sesion: Session, usuario: Usuario, clave: str) -> Informe:
    """Arma el informe solicitado, con la verificación de rol en el servidor."""
    definicion = CATALOGO_INFORMES.get(clave)
    if definicion is None:
        raise InformeNoEncontrado(clave)
    if definicion.ambito == Ambito.ADMINISTRACION and not usuario.es_administrador:
        raise InformeReservado(clave)
    return definicion.construir(sesion, usuario)
