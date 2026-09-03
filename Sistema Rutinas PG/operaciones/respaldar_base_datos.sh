#!/usr/bin/env bash
#
# Respaldo de la base de datos (apartado 3.8 de la tesis).
#
# Genera un volcado comprimido y retira los que superan el periodo de
# retencion. Pensado para ejecutarse desde el planificador del servidor:
#
#     0 2 * * * /ruta/al/proyecto/operaciones/respaldar_base_datos.sh
#
# Se ejecuta contra el contenedor de la composicion de produccion, de modo que
# no necesita tener instalado el cliente de MySQL en el servidor.

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARCHIVO_ENTORNO="${RAIZ}/.env.produccion"
DIRECTORIO_RESPALDOS="${RAIZ}/respaldos"
CONTENEDOR="rutinas_mysql_produccion"

# Dias que se conservan los respaldos. Un mes cubre el ciclo de facturacion y
# permite volver atras si un error se detecta con retraso.
DIAS_DE_RETENCION="${DIAS_DE_RETENCION:-30}"

if [[ ! -f "${ARCHIVO_ENTORNO}" ]]; then
    echo "No se encontró ${ARCHIVO_ENTORNO}. Cree el archivo de entorno antes de respaldar." >&2
    exit 1
fi

# shellcheck disable=SC1090
set -a; source "${ARCHIVO_ENTORNO}"; set +a

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTENEDOR}$"; then
    echo "El contenedor ${CONTENEDOR} no está en ejecución." >&2
    exit 1
fi

mkdir -p "${DIRECTORIO_RESPALDOS}"
MARCA="$(date +%Y-%m-%d_%H%M)"
DESTINO="${DIRECTORIO_RESPALDOS}/${MYSQL_DATABASE}_${MARCA}.sql.gz"

echo "Respaldando ${MYSQL_DATABASE} en ${DESTINO}…"

# --single-transaction toma el volcado sin bloquear las tablas, de modo que el
# sistema siga atendiendo usuarios mientras se respalda.
docker exec "${CONTENEDOR}" mysqldump \
    --single-transaction \
    --routines \
    --triggers \
    --user="${MYSQL_USER}" \
    --password="${MYSQL_PASSWORD}" \
    "${MYSQL_DATABASE}" | gzip > "${DESTINO}"

# Un volcado vacío indica que algo falló aunque el comando devolviera cero.
if [[ ! -s "${DESTINO}" ]]; then
    echo "El respaldo quedó vacío. Se elimina y se reporta el fallo." >&2
    rm -f "${DESTINO}"
    exit 1
fi

echo "Respaldo terminado: $(du -h "${DESTINO}" | cut -f1)"

echo "Retirando respaldos de más de ${DIAS_DE_RETENCION} días…"
find "${DIRECTORIO_RESPALDOS}" -name '*.sql.gz' -type f -mtime "+${DIAS_DE_RETENCION}" -delete

echo "Respaldos conservados: $(find "${DIRECTORIO_RESPALDOS}" -name '*.sql.gz' -type f | wc -l)"
