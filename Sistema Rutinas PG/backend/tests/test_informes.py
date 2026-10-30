"""Pruebas funcionales de los informes (apartado 6.4 de la tesis).

Verifican las cinco formas de obtener un informe que el apartado exige —en
pantalla, en Excel, en CSV, en PDF y para imprimir— y que todas entregan las
mismas cifras. Verifican además el control de acceso: los informes personales
solo leen los datos de su titular (regla RN-06) y los de administración están
reservados a ese rol, comprobado en el servidor (requerimiento 4.5.1).
"""

import csv
import io
import re
import zipfile
from datetime import date, timedelta

import pytest
from openpyxl import load_workbook

from app.servicios import exportacion
from app.servicios.informes import Columna, Indicador, Informe, TipoDato
from tests.conftest import encabezado

RUTA_INFORMES = "/api/v1/informes"

PERFIL = {
    "peso_kg": 82.0,
    "estatura_cm": 176.0,
    "edad": 30,
    "sexo": "masculino",
    "nivel_actividad": "moderado",
    "objetivo": "perdida_grasa",
    "nivel_experiencia": "intermedio",
    "dias_entrenamiento_semana": 4,
}

AVANCES = [
    {"peso_kg": 81.4, "perimetro_cintura_cm": 91.0, "sesiones_cumplidas": 4, "adherencia_nutricional": 85},
    {"peso_kg": 80.6, "perimetro_cintura_cm": 90.2, "sesiones_cumplidas": 3, "adherencia_nutricional": 75},
]


@pytest.fixture(name="con_avance")
def fixture_con_avance(cliente, token_usuario):
    """Usuario con perfil, plan y dos semanas de avance registradas."""
    cabecera = encabezado(token_usuario)
    assert cliente.post("/api/v1/perfil-biometrico", json=PERFIL, headers=cabecera).status_code == 201
    assert cliente.post("/api/v1/plan-nutricional", headers=cabecera).status_code == 201
    for semanas_atras, avance in zip((2, 1), AVANCES, strict=True):
        fecha = (date.today() - timedelta(weeks=semanas_atras)).isoformat()
        respuesta = cliente.post(
            "/api/v1/progreso", json={**avance, "fecha_registro": fecha}, headers=cabecera
        )
        assert respuesta.status_code == 201, respuesta.text
    return token_usuario


def descargar(cliente, token, clave, formato):
    return cliente.get(f"{RUTA_INFORMES}/{clave}/{formato}", headers=encabezado(token))


# --------------------------------------------------------------------------
# Catálogo y control de acceso
# --------------------------------------------------------------------------


def test_sin_sesion_no_se_consulta_ni_se_descarga_ningun_informe(cliente):
    assert cliente.get(RUTA_INFORMES).status_code == 401
    assert cliente.get(f"{RUTA_INFORMES}/evolucion").status_code == 401
    assert cliente.get(f"{RUTA_INFORMES}/evolucion/pdf").status_code == 401


def test_el_deportista_solo_ve_sus_informes_personales(cliente, token_usuario):
    respuesta = cliente.get(RUTA_INFORMES, headers=encabezado(token_usuario))

    assert respuesta.status_code == 200
    claves = {informe["clave"] for informe in respuesta.json()}
    assert claves == {"evolucion", "plan", "medidas", "entrenamiento"}
    assert all(informe["ambito"] == "personal" for informe in respuesta.json())


def test_el_administrador_ve_tambien_los_informes_de_administracion(
    cliente, token_administrador
):
    respuesta = cliente.get(RUTA_INFORMES, headers=encabezado(token_administrador))

    claves = {informe["clave"] for informe in respuesta.json()}
    assert {"indicadores", "cuentas", "alimentos", "ejercicios"} <= claves
    assert all(informe["formatos"] == ["csv", "xlsx", "pdf"] for informe in respuesta.json())


@pytest.mark.parametrize("clave", ["indicadores", "cuentas", "alimentos", "ejercicios"])
def test_un_deportista_no_obtiene_informes_de_administracion(cliente, token_usuario, clave):
    """El rol se comprueba en el servidor, no solo ocultando el botón."""
    assert cliente.get(f"{RUTA_INFORMES}/{clave}", headers=encabezado(token_usuario)).status_code == 403
    assert descargar(cliente, token_usuario, clave, "xlsx").status_code == 403


def test_un_informe_inexistente_devuelve_no_encontrado(cliente, token_usuario):
    assert cliente.get(f"{RUTA_INFORMES}/inventado", headers=encabezado(token_usuario)).status_code == 404


def test_un_formato_no_admitido_se_rechaza(cliente, token_usuario):
    assert descargar(cliente, token_usuario, "evolucion", "docx").status_code == 422


def test_cada_cuenta_solo_lee_su_propio_avance(cliente, con_avance, token_segundo_usuario):
    """Regla RN-06: los datos biométricos solo son visibles para su titular."""
    ajeno = cliente.get(f"{RUTA_INFORMES}/evolucion", headers=encabezado(token_segundo_usuario))

    assert ajeno.status_code == 200
    assert ajeno.json()["filas"] == []
    assert ajeno.json()["titular"] == "Otro deportista"


# --------------------------------------------------------------------------
# 6.4.1 Informe en pantalla
# --------------------------------------------------------------------------


def test_el_informe_en_pantalla_trae_columnas_filas_y_resumen(cliente, con_avance):
    respuesta = cliente.get(f"{RUTA_INFORMES}/evolucion", headers=encabezado(con_avance))

    assert respuesta.status_code == 200
    informe = respuesta.json()
    assert informe["titulo"] == "Evolución del progreso"
    assert [c["clave"] for c in informe["columnas"]] == [
        "fecha",
        "peso_kg",
        "perimetro_cintura_cm",
        "sesiones_cumplidas",
        "adherencia_nutricional",
    ]
    assert [fila["peso_kg"] for fila in informe["filas"]] == [81.4, 80.6]
    resumen = {indicador["rotulo"]: indicador["valor"] for indicador in informe["resumen"]}
    assert resumen["Semanas registradas"] == "2"
    assert resumen["Cambio total"] == "−0.8 kg"
    assert resumen["Sesiones cumplidas"] == "7"
    assert resumen["Adherencia promedio"] == "80 %"


def test_el_informe_del_plan_cuadra_con_el_plan_vigente(cliente, con_avance):
    cabecera = encabezado(con_avance)
    plan = cliente.get("/api/v1/plan-nutricional", headers=cabecera).json()
    informe = cliente.get(f"{RUTA_INFORMES}/plan", headers=cabecera).json()

    assert informe["filas"], "el plan debe traer su menú"
    energia_del_menu = sum(fila["energia_kcal"] for fila in informe["filas"])
    # El menú se arma con porciones servibles: su energía queda cerca de la que
    # el plan prescribe (apartado 4.6 del PLAN de desarrollo), no idéntica.
    assert abs(energia_del_menu - plan["calorias_objetivo"]) / plan["calorias_objetivo"] < 0.10
    assert "profesional de la salud" in informe["nota"]


def test_un_informe_sin_registros_se_entrega_vacio_y_no_falla(cliente, token_usuario):
    for clave in ("evolucion", "plan", "medidas", "entrenamiento"):
        respuesta = cliente.get(f"{RUTA_INFORMES}/{clave}", headers=encabezado(token_usuario))
        assert respuesta.status_code == 200, clave
        assert respuesta.json()["filas"] == []


def test_los_indicadores_de_uso_son_agregados_y_anonimos(
    cliente, con_avance, token_administrador
):
    """Regla RN-06: el administrador ve conteos, nunca datos de una persona."""
    informe = cliente.get(
        f"{RUTA_INFORMES}/indicadores", headers=encabezado(token_administrador)
    ).json()

    assert [c["clave"] for c in informe["columnas"]] == ["indicador", "valor"]
    valores = {fila["indicador"]: fila["valor"] for fila in informe["filas"]}
    assert valores["Usuarios con perfil biométrico"] == 1
    assert valores["Registros de avance semanal"] == 2
    assert valores["Usuarios con objetivo «Perder grasa»"] == 1
    texto = str(informe)
    assert "82.0" not in texto and "deportista.pruebas" not in texto


# --------------------------------------------------------------------------
# 6.4.2 Excel
# --------------------------------------------------------------------------


def test_el_excel_guarda_cifras_como_numeros_y_fechas_como_fechas(cliente, con_avance):
    respuesta = descargar(cliente, con_avance, "evolucion", "xlsx")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    libro = load_workbook(io.BytesIO(respuesta.content))
    assert libro.sheetnames == ["Datos", "Resumen"]
    hoja = libro["Datos"]
    assert hoja["A1"].value == "Evolución del progreso"
    assert [celda.value for celda in hoja[5]] == [
        "Fecha",
        "Peso (kg)",
        "Cintura (cm)",
        "Sesiones cumplidas",
        "Cumplimiento del plan",
    ]
    assert hoja["B6"].value == 81.4 and hoja["B7"].value == 80.6
    assert hoja["A6"].is_date
    assert hoja.freeze_panes == "A6"


def test_el_catalogo_de_alimentos_se_exporta_completo(cliente, token_administrador):
    cabecera = encabezado(token_administrador)
    alimentos = cliente.get("/api/v1/catalogos/alimentos", headers=cabecera).json()
    respuesta = descargar(cliente, token_administrador, "alimentos", "xlsx")

    hoja = load_workbook(io.BytesIO(respuesta.content))["Datos"]
    assert hoja.max_row - 5 == len(alimentos)


# --------------------------------------------------------------------------
# 6.4.3 CSV
# --------------------------------------------------------------------------


def test_el_csv_se_lee_con_cualquier_programa(cliente, con_avance):
    respuesta = descargar(cliente, con_avance, "evolucion", "csv")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/csv")
    assert respuesta.content.startswith("﻿".encode())  # marca para Excel
    filas = list(csv.reader(io.StringIO(respuesta.content.decode("utf-8-sig"))))
    assert filas[0] == [
        "Fecha",
        "Peso (kg)",
        "Cintura (cm)",
        "Sesiones cumplidas",
        "Cumplimiento del plan",
    ]
    assert [fila[1] for fila in filas[1:]] == ["81.4", "80.6"]
    # Fecha en ISO: la que cualquier programa interpreta sin ambigüedad.
    assert date.fromisoformat(filas[1][0])


def test_el_csv_conserva_las_tildes(cliente, token_administrador):
    respuesta = descargar(cliente, token_administrador, "ejercicios", "csv")

    texto = respuesta.content.decode("utf-8-sig")
    assert "Grupo muscular" in texto and "Nivel mínimo" in texto


# --------------------------------------------------------------------------
# Texto ajeno que parece fórmula (inyección de fórmulas en hojas de cálculo)
# --------------------------------------------------------------------------

# Nombres que una persona mal intencionada podría escribir al registrarse. El
# informe de cuentas los entrega al administrador, que abre el archivo en Excel.
NOMBRES_HOSTILES = [
    '=HYPERLINK("http://ejemplo.invalid","Pulse aquí")',
    "+SUM(1+1)",
    "-2+3",
    "@SUM(1+1)",
]


def registrar_con_nombre(cliente, nombre):
    respuesta = cliente.post(
        "/api/v1/autenticacion/registro",
        json={
            "correo": "hostil@sistemarutinas.gt",
            "nombre": nombre,
            "contrasena": "Entrenamiento2028",
        },
    )
    assert respuesta.status_code == 201, respuesta.text


@pytest.mark.parametrize("nombre", NOMBRES_HOSTILES)
def test_el_excel_de_cuentas_no_ejecuta_un_nombre_que_parece_formula(
    cliente, token_administrador, nombre
):
    registrar_con_nombre(cliente, nombre)

    respuesta = descargar(cliente, token_administrador, "cuentas", "xlsx")

    assert respuesta.status_code == 200
    celdas = [
        celda
        for fila in load_workbook(io.BytesIO(respuesta.content))["Datos"].iter_rows(min_row=6)
        for celda in fila
        if celda.value == nombre
    ]
    assert len(celdas) == 1, "el nombre debe conservarse tal como se escribió"
    assert celdas[0].data_type == "s"
    with zipfile.ZipFile(io.BytesIO(respuesta.content)) as paquete:
        hojas = [n for n in paquete.namelist() if n.startswith("xl/worksheets/")]
        assert hojas
        for hoja in hojas:
            assert not re.search(rb"<f[ >]", paquete.read(hoja)), hoja


@pytest.mark.parametrize("nombre", NOMBRES_HOSTILES)
def test_el_csv_de_cuentas_neutraliza_un_nombre_que_parece_formula(
    cliente, token_administrador, nombre
):
    registrar_con_nombre(cliente, nombre)

    respuesta = descargar(cliente, token_administrador, "cuentas", "csv")

    filas = list(csv.reader(io.StringIO(respuesta.content.decode("utf-8-sig"))))
    nombres = [fila[0] for fila in filas[1:]]
    assert "'" + nombre in nombres
    assert nombre not in nombres


def test_las_cifras_negativas_y_los_cambios_con_signo_siguen_siendo_cifras():
    """La neutralización es solo para texto: un −0.8 numérico no es una fórmula."""
    informe = Informe(
        clave="prueba",
        titulo="Prueba",
        descripcion="Cifras con signo",
        titular="Titular de prueba",
        columnas=[
            Columna("etiqueta", "Etiqueta"),
            Columna("cambio", "Cambio", TipoDato.DECIMAL, decimales=1),
        ],
        filas=[{"etiqueta": "Semana 1", "cambio": -0.8}],
        resumen=[Indicador("Cambio total", "+1.2 kg")],
    )

    filas = list(csv.reader(io.StringIO(exportacion.a_csv(informe).decode("utf-8-sig"))))
    assert filas[1] == ["Semana 1", "-0.8"]

    libro = load_workbook(io.BytesIO(exportacion.a_excel(informe)))
    assert libro["Datos"]["B6"].value == -0.8
    assert libro["Datos"]["B6"].data_type == "n"
    # El texto del resumen se conserva sin comilla visible: sigue leyéndose «+1.2 kg».
    assert libro["Resumen"]["B3"].value == "+1.2 kg"
    assert libro["Resumen"]["B3"].data_type == "s"


# --------------------------------------------------------------------------
# 6.4.4 PDF
# --------------------------------------------------------------------------


@pytest.mark.parametrize("clave", ["evolucion", "plan", "medidas", "entrenamiento"])
def test_cada_informe_personal_se_entrega_en_pdf(cliente, con_avance, clave):
    respuesta = descargar(cliente, con_avance, clave, "pdf")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "application/pdf"
    assert respuesta.content.startswith(b"%PDF-")
    assert respuesta.content.rstrip().endswith(b"%%EOF")


@pytest.mark.parametrize("clave", ["indicadores", "cuentas", "alimentos", "ejercicios"])
def test_cada_informe_de_administracion_se_entrega_en_pdf(cliente, token_administrador, clave):
    respuesta = descargar(cliente, token_administrador, clave, "pdf")

    assert respuesta.status_code == 200
    assert respuesta.content.startswith(b"%PDF-")


def test_el_archivo_se_descarga_con_nombre_fechado_y_sin_cache(cliente, con_avance):
    respuesta = descargar(cliente, con_avance, "evolucion", "pdf")

    disposicion = respuesta.headers["content-disposition"]
    assert disposicion == (
        f'attachment; filename="informe-evolucion-{date.today().isoformat()}.pdf"'
    )
    assert respuesta.headers["cache-control"] == "no-store"
