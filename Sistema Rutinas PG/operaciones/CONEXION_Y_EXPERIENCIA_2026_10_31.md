# Conexión y experiencia de Senda

31 de octubre de 2026, Guatemala. Implementación local; fase 7 abierta.

## Diagnóstico con el autor

El autor indicó que el monitor visita cada cinco minutos
`https://senda-gt.onrender.com`, antes `rutinas-interfaz`. Esa dirección sirve la
portada estática y no comprueba el servicio de autenticación. El reenvío actual
sí funciona: `/api/v1/estado` en Senda llega a la API. El monitor externo debe
usar GET a cualquiera de estas dos direcciones, cada cinco minutos:

- `https://senda-gt.onrender.com/api/v1/estado`
- `https://rutinas-servicios.onrender.com/api/v1/estado`

Se comprobó HTTP 200, JSON y `estado=disponible` en ambas. HEAD al estado directo
devolvió 405: no usar HEAD como sustituto de GET. La API permite el origen actual
de Senda en su encabezado CORS. No se encontró un fallo del reenvío en ese instante.
No se modificó el monitor externo ni se accedió a su historial o al panel de Render.

[Render](https://render.com/docs/free) documenta suspensión de servicios gratuitos
tras 15 minutos sin tráfico entrante, arranque de aproximadamente un minuto y
posibles reinicios. Vigilar la portada explica por qué su disponibilidad no
mantiene la API activa; no demuestra que toda demora histórica provenga de la
suspensión. Salud no consulta Supabase ni mide autenticación o inferencia.

El mensaje antiguo de acceso afirmaba «El servidor está iniciando» solo por
transcurrir seis segundos. No había una comprobación de la causa. Además,
verificar o renovar sesión borraba el token ante cualquier fallo, incluso de red.
El panel usaba un único `Promise.all`: una consulta fallida impedía mostrar todas.

Lecturas públicas del ensayo con el dominio confirmado:

| Comprobación | API directa | Reenvío de Senda |
|---|---|---|
| Salud | 200 JSON, 1.127 s | 200 JSON, 0.580 s |
| Opciones públicas | 200 JSON, 0.384 s | 200 JSON, 0.413 s |
| Catálogo sin token | 401 JSON, 0.414 s | 401 JSON, 0.372 s |

El 401 es esperado y no acredita acceso autenticado ni consulta de la base.
Estos tiempos son lecturas puntuales con el proceso ya disponible, sin ensayo
de arranque frío productivo. Se conserva también el diagnóstico inicial con el
dominio histórico: no sustituirlo ni presentarlo como dominio vigente.

## Cambios de conexión

- Una lectura pública de salud al abrir Senda; la portada y el acceso comparten
  la comprobación en curso. No hay pings periódicos desde cada navegador.
- Antes de enviar credenciales se espera disponibilidad, con plazo de 75 s.
  Solo salud se reintenta; el POST de acceso y las escrituras se envían una vez.
- Mensajes de conexión, ausencia de red y reintento sin atribuir una causa no
  comprobada. El botón distingue conexión de verificación de credenciales.
- Las consultas y descargas incluyen la lectura completa del cuerpo dentro del
  corte de red de 30 s. HTML recibido por error no se interpreta como datos ni
  se descarga como un informe válido. Una escritura sin confirmación a tiempo
  indica comprobar su resultado antes de repetirla.
- La verificación y renovación de sesión solo la invalidan por 401/403. Se
  conserva el cierre por inactividad y la protección del servidor en cada ruta.
  No se repite una consulta de sesión inmediatamente después de autenticarse.
- El panel conserva resultados disponibles y distingue consulta fallida de
  ausencia de plan, medidas o rutina; no anuncia descanso si falló la rutina.
- Semana no ofrece preparar un plan nuevo cuando falló consultar la semana
  existente. La preparación inicial sigue disponible ante el 404 esperado.
- Producción usa `/api/v1` aun si falta la variable de construcción. Desarrollo
  mantiene el puerto predeterminado documentado; la revisión usa 18160.
- `render.yaml` alinea CORS y URL pública con `senda-gt`. Conserva la identidad
  histórica del recurso del Blueprint para no proponer crear otro sitio.

## Experiencia e ilustraciones

Por petición del autor, las diez fichas normales permiten consultar su esquema
en movimiento; antes la reproducción estaba reservada al piloto. No se alteró
su estado de validación: siguen pendientes de revisión técnica. No se inventaron
dictámenes, fuentes, apoyos profesionales ni aprobaciones.

Los nueve ejercicios dinámicos reproducen un recorrido al abrir; después se
pausan. Hay pausa inmediata, repetición manual, velocidad, recorrido y selección
de fases. Al ocultar la pestaña o salir de vista se detiene el movimiento.
Con movimiento reducido se muestran tres posiciones y no se reproduce. Plancha
permanece como sostén estático: no se le atribuyen repeticiones ni otra dosis.

La biblioteca muestra miniaturas y acciones comprensibles. En escritorio,
los controles quedan junto al dibujo; en pantallas estrechas el botón principal
ocupa una fila completa. Se conservan el texto, las fuentes y los límites de
las ilustraciones. Los otros quince ejercicios del catálogo inicial siguen con
descripción escrita: no se anuncian 25 animaciones completas.

Hay respuestas de pulsación y foco, entrada de pantallas y tarjetas, selección
de navegación, trazado de anillos y barras de progreso. El panel incorpora
accesos a aprender ejercicios, organizar comidas y Mi senda. Los títulos del
navegador identifican la sección. Se mantienen Senda/Camino y A claro/B oscuro.
La preferencia de movimiento reducido desactiva las transiciones y animaciones.

## Verificación y evidencia

Evidencia local excluida de Git en `operaciones/evidencias/experiencia-2026-10-31/`:

- **46 pruebas actuales del cliente aprobadas**, cero fallos, en una invocación
  conjunta: 14 de conexión, 21 de entrenamiento y 11 de interacción. JUnit final
  en `cliente-cierre.xml`, con los archivos ejecutados en secuencia dentro de la
  misma invocación. Se conservan `cliente-final-sin-hmr.xml` y `cliente-final.xml`:
  esas ejecuciones previas mostraron un aviso de puerto de WebSocket de desarrollo
  ocupado al coexistir los servidores SSR; no falló ningún caso. La ejecución
  final secuencial terminó sin ese aviso.
- Construcción y verificador correctos: diez páginas públicas y seis armazones
  privados sin datos. No se añadieron bibliotecas ni se actualizó el bloqueo.
- **33 pruebas focalizadas de despliegue aprobadas**, una advertencia previa de
  obsolescencia Starlette/httpx. `despliegue-configuracion.xml`. Un primer intento
  no recogió casos por configurar la conexión global con SQLite en memoria y
  `max_overflow`; se corrigió el entorno de ensayo usando una ruta local nueva.
  No se modificó el motor de producción para corregir ese comando.
- API local, base SQLite nueva y cuenta ficticia: plan, rutina, menú, catálogo,
  preferencias, recetas y juego respondieron 200; comunidad respondió 404.
  Detalle en `recorridos-api.json`. No son perfiles ni participantes reales.
- En navegador: acceso, panel, biblioteca, reproducción real (cambio de puntos
  SVG y recorrido), selección de fase, preparación de semana y cambio al día 2.
  Se observaron cinco comidas y ningún error en ese día ficticio.
- Caída provocada solo en la API local creada por esta revisión: al recargar
  el panel se conservó la sesión y apareció reintento. Tras reiniciarla,
  reintentar recuperó el panel sin pedir credenciales. `sin-api-320.png`.
- Panel claro y guía en oscuro, con revisión a 320 px y tamaño de escritorio.
  Anchos observados de documento/contenido: 305/305 y 1265/1265 px, sin desborde.
  `guia-oscuro.png` muestra dibujo y controles. Se restauraron el tamaño y el
  tema oscuro originales. No es prueba en teléfono físico.

La suite completa histórica de servidor (812/4) no se volvió a ejecutar ni se
suma a las 33 pruebas focalizadas. Un aviso inicial de React sobre el título
SVG con varios nodos se corrigió usando una sola cadena. Las comprobaciones no
acreditan validación biomecánica ni accesibilidad completa con personas.

Reproducir cliente desde `frontend` con `npm run test:conexion`,
`npm run test:entrenamiento`, `npm run test:interaccion`, `npm run build` y
`npm run verificar:construccion`. El diagnóstico público sin credenciales es
`operaciones/diagnosticar_conexion.py`; su salida opcional exige un nombre nuevo
para conservar los ensayos anteriores. El valor predeterminado ya usa Senda.

## Continuidad

No hubo publicación, migración de producción, cambio de dosis, envío de correo
ni modificación de la tesis de 667 pruebas. Comunidad permanece apagada.
Se conservan todos los resultados anteriores de 50 usuarios, incluidos los
fallidos, y el primer plan de 6.29 s: este incremento no vuelve a medirlos ni
acredita sus límites de 3 s y 2 s. Fase 7 sigue abierta, junto con Gmail,
revisión profesional, participantes, observación y teléfono/red móvil real.

Cliente de revisión: `http://127.0.0.1:15176`; API ficticia:
`http://127.0.0.1:18160`. Los procesos pueden necesitar reinicio al retomar.
Los cambios todavía no están en la web publicada. Para el monitor externo,
el autor debe sustituir la URL de la portada por una de las rutas de salud
indicadas al inicio y verificar su historial después.
