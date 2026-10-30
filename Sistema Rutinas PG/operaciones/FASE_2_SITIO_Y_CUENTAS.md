# Fase 2: sitio público, cuentas y primer uso

Fecha de verificación: 30 de octubre de 2026. Incremento local implementado;
pendiente de autorización de correo, evaluación humana y publicación en pruebas.
No se modificó la base de producción ni se desplegó esta versión.

## Comportamiento entregado

La portada `/` explica el producto, permite probar un registro de series con
datos ficticios y enlaza con las cuentas reales. Hay diez páginas públicas:
inicio, cómo funciona, ejercicios, alimentación, comunidad, preguntas frecuentes,
proyecto, privacidad, condiciones y ayuda. Comunidad describe una ampliación
futura; no ofrece retos todavía. El contacto público es `senda1986.gt@gmail.com`.

La compilación genera HTML público con contenido y metadatos por página. Las
rutas privadas reciben un armazón vacío con `noindex`; Nginx añade `no-store`.
Esto complementa, sin sustituir, la autorización de la API. Render conserva
reescrituras explícitas públicas y una salida privada para el resto de rutas.

Registro e inicio de sesión usan las cuentas existentes. Después del registro,
la bienvenida conduce al perfil, luego al plan de alimentación y a Mi día.
El panel prioriza la sesión prescrita de hoy o la alimentación en un día libre;
las cifras proceden de la cuenta. Ambos temas se comparten entre sitio y sistema:
A claro y B oscuro. Se conserva la palabra Senda; el símbolo final sigue pendiente.

## Recuperación de acceso

Se añadieron solicitud y restablecimiento, envío por Gmail API HTTPS y SMTP
alternativo. Sin credenciales el formulario informa que el servicio no está
disponible. No se ha autorizado Google ni enviado un mensaje real.
La configuración manual está en [CORREO_GMAIL.md](CORREO_GMAIL.md).

El enlace dura quince minutos, contiene un secreto aleatorio en el fragmento
de la URL y solo su SHA-256 se guarda en la base. Cada nueva solicitud sustituye
la anterior. El consumo es atómico, de un solo uso, y cambiar o restablecer la
contraseña revoca las sesiones anteriores. El cliente retira el fragmento del
historial y cierra su sesión antigua tras un restablecimiento exitoso.
La respuesta de solicitud es uniforme para cuentas existentes e inexistentes.

Los límites actuales son por proceso y se reinician con él; no constituyen un
límite distribuido entre réplicas. El envío usa tareas del proceso: una caída
puede perder la tarea y el usuario debe solicitar otro enlace. No hay una cola
durable ni reintentos garantizados. La configuración completa indica que puede
intentarse el envío; no prueba que Google lo acepte ni que llegue a la bandeja.

## Persistencia y publicación

La revisión `0002_recuperacion_acceso` añade `usuarios.version_sesion` y la tabla
de recuperación. Aplicarla explícitamente antes de arrancar el código nuevo;
`create_all` no añade columnas a tablas existentes. Respaldar y ensayar primero.
Consultar [MIGRACIONES.md](MIGRACIONES.md) para bases antiguas sin versión.

Render gratuito bloquea los puertos SMTP habituales; se eligió Gmail API sobre
HTTPS para mantener ese alojamiento. No se añadieron servicios de pago.
La portada conserva contenidos generales y no presenta testimonios ni resultados
de salud inventados. Privacidad y condiciones describen el alcance actual;
requieren revisión del responsable antes de publicar.

## Evidencia ejecutada

- Suite completa del backend con PostgreSQL habilitado: **709 aprobadas,
  2 omitidas**, 158 advertencias, 226.80 segundos. Las omisiones corresponden a
  casos que requieren un dialecto específico. Evidencia local:
  `operaciones/evidencias/fase2/pruebas-finales.xml`.
- Incluye actualización sobre esquema poblado, recuperación concurrente en
  PostgreSQL y SQLite, caducidad, reutilización, revocación, límites, ausencia
  de configuración y transporte Gmail simulado. No equivale a entrega real.
- Compilación y verificador de HTML público/privado ejecutados correctamente.
  Nginx validado y 22 comprobaciones HTTP locales aprobadas, incluidas rutas
  privadas, encabezados y una ruta pública con barra final. Evidencia:
  `operaciones/evidencias/fase2/http-construccion.json`.
- Navegador: acceso con cuenta ficticia, bienvenida, guardado de perfil,
  generación de plan y panel real. Revisión de ambos temas y tamaños de escritorio
  y móvil emulado. Se aisló la caché de prerenderizado para evitar que una
  compilación invalidara las dependencias del servidor de desarrollo.

## Pendientes para cerrar el incremento

Autorizar el remitente y verificar entrega, vencimiento y recuperación con una
cuenta controlada; ensayar migración y publicar en pruebas; revisar contenido de
privacidad y condiciones con el responsable; evaluar comprensión y medir el
primer plan en menos de cinco minutos con participantes. Probar un teléfono
físico. Las capturas y emulación no acreditan estas mediciones.

La tesis aún no se modificó. Trasladar este incremento a análisis de requisitos,
arquitectura de correo, diccionario de datos, seguridad, interfaces, manuales y
resultados; conservar los totales históricos por versión y no sumar ejecuciones.
Los pendientes de fase 0 y la evaluación humana de fase 1 siguen vigentes.
