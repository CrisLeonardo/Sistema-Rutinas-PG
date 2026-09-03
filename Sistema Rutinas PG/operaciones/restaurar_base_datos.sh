#!/usr/bin/env bash
#
# Restauracion de un respaldo (apartado 3.8 de la tesis).
#
# Un respaldo que nunca se ha restaurado no es un respaldo: es un archivo. Este
# script permite comprobar que los volcados sirven, y recuperar el sistema si
# hiciera falta.
#
#     ./operaciones/restaurar_base_datos.sh respaldos/sistema_rutinas_2026-09-03_0200.sql.gz
#
# Sin variables restaura el entorno de pruebas, que es donde se comprueba un
# respaldo. Comprobarlo ahi cuesta unos minutos; descubrir que no servia, con
# produccion caida, cuesta los datos de los usuarios.
#
#     URL_RESTAURACION="$CADENA_DE_SUPABASE" ./operaciones/restaurar_base_datos.sh <archivo>

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARCHIVO_ENTORNO="${RAIZ}/.env.pruebas"
IMAGEN_CLIENTE="postgres:16-alpine"
CONTENEDOR_PRUEBAS="rutinas_postgres_pruebas"

if [[ $# -ne 1 ]]; then
    echo "Uso: $0 <archivo-de-respaldo.sql.gz>" >&2
    exit 1
fi

RESPALDO="$1"
if [[ ! -f "${RESPALDO}" ]]; then
    echo "No se encontró el respaldo ${RESPALDO}." >&2
    exit 1
fi

# Las dos maneras de alcanzar la base de datos son las mismas del respaldo: por
# la red cuando se indica la cadena de conexion, y por el contenedor cuando se
# trata del entorno de pruebas, cuya base no publica ningun puerto al exterior.
POR_CONTENEDOR=0

if [[ -z "${URL_RESTAURACION:-}" ]]; then
    if [[ ! -f "${ARCHIVO_ENTORNO}" ]]; then
        echo "Defina URL_RESTAURACION con la cadena de conexión, o cree ${ARCHIVO_ENTORNO}." >&2
        exit 1
    fi
    # shellcheck disable=SC1090
    set -a; source "${ARCHIVO_ENTORNO}"; set +a

    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTENEDOR_PRUEBAS}$"; then
        echo "El contenedor ${CONTENEDOR_PRUEBAS} no está en ejecución." >&2
        exit 1
    fi

    POR_CONTENEDOR=1
    DESTINO="${POSTGRES_DB}"
    DONDE="el contenedor ${CONTENEDOR_PRUEBAS}"
else
    URL_RESTAURACION="${URL_RESTAURACION//postgresql+psycopg:\/\//postgresql:\/\/}"
    URL_RESTAURACION="${URL_RESTAURACION//postgres:\/\//postgresql:\/\/}"
    DESTINO="$(basename "${URL_RESTAURACION%%\?*}")"
    DONDE="${URL_RESTAURACION#*@}"
    DONDE="${DONDE%%/*}"
fi

echo "ATENCIÓN: esto reemplaza el contenido actual de ${DESTINO} en ${DONDE}."
read -r -p "Escriba «restaurar» para continuar: " confirmacion
if [[ "${confirmacion}" != "restaurar" ]]; then
    echo "Operación cancelada."
    exit 0
fi

# --single-transaction deja la base intacta si el volcado falla a la mitad: o se
# restaura completo, o no se restaura nada.
restaurar() {
    if [[ "${POR_CONTENEDOR}" -eq 1 ]]; then
        docker exec --interactive "${CONTENEDOR_PRUEBAS}" psql \
            --single-transaction --set ON_ERROR_STOP=on \
            --quiet --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}"
    elif command -v psql >/dev/null 2>&1; then
        psql --single-transaction --set ON_ERROR_STOP=on --quiet "${URL_RESTAURACION}"
    else
        docker run --rm --interactive "${IMAGEN_CLIENTE}" psql \
            --single-transaction --set ON_ERROR_STOP=on --quiet "${URL_RESTAURACION}"
    fi
}

gunzip --stdout "${RESPALDO}" | restaurar

echo "Restauración terminada. Reinicie los servicios para que tomen los datos nuevos."
