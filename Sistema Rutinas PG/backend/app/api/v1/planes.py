"""Controlador del plan nutricional (historia HU-06, subfase 3.3).

Igual que el perfil biometrico, todas las rutas operan sobre la cuenta que inicio
sesion: no existe forma de consultar el plan de otra persona.
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.dependencias import SesionBD, UsuarioAutenticado
from app.esquemas.compras import (
    DIAS_DE_LA_SEMANA,
    GrupoDeCompra,
    ListaDeCompras,
    RenglonDeCompra,
)
from app.esquemas.menu import (
    MenuPublico,
    PorcionPublica,
    SustitutoPublico,
    TiempoComidaPublico,
)
from app.esquemas.plan import PlanNutricionalPublico
from app.modelos.catalogo import Alimento
from app.modelos.enumeraciones import CategoriaAlimento
from app.modelos.perfil import PerfilBiometrico
from app.modelos.plan import ComidaPlan, Plan
from app.motor.menu import TIEMPOS_DE_COMIDA, AlimentoDisponible, buscar_sustituto
from app.servicios import plan as servicio_plan

enrutador = APIRouter(prefix="/plan-nutricional", tags=["Plan nutricional"])

_PERFIL_INCOMPLETO = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail=(
        "No es posible generar su plan porque su perfil biométrico está incompleto. "
        "Registre sus medidas para continuar."
    ),
)

_SIN_PLAN = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Todavía no tiene un plan generado.",
)


def _componer(sesion: SesionBD, plan: Plan) -> PlanNutricionalPublico:
    """Agrega al plan almacenado los datos derivados del perfil que lo origino."""
    perfil = sesion.get(PerfilBiometrico, plan.perfil_id)
    correcciones, advertencias = servicio_plan.notas_de_seguridad(perfil, plan)
    return PlanNutricionalPublico(
        id=plan.id,
        usuario_id=plan.usuario_id,
        perfil_id=plan.perfil_id,
        fecha_generacion=plan.fecha_generacion,
        activo=plan.activo,
        tasa_metabolica_basal=float(plan.tasa_metabolica_basal),
        gasto_energetico_total=float(plan.gasto_energetico_total),
        calorias_objetivo=float(plan.calorias_objetivo),
        referencia_mifflin=float(plan.referencia_mifflin),
        referencia_harris_benedict=float(plan.referencia_harris_benedict),
        margen_error_porcentaje=float(plan.margen_error_porcentaje),
        origen_calculo=plan.origen_calculo,
        proteina_g=float(plan.proteina_g),
        carbohidrato_g=float(plan.carbohidrato_g),
        grasa_g=float(plan.grasa_g),
        agua_ml=servicio_plan.agua_recomendada(perfil),
        objetivo=perfil.objetivo.value,
        explicacion_objetivo=servicio_plan.explicacion_objetivo(perfil),
        correcciones_de_seguridad=correcciones,
        advertencias_de_salud=advertencias,
    )


@enrutador.post(
    "",
    response_model=PlanNutricionalPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Generar el plan nutricional",
)
def generar(sesion: SesionBD, usuario: UsuarioAutenticado) -> PlanNutricionalPublico:
    """Calcula el plan a partir del perfil biométrico vigente (historia HU-06).

    El plan anterior deja de estar vigente pero se conserva en el historial.
    """
    try:
        plan = servicio_plan.generar_plan(sesion, usuario)
    except servicio_plan.PerfilIncompleto:
        raise _PERFIL_INCOMPLETO from None
    return _componer(sesion, plan)


@enrutador.get(
    "",
    response_model=PlanNutricionalPublico,
    summary="Consultar el plan nutricional vigente",
)
def consultar_vigente(sesion: SesionBD, usuario: UsuarioAutenticado) -> PlanNutricionalPublico:
    """Devuelve el plan activo de la cuenta en sesión."""
    plan = servicio_plan.obtener_plan_vigente(sesion, usuario)
    if plan is None:
        raise _SIN_PLAN
    return _componer(sesion, plan)


@enrutador.get(
    "/historial",
    response_model=list[PlanNutricionalPublico],
    summary="Consultar el historial de planes",
)
def consultar_historial(
    sesion: SesionBD, usuario: UsuarioAutenticado
) -> list[PlanNutricionalPublico]:
    """Devuelve los planes del usuario, del más reciente al más antiguo.

    Conservarlos permite comparar el plan inicial con el vigente (historia HU-10).
    """
    return [_componer(sesion, plan) for plan in servicio_plan.listar_planes(sesion, usuario)]


@enrutador.get(
    "/menu",
    response_model=MenuPublico,
    summary="Consultar el menu diario del plan vigente",
)
def consultar_menu(sesion: SesionBD, usuario: UsuarioAutenticado) -> MenuPublico:
    """Devuelve el reparto del plan en tiempos de comida (historia HU-08).

    El menu se arma al generar el plan y se guarda con el. Aqui se reconstruye
    a partir de esas porciones almacenadas, y se le anaden los sustitutos, que
    se calculan sobre el catalogo vigente en el momento de la consulta: si un
    alimento dejo de conseguirse despues de generado el plan, la alternativa que
    se ofrece ya toma en cuenta esa baja.
    """
    plan = servicio_plan.obtener_plan_vigente(sesion, usuario)
    if plan is None:
        raise _SIN_PLAN

    porciones_guardadas = list(
        sesion.execute(
            select(ComidaPlan)
            .where(ComidaPlan.plan_id == plan.id)
            .order_by(ComidaPlan.id)
        ).scalars()
    )
    if not porciones_guardadas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Su plan no tiene menú. El catálogo de alimentos no tenía suficientes "
                "opciones cuando se generó; vuelva a generar su plan."
            ),
        )

    disponibles = servicio_plan.alimentos_disponibles(sesion)
    por_identificador = {alimento.id: alimento for alimento in disponibles}

    tiempos: dict[str, list[PorcionPublica]] = {}
    for guardada in porciones_guardadas:
        alimento = por_identificador.get(guardada.alimento_id)
        if alimento is None:
            # El alimento se dio de baja despues de generar el plan. Se conserva
            # la porcion con los datos del catalogo para no perder el registro.
            registro = sesion.get(Alimento, guardada.alimento_id)
            if registro is None:
                continue
            alimento = AlimentoDisponible(
                id=registro.id,
                nombre=registro.nombre,
                categoria=registro.categoria,
                energia_kcal_100g=float(registro.energia_kcal_100g),
                proteina_g_100g=float(registro.proteina_g_100g),
                carbohidrato_g_100g=float(registro.carbohidrato_g_100g),
                grasa_g_100g=float(registro.grasa_g_100g),
                medida_casera=registro.medida_casera,
                costo_quetzales_100g=(
                    float(registro.costo_aproximado_quetzales)
                    if registro.costo_aproximado_quetzales is not None
                    else None
                ),
            )

        gramos = int(guardada.cantidad_g)
        alternativa = buscar_sustituto(alimento, gramos, disponibles)
        tiempos.setdefault(guardada.tiempo_comida, []).append(
            PorcionPublica(
                alimento_id=alimento.id,
                nombre=alimento.nombre,
                categoria=alimento.categoria,
                gramos=gramos,
                energia_kcal=round(alimento.energia_de(gramos)),
                proteina_g=round(alimento.proteina_de(gramos)),
                carbohidrato_g=round(alimento.carbohidrato_de(gramos)),
                grasa_g=round(alimento.grasa_de(gramos)),
                medida_casera=alimento.medida_casera,
                costo_quetzales=alimento.costo_de(gramos),
                sustituto=(
                    SustitutoPublico(
                        alimento_id=alternativa.alimento_id,
                        nombre=alternativa.nombre,
                        gramos=alternativa.gramos,
                        medida_casera=alternativa.medida_casera,
                    )
                    if alternativa is not None
                    else None
                ),
            )
        )

    # Se respeta el orden natural de los tiempos de comida del dia.
    ordenados = [
        TiempoComidaPublico(nombre=nombre, porciones=tiempos[nombre])
        for nombre, _ in TIEMPOS_DE_COMIDA
        if nombre in tiempos
    ]

    return MenuPublico(
        plan_id=plan.id,
        fecha_generacion=plan.fecha_generacion,
        activo=plan.activo,
        energia_objetivo_kcal=float(plan.calorias_objetivo),
        proteina_objetivo_g=float(plan.proteina_g),
        tiempos=ordenados,
    )


@enrutador.get(
    "/lista-de-compras",
    response_model=ListaDeCompras,
    summary="Consultar la lista de compras de la semana",
)
def consultar_lista_de_compras(
    sesion: SesionBD, usuario: UsuarioAutenticado
) -> ListaDeCompras:
    """Suma el menú de un día por siete y lo agrupa por puesto de mercado.

    No corresponde a ninguna historia de la pila de producto. Se agrega porque
    el menú diario dice qué comer en cada tiempo, pero para surtir la despensa
    hace falta la suma de la semana, agrupada por el lugar donde cada cosa se
    compra y con el costo a la vista antes de salir de casa.
    """
    plan = servicio_plan.obtener_plan_vigente(sesion, usuario)
    if plan is None:
        raise _SIN_PLAN

    porciones = list(
        sesion.execute(
            select(ComidaPlan).where(ComidaPlan.plan_id == plan.id)
        ).scalars()
    )
    if not porciones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Su plan no tiene menú, de modo que no hay lista de compras que armar. "
                "Vuelva a generar su plan."
            ),
        )

    # Se acumulan los gramos de cada alimento a lo largo del día y se multiplican
    # por los días de la semana.
    gramos_por_alimento: dict[int, int] = {}
    for porcion in porciones:
        gramos_por_alimento[porcion.alimento_id] = (
            gramos_por_alimento.get(porcion.alimento_id, 0) + int(porcion.cantidad_g)
        )

    por_categoria: dict[CategoriaAlimento, list[RenglonDeCompra]] = {}
    for alimento_id, gramos_dia in gramos_por_alimento.items():
        registro = sesion.get(Alimento, alimento_id)
        if registro is None:
            continue

        gramos_semana = gramos_dia * DIAS_DE_LA_SEMANA
        costo = (
            round(float(registro.costo_aproximado_quetzales) * gramos_semana / 100, 2)
            if registro.costo_aproximado_quetzales is not None
            else None
        )
        por_categoria.setdefault(registro.categoria, []).append(
            RenglonDeCompra(
                alimento_id=registro.id,
                nombre=registro.nombre,
                categoria=registro.categoria,
                gramos_semana=gramos_semana,
                costo_quetzales=costo,
                medida_casera=registro.medida_casera,
            )
        )

    # Se recorre la enumeracion y no el diccionario para que el orden de los
    # grupos sea siempre el mismo, cualquiera que sea el plan.
    grupos = [
        GrupoDeCompra(
            categoria=categoria,
            renglones=sorted(por_categoria[categoria], key=lambda r: r.nombre),
        )
        for categoria in CategoriaAlimento
        if categoria in por_categoria
    ]

    return ListaDeCompras(
        plan_id=plan.id,
        fecha_generacion=plan.fecha_generacion,
        dias=DIAS_DE_LA_SEMANA,
        grupos=grupos,
    )
