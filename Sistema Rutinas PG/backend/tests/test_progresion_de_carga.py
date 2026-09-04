"""Pruebas del motor de progresion de carga (regla del negocio *d*).

`formulas.progresion_admitida` implementaba el incremento maximo del 10 % entre
microciclos desde la Iteracion 3, y su unica invocacion en todo el sistema estaba
dentro de su propia prueba: ningun servicio la llamaba. En la practica, la rutina
de la semana doce era identica a la de la primera.

Estas pruebas fijan el comportamiento del motor que la pone en uso. No tocan la
base de datos: el paquete `motor` recibe el historial ya leido.
"""

import pytest

from app.motor import progresion
from app.motor.formulas import INCREMENTO_MAXIMO_ENTRE_MICROCICLOS
from app.motor.progresion import Decision, EjecucionPrevia, SerieEjecutada


def ejecucion(repeticiones: list[int], peso: float | None, esfuerzo: int | None = None):
    return EjecucionPrevia(
        series=[SerieEjecutada(repeticiones=r, peso_kg=peso) for r in repeticiones],
        percepcion_esfuerzo=esfuerzo,
    )


# --------------------------------------------------------------------------
# Primera vez
# --------------------------------------------------------------------------


def test_sin_historial_no_se_inventa_una_carga():
    """El sistema no puede saber con cuanto peso empieza alguien."""
    recomendacion = progresion.calcular(None, 8, 12, es_compuesto=True)

    assert recomendacion.decision == Decision.PRIMERA_VEZ
    assert recomendacion.carga_sugerida_kg is None
    assert recomendacion.repeticiones_objetivo == 8


def test_una_ejecucion_vacia_equivale_a_no_tener_historial():
    recomendacion = progresion.calcular(
        EjecucionPrevia(series=[]), 8, 12, es_compuesto=True
    )

    assert recomendacion.decision == Decision.PRIMERA_VEZ


# --------------------------------------------------------------------------
# Progresion doble
# --------------------------------------------------------------------------


def test_sin_completar_el_rango_se_repite_la_carga():
    """Se avanza en repeticiones antes que en peso."""
    recomendacion = progresion.calcular(
        ejecucion([10, 9, 8], 60.0), 8, 12, es_compuesto=True
    )

    assert recomendacion.decision == Decision.MANTENER
    assert recomendacion.carga_sugerida_kg == 60.0


def test_una_sola_serie_floja_impide_subir():
    """La progresion doble avanza cuando el rango se domina por completo."""
    recomendacion = progresion.calcular(
        ejecucion([12, 12, 11], 60.0), 8, 12, es_compuesto=True
    )

    assert recomendacion.decision == Decision.MANTENER


def test_al_dominar_el_rango_se_sube_la_carga():
    recomendacion = progresion.calcular(
        ejecucion([12, 12, 12], 60.0), 8, 12, es_compuesto=True
    )

    assert recomendacion.decision == Decision.SUBIR_CARGA
    assert recomendacion.carga_sugerida_kg == 62.5
    assert recomendacion.hay_incremento


def test_superar_el_rango_tambien_habilita_la_subida():
    recomendacion = progresion.calcular(
        ejecucion([14, 13, 12], 60.0), 8, 12, es_compuesto=True
    )

    assert recomendacion.decision == Decision.SUBIR_CARGA


def test_al_subir_la_carga_las_repeticiones_vuelven_al_extremo_bajo():
    """Es lo que define a la progresion doble: se sube peso y se baja volumen."""
    recomendacion = progresion.calcular(
        ejecucion([12, 12, 12], 60.0), 8, 12, es_compuesto=True
    )

    assert recomendacion.repeticiones_objetivo == 8


# --------------------------------------------------------------------------
# La regla del negocio *d*
# --------------------------------------------------------------------------


@pytest.mark.parametrize("carga", [30.0, 45.0, 60.0, 80.0, 100.0, 140.0, 200.0])
def test_el_incremento_nunca_supera_el_diez_por_ciento(carga):
    """Regla *d* del apartado 4.3.4, ahora verificada sobre el camino real."""
    recomendacion = progresion.calcular(
        ejecucion([12, 12, 12], carga), 8, 12, es_compuesto=True
    )

    if recomendacion.decision != Decision.SUBIR_CARGA:
        return
    incremento = (recomendacion.carga_sugerida_kg - carga) / carga
    assert incremento <= INCREMENTO_MAXIMO_ENTRE_MICROCICLOS + 1e-9


def test_con_carga_ligera_se_progresa_en_repeticiones():
    """El disco mas pequeno del gimnasio ya excederia el 10 % admitido.

    Saltarse la regla seria lo facil; la respuesta correcta es seguir sumando
    repeticiones hasta que el escalon quepa dentro del limite.
    """
    recomendacion = progresion.calcular(
        ejecucion([12, 12, 12], 10.0), 8, 12, es_compuesto=True
    )

    assert recomendacion.decision == Decision.SUMAR_REPETICIONES
    assert recomendacion.carga_sugerida_kg == 10.0
    assert "10 %" in recomendacion.explicacion


def test_el_umbral_de_carga_ligera_es_el_que_la_regla_impone():
    """Con 25 kg el escalon de 2.5 cabe justo; con 24 ya no."""
    cabe = progresion.calcular(ejecucion([12, 12], 25.0), 8, 12, es_compuesto=True)
    no_cabe = progresion.calcular(ejecucion([12, 12], 24.0), 8, 12, es_compuesto=True)

    assert cabe.decision == Decision.SUBIR_CARGA
    assert no_cabe.decision == Decision.SUMAR_REPETICIONES


def test_la_carga_sugerida_siempre_supera_a_la_previa_cuando_sube():
    """El redondeo al escalon no debe dejar la sugerencia donde estaba."""
    for carga in (27.5, 33.0, 47.5, 62.5, 91.0):
        recomendacion = progresion.calcular(
            ejecucion([12, 12], carga), 8, 12, es_compuesto=True
        )
        if recomendacion.decision == Decision.SUBIR_CARGA:
            assert recomendacion.carga_sugerida_kg > carga


def test_la_carga_sugerida_cae_en_un_escalon_armable():
    """No sirve pedir 61.3 kg: hay que poder armarlo con los discos del gimnasio."""
    for carga in (40.0, 55.0, 72.5, 100.0):
        recomendacion = progresion.calcular(
            ejecucion([12, 12], carga), 8, 12, es_compuesto=True
        )
        if recomendacion.decision == Decision.SUBIR_CARGA:
            resto = round(recomendacion.carga_sugerida_kg / 2.5, 6) % 1
            assert resto == pytest.approx(0), recomendacion.carga_sugerida_kg


def test_el_ejercicio_aislado_usa_un_escalon_menor():
    """La mancuerna y la maquina saltan de a menos que la barra."""
    compuesto = progresion.calcular(
        ejecucion([12, 12], 40.0), 8, 12, es_compuesto=True
    )
    aislado = progresion.calcular(
        ejecucion([12, 12], 40.0), 8, 12, es_compuesto=False
    )

    assert aislado.carga_sugerida_kg < compuesto.carga_sugerida_kg


# --------------------------------------------------------------------------
# Peso corporal
# --------------------------------------------------------------------------


def test_sin_carga_se_progresa_en_repeticiones():
    recomendacion = progresion.calcular(
        ejecucion([15, 14, 12], None), 10, 20, es_compuesto=False
    )

    assert recomendacion.decision == Decision.SUMAR_REPETICIONES
    assert recomendacion.repeticiones_objetivo == 13
    assert "su propio peso" in recomendacion.explicacion


def test_una_carga_insignificante_se_trata_como_peso_corporal():
    recomendacion = progresion.calcular(
        ejecucion([15, 15], 1.0), 10, 20, es_compuesto=False
    )

    assert recomendacion.decision == Decision.SUMAR_REPETICIONES


def test_el_objetivo_de_repeticiones_no_pasa_del_rango():
    recomendacion = progresion.calcular(
        ejecucion([20, 20], None), 10, 20, es_compuesto=False
    )

    assert recomendacion.repeticiones_objetivo == 20


# --------------------------------------------------------------------------
# Descarga por fatiga
# --------------------------------------------------------------------------


def test_el_estancamiento_con_esfuerzo_alto_sugiere_descargar():
    """Estancarse esforzandose mucho es fatiga, no falta de estimulo."""
    recomendacion = progresion.calcular(
        ejecucion([10, 9, 9], 80.0, esfuerzo=9),
        8,
        12,
        es_compuesto=True,
        sesiones_sin_avanzar=3,
    )

    assert recomendacion.decision == Decision.DESCARGAR
    assert recomendacion.carga_sugerida_kg < 80.0


def test_el_estancamiento_sin_esfuerzo_alto_no_descarga():
    """Sin fatiga reportada, el estancamiento pide constancia, no descanso."""
    recomendacion = progresion.calcular(
        ejecucion([10, 9, 9], 80.0, esfuerzo=5),
        8,
        12,
        es_compuesto=True,
        sesiones_sin_avanzar=4,
    )

    assert recomendacion.decision == Decision.MANTENER


def test_pocas_sesiones_estancadas_no_bastan_para_descargar():
    recomendacion = progresion.calcular(
        ejecucion([10, 9], 80.0, esfuerzo=9),
        8,
        12,
        es_compuesto=True,
        sesiones_sin_avanzar=1,
    )

    assert recomendacion.decision == Decision.MANTENER


def test_la_descarga_cae_en_un_escalon_armable():
    recomendacion = progresion.calcular(
        ejecucion([10, 9], 100.0, esfuerzo=9),
        8,
        12,
        es_compuesto=True,
        sesiones_sin_avanzar=3,
    )

    assert recomendacion.carga_sugerida_kg == 90.0


# --------------------------------------------------------------------------
# Coherencia general
# --------------------------------------------------------------------------


def test_toda_recomendacion_trae_su_explicacion():
    """El requerimiento 4.5.3 exige explicar toda cifra tecnica."""
    casos = [
        (None, 0),
        (ejecucion([12, 12], 60.0), 0),
        (ejecucion([9, 8], 60.0), 0),
        (ejecucion([12, 12], 10.0), 0),
        (ejecucion([15, 15], None), 0),
        (ejecucion([10, 9], 80.0, esfuerzo=9), 3),
    ]
    for previa, estancadas in casos:
        recomendacion = progresion.calcular(
            previa, 8, 12, es_compuesto=True, sesiones_sin_avanzar=estancadas
        )
        assert recomendacion.explicacion
        assert len(recomendacion.explicacion) > 40


def test_cumplio_el_rango_exige_todas_las_series():
    completo = ejecucion([12, 12, 12], 60.0)
    incompleto = ejecucion([12, 12, 11], 60.0)

    assert progresion.cumplio_el_rango(completo, 12)
    assert not progresion.cumplio_el_rango(incompleto, 12)
    assert not progresion.cumplio_el_rango(EjecucionPrevia(series=[]), 12)


def test_la_carga_maxima_es_la_de_trabajo():
    previa = EjecucionPrevia(
        series=[
            SerieEjecutada(repeticiones=12, peso_kg=40.0),
            SerieEjecutada(repeticiones=10, peso_kg=60.0),
            SerieEjecutada(repeticiones=8, peso_kg=50.0),
        ]
    )

    assert previa.carga_maxima == 60.0
    assert previa.repeticiones_minimas == 8
