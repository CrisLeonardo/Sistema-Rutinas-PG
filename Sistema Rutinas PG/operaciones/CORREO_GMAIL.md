# Correo de Senda

Cuenta pública elegida por el responsable: **senda1986.gt@gmail.com**.
El contacto mediante enlace de correo ya funciona sin credenciales del servidor.
Enviar recuperación desde esa cuenta requiere su autorización. No se realizó
esa autorización ni se enviaron correos durante la implementación.

## Preparación personal del propietario

Estado confirmado el 30-10-2026: el propietario aún no dispone del cliente OAuth.
`python comprobar_gmail.py` comprueba la presencia de configuración sin mostrar
secretos ni hacer conexiones. Tras completar la autorización, ejecutar
`python comprobar_gmail.py --enviar-a-remitente` envía una prueba únicamente a
`senda1986.gt@gmail.com`. La aceptación por la API no prueba llegada a la bandeja;
comprobarla personalmente y después verificar recuperación con una cuenta
controlada. No se ejecutó un envío real en este incremento.

1. En Google Cloud, seleccionar un proyecto propio, habilitar Gmail API y
   configurar la pantalla de consentimiento OAuth. Si está en pruebas, incluir
   la cuenta remitente como usuario de prueba.
2. Crear un cliente OAuth de tipo **Aplicación de escritorio** y descargar su
   JSON fuera del repositorio. Comprobar las políticas y condiciones de Google
   antes de aceptar. El alcance utilizado es solo `gmail.send`; no se solicita
   leer la bandeja. Revisar el estado de publicación y las reglas de vigencia
   de las autorizaciones antes de operar de forma continua.
3. Desde `backend`, ejecutar personalmente:

   ```powershell
   uv run python configurar_gmail.py "C:\ruta-privada\client_secret.json"
   ```

4. Abrir el enlace mostrado, comprobar el proyecto y autorizar la cuenta
   `senda1986.gt@gmail.com`. El retorno ocurre en `127.0.0.1` y vence a los cinco
   minutos. El asistente utiliza estado aleatorio y PKCE, y guarda los secretos
   en `backend/.env.gmail` sin imprimirlos ni sobrescribir un archivo existente.
   En Windows conservar ese archivo bajo el usuario propietario y revisar sus
   permisos NTFS; el modo de creación de Python no garantiza una ACL privada.
5. Configurar en `.env` `URL_PUBLICA_FRONTEND` con el origen real de la interfaz
   (sin ruta), reiniciar el backend y verificar la recuperación con una cuenta
   controlada. En producción se exige HTTPS. Un enlace dura quince minutos;
   el envío real y su llegada deben comprobarse por separado.

`.env.gmail` está ignorado por Git. No pegar el JSON, secreto, código OAuth ni
refresh token en un chat, captura, documentación o commit. La autorización es
para el servidor remitente; los usuarios de Senda siguen usando sus propias
cuentas del sistema, sin iniciar sesión con Google.

## Render

Guardar mediante el panel privado de variables de entorno del backend:
`CORREO_TRANSPORTE=gmail_api`, `CORREO_REMITENTE`, `GMAIL_CLIENTE_ID`,
`GMAIL_CLIENTE_SECRETO`, `GMAIL_REFRESH_TOKEN`, `CORREO_CONTACTO` y
`URL_PUBLICA_FRONTEND`. Copiar los valores desde el archivo privado, nunca a
`render.yaml`. Configurar también `VITE_CORREO_CONTACTO` del frontend si cambia
el contacto. El repositorio solo contiene ejemplos sin secretos.

El plan gratuito de Render bloquea conexiones salientes a los puertos 25, 465
y 587; por eso se usa la API HTTPS. SMTP queda disponible para otro alojamiento
o desarrollo mediante `CORREO_TRANSPORTE=smtp` y las variables del ejemplo,
con conexión cifrada. No se debe configurar una contraseña normal de Gmail.

Si Google revoca o vence la autorización, volver a autorizar personalmente y
actualizar el secreto del servidor. Una configuración completa no detecta por
adelantado ese rechazo. Los registros del envío omiten destinatario, token y
contenido de la excepción; no registrar respuestas OAuth ni enlaces completos.

Referencias oficiales consultadas el 30 de octubre de 2026:
[restricciones de Render gratuito](https://render.com/docs/free),
[envío mediante Gmail API](https://developers.google.com/workspace/gmail/api/guides/sending),
[OAuth para aplicaciones nativas](https://developers.google.com/identity/protocols/oauth2/native-app).
