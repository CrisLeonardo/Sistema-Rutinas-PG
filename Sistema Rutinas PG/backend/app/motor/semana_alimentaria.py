"""Ajuste acotado de ingredientes al objetivo existente, sin modificarlo.

6 % es un criterio de aceptación de software del piloto para energía y cada
macronutriente; requiere revisión profesional antes de publicación. Si no se
alcanza, se rechaza la propuesta en vez de relajar el objetivo silenciosamente.
"""
from copy import deepcopy
import numpy as np

from app.esquemas.menu import PorcionPublica
from app.motor.menu import TIEMPOS_DE_COMIDA
from app.nucleo.recetas import RECETAS
from app.servicios.restricciones_alimentarias import detalle

TOLERANCIA = 0.06
MAGNITUDES = ("energia_kcal", "proteina_g", "carbohidrato_g", "grasa_g")


class SemanaNoFactible(ValueError):
    pass


def vector(alimento):
    return np.array([float(getattr(alimento, k + "_100g")) for k in MAGNITUDES]) / 100


def totales(tiempos):
    return {k: round(sum(p[k] for t in tiempos for p in t["porciones"]), 2) for k in MAGNITUDES}


def dentro(aporte, objetivo):
    # Solo dos centésimas de holgura por el redondeo, también en refacciones:
    # permitir un gramo entero excedería el 6 % cuando el aporte es pequeño.
    return all(abs(aporte[k] - objetivo[k]) <= objetivo[k] * TOLERANCIA + 0.02 for k in MAGNITUDES)


def disponibles_para_recetas(alimentos):
    por_nombre = {a.nombre: a for a in alimentos if detalle(a) is not None}
    recetas = [r for r in RECETAS if all(n in por_nombre for n, _ in r.ingredientes)]
    return recetas, por_nombre


def porcion(alimento, gramos):
    datos = PorcionPublica(
        alimento_id=alimento.id, nombre=alimento.nombre, categoria=alimento.categoria,
        gramos=gramos, medida_casera=alimento.medida_casera,
        energia_kcal=round(alimento.energia_de(gramos)),
        proteina_g=round(alimento.proteina_de(gramos)),
        carbohidrato_g=round(alimento.carbohidrato_de(gramos)),
        grasa_g=round(alimento.grasa_de(gramos)),
        costo_quetzales=alimento.costo_de(gramos),
    ).model_dump(mode="json")
    # Los totales se calculan sobre la cantidad realmente servida, con 2 decimales.
    for k, valor in zip(MAGNITUDES, vector(alimento) * gramos):
        datos[k] = round(float(valor), 2)
    datos.update(estado=detalle(alimento)[0], unidad="g", precio_fecha=None,
                 precio_fuente="Estimación del catálogo provisional; sin verificación de campo")
    if datos["costo_quetzales"] is not None:
        datos["costo_quetzales"] = round(datos["costo_quetzales"], 4)
    return datos


def componer(receta, alimentos, gramos, tiempo=None):
    porciones = [porcion(alimentos[n], int(g)) for (n, _), g in zip(receta.ingredientes, gramos)]
    costo = None if any(p["costo_quetzales"] is None for p in porciones) else round(sum(p["costo_quetzales"] for p in porciones), 2)
    return {
        "receta_id": receta.id, "receta": receta.nombre,
        "nombre": TIEMPOS_DE_COMIDA[tiempo][0] if tiempo is not None else receta.nombre,
        "minutos": receta.minutos, "pasos": list(receta.pasos),
        "rendimiento_porciones": receta.rendimiento_porciones,
        "estado_revision": receta.estado_revision, "porciones": porciones,
        "costo_quetzales": costo, **totales([{"porciones": porciones}]),
    }


def ajustar(recetas, alimentos, objetivo, tiempos):
    """Mínimos cuadrados con límites por ingrediente; redondeo final a gramos."""
    ingredientes = [(alimentos[n], g) for r in recetas for n, g in r.ingredientes]
    bases = np.array([g for _, g in ingredientes], dtype=float)
    escala = np.array([max(objetivo[k], 1) for k in MAGNITUDES])
    matriz = np.column_stack([vector(a) * g / escala for a, g in ingredientes])
    meta = np.array([objetivo[k] for k in MAGNITUDES]) / escala
    if len(recetas) == 5:
        # Conserva el reparto existente: el ajuste diario no concentra toda la
        # energía en un único plato para conseguir buenos totales agregados.
        filas = np.zeros((5, len(ingredientes)))
        cursor = 0
        for t, receta in enumerate(recetas):
            for _ in receta.ingredientes:
                a, g = ingredientes[cursor]
                filas[t, cursor] = a.energia_de(g) / (objetivo["energia_kcal"] * TIEMPOS_DE_COMIDA[t][1])
                cursor += 1
        matriz = np.vstack((matriz, filas))
        meta = np.concatenate((meta, np.ones(5)))
    inferior = np.full(len(bases), 0.35)
    # Límites de edición del piloto, no una nueva prescripción clínica.
    superior = np.array([min(2.5, (60 if a.nombre in {"Maní tostado", "Semilla de marañón"} else 400) / g) for a, g in ingredientes])
    x = np.ones(len(bases))
    residual = matriz @ x - meta
    normas = np.sum(matriz * matriz, axis=0)
    for _ in range(100):
        for i in range(len(x)):
            if normas[i] <= 0:
                continue
            nuevo = np.clip(x[i] - np.dot(matriz[:, i], residual) / normas[i], inferior[i], superior[i])
            residual += matriz[:, i] * (nuevo - x[i])
            x[i] = nuevo
        if np.max(np.abs(residual)) < 0.008:
            break
    gramos = np.rint(bases * x).astype(int)
    resultado = []
    cursor = 0
    for r, tiempo in zip(recetas, tiempos):
        cantidad = len(r.ingredientes)
        resultado.append(componer(r, alimentos, gramos[cursor:cursor + cantidad], tiempo))
        cursor += cantidad
    reparto_correcto = len(recetas) != 5 or all(
        abs(t["energia_kcal"] / (objetivo["energia_kcal"] * TIEMPOS_DE_COMIDA[i][1]) - 1) <= TOLERANCIA
        for i, t in enumerate(resultado))
    return resultado if reparto_correcto and dentro(totales(resultado), objetivo) else None


def generar(objetivo, alimentos):
    recetas, por_nombre = disponibles_para_recetas(alimentos)
    por_tiempo = [[r for r in recetas if t in r.tiempos] for t in range(5)]
    if any(not lista for lista in por_tiempo):
        raise SemanaNoFactible("No hay recetas compatibles para todos los tiempos. Revise el catálogo con un profesional; no quite una alergia para generar la semana.")
    dias = []
    anteriores = []
    for dia in range(1, 8):
        encontrado = None
        # Orden estable: mismas restricciones y catálogo producen la misma semana.
        for intento in range(100):
            elegidas = [lista[(dia - 1 + (1 if t == 3 else 0) + intento * (t + 1) + intento // len(lista)) % len(lista)] for t, lista in enumerate(por_tiempo)]
            if intento < 75 and anteriores and any(elegidas[t].id == anteriores[t] for t in (0, 2, 4)):
                continue
            ajustadas = ajustar(elegidas, por_nombre, objetivo, range(5))
            if ajustadas:
                encontrado = {"dia": dia, "tiempos": ajustadas, **totales(ajustadas)}
                anteriores = [r.id for r in elegidas]
                break
        if encontrado is None:
            raise SemanaNoFactible("Las recetas disponibles no alcanzan los objetivos del plan dentro del 6 %. No se guardó una semana incompleta. Requiere revisión profesional del catálogo y las porciones.")
        dias.append(encontrado)
    return {"dias": dias, "objetivo": objetivo, "tolerancia_porcentaje": TOLERANCIA * 100}


def alternativas(semana, alimentos, dia, tiempo):
    recetas, por_nombre = disponibles_para_recetas(alimentos)
    original = semana["dias"][dia - 1]["tiempos"][tiempo]
    objetivo = {k: original[k] for k in MAGNITUDES}
    opciones = []
    for receta in recetas:
        if tiempo not in receta.tiempos or receta.id == original["receta_id"]:
            continue
        ajustadas = ajustar([receta], por_nombre, objetivo, [tiempo])
        if ajustadas:
            copia = deepcopy(semana["dias"][dia - 1]["tiempos"])
            copia[tiempo] = ajustadas[0]
            energia_del_tiempo = semana["objetivo"]["energia_kcal"] * TIEMPOS_DE_COMIDA[tiempo][1]
            if dentro(totales(copia), semana["objetivo"]) and abs(ajustadas[0]["energia_kcal"] / energia_del_tiempo - 1) <= TOLERANCIA:
                opciones.append(ajustadas[0])
    return opciones


def compras(semana):
    acumulados = {}
    for dia in semana["dias"]:
        for tiempo in dia["tiempos"]:
            for p in tiempo["porciones"]:
                clave = p["alimento_id"]
                if clave not in acumulados:
                    acumulados[clave] = {k: p[k] for k in ("alimento_id", "nombre", "categoria", "estado", "medida_casera", "precio_fecha", "precio_fuente")}
                    acumulados[clave].update(gramos_semana=0, costo_quetzales=0.0)
                fila = acumulados[clave]
                fila["gramos_semana"] += p["gramos"]
                if p["costo_quetzales"] is None or fila["costo_quetzales"] is None:
                    fila["costo_quetzales"] = None
                else:
                    fila["costo_quetzales"] += p["costo_quetzales"]
    filas = sorted(acumulados.values(), key=lambda f: (f["categoria"], f["nombre"]))
    for f in filas:
        if f["costo_quetzales"] is not None:
            f["costo_quetzales"] = round(f["costo_quetzales"], 2)
    return {"renglones": filas, "costo_quetzales": None if any(f["costo_quetzales"] is None for f in filas) else round(sum(f["costo_quetzales"] for f in filas), 2),
            "nota": "Cantidades comestibles en el estado indicado; arroz y legumbres se pesan cocidos. No equivalen a kilos de producto crudo. Precios provisionales, sin fecha de observación."}
