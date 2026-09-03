#!/bin/sh
#
# Arranque del contenedor de servicios (apartado 3.8 de la tesis).
#
# Resuelve dos cosas que el CMD del Dockerfile no puede resolver por si solo.

set -eu

DIRECTORIO_MODELO="/aplicacion/modelo"
MODELO_INICIAL="/aplicacion/modelo_inicial"

# 1. Sembrar el modelo entrenado.
#
# El directorio del modelo es un volumen: sobrevive a la actualizacion del
# contenedor, que es lo que permite reentrenar la red sin reconstruir la imagen
# (requerimiento no funcional 4.5.6). Pero un volumen recien creado esta vacio,
# y el servicio arrancaria sin modelo y calcularia los planes con la formula de
# respaldo en lugar de la red neuronal, en silencio. Se copia entonces el
# modelo que trae la imagen, y solo si no hay ninguno: un modelo reentrenado
# jamas se sobrescribe.
if [ ! -f "${DIRECTORIO_MODELO}/requerimiento_energetico.keras" ] &&
   [ -f "${MODELO_INICIAL}/requerimiento_energetico.keras" ]; then
    echo "Sembrando el modelo entrenado que trae la imagen."
    cp "${MODELO_INICIAL}"/* "${DIRECTORIO_MODELO}/"
fi

# 2. Escuchar donde el proveedor indique.
#
# Render asigna el puerto por la variable PORT y descarta el servicio si nadie
# escucha en el. En el entorno de pruebas la composicion fija el 8000.
PUERTO="${PORT:-8000}"

# Cada proceso de trabajo carga su propia copia de TensorFlow, que ocupa cerca
# de 190 MB. Con la instancia de 512 MB contratada en Render cabe uno solo; el
# entorno de pruebas levanta dos para reproducir la carrera de arranque entre
# ellos, que fue un defecto real.
PROCESOS="${PROCESOS_DE_TRABAJO:-1}"

echo "Servicios en el puerto ${PUERTO} con ${PROCESOS} proceso(s) de trabajo."

exec uvicorn app.main:aplicacion \
    --host 0.0.0.0 \
    --port "${PUERTO}" \
    --workers "${PROCESOS}"
