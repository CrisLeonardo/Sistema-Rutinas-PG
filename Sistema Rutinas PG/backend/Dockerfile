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
COPY --chown=rutinas:rutinas entrenar_modelo.py ./

# El modelo entrenado se monta como volumen y no se copia en la imagen: pesa,
# cambia con cada reentrenamiento y debe sobrevivir a la actualizacion del
# contenedor, que es lo que permite reentrenar sin detener el servicio
# (requerimiento no funcional 4.5.6).
RUN mkdir -p /aplicacion/modelo && chown rutinas:rutinas /aplicacion/modelo

USER rutinas

EXPOSE 8000

# El sondeo de salud permite al orquestador reiniciar el contenedor cuando el
# servicio deja de responder, en lugar de dejarlo caido sin que nadie lo note.
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/estado')"

CMD ["uvicorn", "app.main:aplicacion", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
