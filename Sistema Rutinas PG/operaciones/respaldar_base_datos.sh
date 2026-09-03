#!/usr/bin/env bash
#
# Respaldo de la base de datos (apartado 3.8 de la tesis).
#
# Genera un volcado comprimido y retira los que superan el periodo de
# retencion. Pensado para ejecutarse desde el planificador de tareas:
#
#     0 2 * * * /ruta/al/proyecto/operaciones/respaldar_base_datos.sh
#
# El plan gratuito de Supabase no conserva copias automaticas, de modo que este
# respaldo no es una precaucion adicional sino la unica que existe sobre los
# datos de produccion.

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARCHIVO_ENTORNO="${RAIZ}/.env.pruebas"
DIRECTORIO_RESPALDOS="${RAIZ}/respaldos"
IMAGEN_CLIENTE="postgres:16-alpine"
CONTENEDOR_PRUEBAS="rutinas_postgres_pruebas"

# Dias que se conservan los respaldos. Un mes cubre el ciclo de facturacion y
# permite volver atras si un error se detecta con retraso.
DIAS_DE_RETENCION="${DIAS_DE_RETENCION:-30}"

# Hay dos maneras de alcanzar la base de datos, y el script elige solo.
#
# Con URL_RESPALDO definida se respalda por la red, que es como se respalda
# produccion: la credencial de Supabase entra por el entorno y no queda escrita
# en ningun archivo del repositorio.
#
#     URL_RESPALDO="$CADENA_DE_SUPABASE" ./operaciones/respaldar_base_datos.sh
#
# Sin ella se respalda el entorno de pruebas, y ahi no sirve una direccion de
# red: la base de datos de esa composicion no publica ningun puerto al exterior
# —solo los servicios la alcanzan, por la red interna de la composicion—, que es
# justamente lo que se quiere de ella. Se entra entonces por el contenedor, que
# ya trae el cliente de PostgreSQL.
POR_CONTENEDOR=0

if [[ -z "${URL_RESPALDO:-}" ]]; then
    if [[ ! -f "${ARCHIVO_ENTORNO}" ]]; then
        echo "Defina URL_RESPALDO con la cadena de conexión, o cree ${ARCHIVO_ENTORNO}." >&2
        exit 1
    fi
    # shellcheck disable=SC1090
    set -a; source "${ARCHIVO_ENTORNO}"; set +a

    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTENEDOR_PRUEBAS}$"; then
        echo "El contenedor ${CONTENEDOR_PRUEBAS} no está en ejecución." >&2
        echo "Levante el entorno de pruebas, o defina URL_RESPALDO para respaldar producción." >&2
        exit 1
    fi

    POR_CONTENEDOR=1
    NOMBRE_BASE="${POSTGRES_DB}"
    echo "Respaldando el entorno de pruebas desde el contenedor ${CONTENEDOR_PRUEBAS}."
else
    # SQLAlchemy nombra el controlador dentro del esquema de la direccion
    # («postgresql+psycopg://»); pg_dump no lo entiende. Se retira para poder
    # reutilizar la misma cadena que consume el sistema.
    URL_RESPALDO="${URL_RESPALDO//postgresql+psycopg:\/\//postgresql:\/\/}"
    URL_RESPALDO="${URL_RESPALDO//postgres:\/\//postgresql:\/\/}"
    NOMBRE_BASE="$(basename "${URL_RESPALDO%%\?*}")"
fi

mkdir -p "${DIRECTORIO_RESPALDOS}"
MARCA="$(date +%Y-%m-%d_%H%M)"
DESTINO="${DIRECTORIO_RESPALDOS}/${NOMBRE_BASE}_${MARCA}.sql.gz"

echo "Respaldando ${NOMBRE_BASE} en ${DESTINO}…"

# --no-owner y --no-privileges omiten los roles del servidor de origen: en
# Supabase pertenecen a su propia administracion, y restaurarlos en otro
# servidor falla. Lo que interesa conservar son las tablas y sus datos.
#
# Si el equipo no tiene instalado el cliente de PostgreSQL, el volcado se toma
# desde una imagen de contenedor de la misma version mayor que el servidor,
# porque un pg_dump mas antiguo que la base se niega a trabajar.
volcar() {
    if [[ "${POR_CONTENEDOR}" -eq 1 ]]; then
        docker exec "${CONTENEDOR_PRUEBAS}" pg_dump \
            --no-owner --no-privileges --clean --if-exists \
            --username "${POSTGRES_USER}" "${POSTGRES_DB}"
    elif command -v pg_dump >/dev/null 2>&1; then
        pg_dump --no-owner --no-privileges --clean --if-exists "${URL_RESPALDO}"
    else
        docker run --rm "${IMAGEN_CLIENTE}" pg_dump \
            --no-owner --no-privileges --clean --if-exists "${URL_RESPALDO}"
    fi
}

volcar | gzip > "${DESTINO}"

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
