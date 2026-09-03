#!/usr/bin/env bash
#
# Restauracion de un respaldo (apartado 3.8 de la tesis).
#
# Un respaldo que nunca se ha restaurado no es un respaldo: es un archivo. Este
# script permite comprobar que los volcados sirven, y recuperar el sistema si
# hiciera falta.
#
#     ./operaciones/restaurar_base_datos.sh respaldos/sistema_rutinas_2026-09-03_0200.sql.gz

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ARCHIVO_ENTORNO="${RAIZ}/.env.produccion"
CONTENEDOR="rutinas_mysql_produccion"

if [[ $# -ne 1 ]]; then
    echo "Uso: $0 <archivo-de-respaldo.sql.gz>" >&2
    exit 1
fi

RESPALDO="$1"
if [[ ! -f "${RESPALDO}" ]]; then
    echo "No se encontró el respaldo ${RESPALDO}." >&2
    exit 1
fi

# shellcheck disable=SC1090
set -a; source "${ARCHIVO_ENTORNO}"; set +a

echo "ATENCIÓN: esto reemplaza el contenido actual de ${MYSQL_DATABASE}."
read -r -p "Escriba «restaurar» para continuar: " confirmacion
if [[ "${confirmacion}" != "restaurar" ]]; then
    echo "Operación cancelada."
    exit 0
fi

gunzip --stdout "${RESPALDO}" | docker exec --interactive "${CONTENEDOR}" mysql \
    --user="${MYSQL_USER}" \
    --password="${MYSQL_PASSWORD}" \
    "${MYSQL_DATABASE}"

echo "Restauración terminada. Reinicie los servicios para que tomen los datos nuevos."
