# Imagen de la interfaz de cliente (apartado 3.8 de la tesis).
#
# La construccion produce archivos estaticos, que un servidor ligero entrega.
# No hay proceso de Node en produccion: solo HTML, CSS y JavaScript ya
# compilados, lo que reduce la superficie expuesta y el consumo del servidor.

FROM node:20-alpine AS construccion

WORKDIR /aplicacion

# Se copian primero los archivos de dependencias para reutilizar la capa
# mientras no cambien.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# La direccion de los servicios se fija al construir, porque Vite la incrusta en
# el paquete. En produccion la interfaz y los servicios comparten dominio, de
# modo que basta la ruta relativa y no hace falta declarar el origen completo.
ARG VITE_URL_API=/api/v1
ENV VITE_URL_API=$VITE_URL_API
RUN npm run build


FROM nginx:1.27-alpine AS produccion

COPY --from=construccion /aplicacion/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://127.0.0.1/ || exit 1
