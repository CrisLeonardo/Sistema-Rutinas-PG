"""La optimización de una fila conserva las respuestas de predict del modelo real."""
from concurrent.futures import ThreadPoolExecutor
from app.motor.red_neuronal import MotorNeuronal
from app.modelos.enumeraciones import Sexo, NivelActividad, Objetivo, NivelExperiencia
from prueba_de_carga import perfil_de

def perfiles():
    for n in range(6):
        p=perfil_de(n+7)
        for clave,tipo in [('sexo',Sexo),('nivel_actividad',NivelActividad),
                           ('objetivo',Objetivo),('nivel_experiencia',NivelExperiencia)]:
            p[clave]=tipo(p[clave])
        yield p

def test_llamada_directa_conserva_predicciones_del_modelo_real():
    directo=MotorNeuronal.cargar()
    class ReferenciaPorLotes:
        def __call__(self,entrada,training=False):
            assert training is False
            return directo._modelo.predict(entrada,verbose=0)
    referencia=MotorNeuronal(ReferenciaPorLotes(),directo._normalizador,
                             directo._normalizador_salidas,directo.metricas)
    for p in perfiles():
        assert directo.predecir(**p)==referencia.predecir(**p)

def test_inferencia_concurrente_conserva_respuestas_y_memoria():
    motor=MotorNeuronal.cargar()
    entradas=list(perfiles())*2
    esperadas=[motor.predecir(**p) for p in entradas]
    motor.vaciar_memoria()
    with ThreadPoolExecutor(max_workers=8) as ejecutor:
        respuestas=list(ejecutor.map(lambda p:motor.predecir(**p),entradas))
    assert respuestas==esperadas
    assert motor.consultas==len(entradas)
