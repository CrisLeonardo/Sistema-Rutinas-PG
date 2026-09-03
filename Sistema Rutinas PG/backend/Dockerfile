# Imagen de los servicios del sistema (apartado 3.8 de la tesis).
#
# Se fija Python 3.12 porque TensorFlow, que ejecuta el motor neuronal, no
# publica versiones compatibles con Python 3.13 ni 3.14.
#
# La construccion ocurre en dos etapas para que la imagen final no cargue con
# las herramientas de compilacion: la primera resuelve las dependencias y la
# segunda solo copia el entorno ya construido.

FROM python:3.12-slim AS dependencias

# uv administra el entorno, igual que en desarrollo, para que las versiones
# instaladas en produccion sean exactamente las del archivo de bloqueo.
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

WORKDIR /aplicacion

# Se copian primero los archivos de dependencias: mientras no cambien, esta capa
# se reutiliza y la construccion no vuelve a descargar TensorFlow.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev


FROM python:3.12-slim AS produccion

# El servicio se ejecuta con una cuenta sin privilegios: si el proceso se ve
# comprometido, el atacante no obtiene la cuenta administrativa del contenedor.
RUN groupadd --system rutinas && useradd --system --gid rutinas --create-home rutinas

WORKDIR /aplicacion

COPY --from=dependencias /aplicacion/.venv /aplicacion/.venv
ENV PATH="/aplicacion/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --chown=rutinas:rutinas app ./app
COPY --chown=rutinas:rutinas entrenar_modelo.py entrada.sh ./
RUN chmod +x /aplicacion/entrada.sh

# El modelo entrenado viaja en la imagen, pero en un directorio aparte del que
# el servicio lee. El directorio de lectura se monta como volumen —en Render,
# un disco persistente— para que un modelo reentrenado sobreviva a la
# actualizacion del contenedor, que es lo que permite reentrenar sin detener el
# servicio (requerimiento no funcional 4.5.6). El guion de arranque copia el
# modelo de la imagen al volumen solo cuando este ultimo esta vacio, de modo
# que el primer despliegue arranque ya con la red neuronal y no con la formula
# de respaldo.
COPY --chown=rutinas:rutinas modelo ./modelo_inicial
RUN mkdir -p /aplicacion/modelo && chown rutinas:rutinas /aplicacion/modelo

USER rutinas

EXPOSE 8000

# El sondeo de salud permite al orquestador reiniciar el contenedor cuando el
# servicio deja de responder, en lugar de dejarlo caido sin que nadie lo note.
# Render hace ademas su propia comprobacion sobre la ruta declarada en
# `render.yaml`.
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8000')+'/api/v1/estado')"

# El arranque pasa por un guion y no por un CMD directo porque el puerto y el
# numero de procesos los decide el entorno: Render asigna el puerto por la
# variable PORT y la memoria de la instancia limita cuantos procesos caben.
CMD ["/aplicacion/entrada.sh"]
