# Fase 6: retos privados y pendientes transversales

**Actualización posterior del 30-10-2026:** el autor pospuso las funciones sociales. Este informe conserva la evidencia histórica del piloto; no describe funciones habilitadas actualmente. Continuar en [fase 7 individual](FASE_7_VALIDACION_INDIVIDUAL.md).

30 de octubre de 2026, horario de Guatemala. **Piloto local implementado y
comprobado técnicamente; fase abierta.** El responsable confirmó durante este
chat que todavía no tiene cliente OAuth de Gmail, teléfono físico ni revisores.
No se enviaron correos reales, no se evaluaron participantes ni se obtuvieron
dictámenes profesionales. No se publicó ni se migró producción.

## Recorrido entregado

`/avance/amigos`, accesible desde Avance y Más, permite crear un grupo con alias
y aceptación explícita de reglas. El propietario prepara códigos privados de
un solo uso, con 256 bits aleatorios, SHA-256 en almacenamiento y vencimiento
de 48 horas. Puede revocar todas las invitaciones; quien tiene un código puede
aceptarlo o rechazarlo. No se envían invitaciones por Gmail ni a contactos.
Límites del piloto: tres grupos por cuenta, veinte integrantes activos por grupo,
diez invitaciones vigentes y cinco denuncias abiertas por autor y grupo.

La participación semanal requiere otro consentimiento y una meta de 2 a 5
sesiones que no supere las sesiones con ejercicios del plan vigente. La semana
usa lunes–domingo y UTC−06:00 (Guatemala). Se conservan los días e identificadores
de las sesiones aceptadas al inscribirse. El servidor limita cada semana a
`min(100, floor(fechas_validas * 100 / meta))`. Cumplir dos de dos o cuatro de
cuatro da el mismo máximo; no hay ventajas por exceder el plan.

Una fecha válida corresponde a una sesión del calendario aceptado, registrada
el mismo día y después de la inscripción, con al menos una serie con repeticiones
o duración positiva. No cuenta una sesión libre, retroactiva, en día de descanso
o previa a la inscripción. Es un registro autodeclarado, no una verificación de
actividad real ni de completar toda la sesión. No ofrece premios monetarios.

`eventos_constancia` conserva una clave única `(semana_id, fecha)`. Se registra
en la misma transacción que la sesión de entrenamiento, bajo bloqueo de la
participación en PostgreSQL. La consulta no otorga puntos. Duplicar una sesión
no duplica su aporte social; regenerar el plan no borra los eventos ya otorgados.
Se corrigió la precisión subsegundo de la fecha de registro para evitar perder
la primera sesión si se inscribe y registra durante el mismo segundo.
La API histórica de entrenamiento sigue permitiendo registros duplicados;
este incremento garantiza idempotencia del aporte social, no de toda la bitácora.

La meta queda fija hasta la semana siguiente. Pausar retira aporte y objetivo
individual del colectivo, sin publicar el motivo; no se reactiva esa semana.
Salir oculta alias y aporte, conservando Mi senda. El propietario que sale
cierra el grupo para todos. No se permite reingreso al mismo grupo en este piloto.

## Privacidad y moderación

Solo los miembros activos consultan el grupo. La salida pública usa contratos
explícitos: alias, identificador de membresía, estado y puntos; no incluye correo,
ID de cuenta, peso, lesiones, cargas, calorías, notas ni bitácoras. Las metas y
los calendarios fijados permanecen internos. Las rutas personales conservan sus
permisos. Los puntos históricos de Mi senda no se trasladan al reto.

Bloquear oculta mutuamente las membresías entre las dos cuentas; el objetivo
colectivo se calcula entre participantes visibles para no filtrar el aporte de
una cuenta bloqueada por diferencia. No equivale a expulsar. El propietario puede
revisar denuncias por categoría, resolverlas y retirar miembros. Las denuncias
no tienen campos abiertos para datos de salud ni muestran identidad del autor.
Una denuncia contra el propietario requiere acudir al canal de Ayuda para revisión
fuera del grupo. No hay moderación independiente automatizada ni mensajería.

Se conservan membresías inactivas y denuncias para continuidad y moderación,
con eliminación vinculada a la cuenta mediante claves foráneas. El responsable
debe concretar el plazo operativo de retención antes del piloto real; la interfaz
dirige las solicitudes de eliminación a Ayuda. La política pública describe los
datos sociales. Consultas de grupo e invitaciones indican `no-store`.

## Duración de plancha (MEJ-14)

Motor, prescripción persistida, sesión, formulario, antecedentes, bitácora e
historial de ejercicio admiten segundos por serie. Los ejercicios dinámicos
siguen en repeticiones. La API rechaza mezclar segundos con repeticiones, carga
o reserva para la plancha, y rechaza segundos en otros ejercicios.

La identificación exige nombre, grupo y equipo exactos del catálogo piloto; no
depende del ID. Para planes nuevos se usan cero repeticiones y el rango de
20–30 segundos, como **referencia provisional** basada en [NASM](https://www.nasm.org/resource-center/exercise-library/plank),
consultada el 30-10-2026. La migración añade esa nueva orientación a las
prescripciones antiguas correspondientes, conservando sus cifras anteriores;
no convierte una cifra de repeticiones a segundos. Las series históricas
conservan repeticiones y duración nula. No se calcula progreso automático en
tiempo o carga para la plancha ni volumen en kg a partir de segundos.

Los borradores locales nuevos usan una clave de versión distinta: no se
interpreta como segundos un borrador anterior. Los borradores previos se
conservan en su clave antigua, sin reutilizarlos automáticamente. La referencia
de duración y el número de series aún necesitan revisión profesional.

## Migraciones y conservación

`0004_duracion_sostenes` añade tres columnas opcionales; `0005_comunidad_privada`
añade grupos, membresías, invitaciones, semanas, eventos, bloqueos y denuncias.
No importar modelos dinámicos en las revisiones estáticas. La actualización de
una base poblada conserva las series y cuentas originales. El descenso de 0004
se niega a borrar columnas si ya hay duraciones registradas; para retroceder con
datos reales usar un respaldo compatible. El descenso de 0005 elimina datos
sociales: limitarlo a ensayos desechables o restauración planificada.

Antes de iniciar este código en una base existente, respaldar, ensayar y ejecutar
`python gestionar_esquema.py actualizar` y `comprobar` desde backend con la
conexión elegida. `create_all` no reemplaza estas migraciones. No se cambiaron
las credenciales del usuario ni se ejecutó actualización sobre producción.

Se preservaron los cambios anteriores y la tesis de 667 pruebas. El manifiesto
previo de 186 archivos está en `evidencias/fase6/estado-inicial.json`. No se creó
un commit que mezclara el trabajo anterior con este incremento.

## Verificación del estado final

Windows, Python 3.12 del entorno existente, PostgreSQL 16 local en contenedor,
SQLite temporal, Node/Vite y navegador integrado; exclusivamente datos ficticios.

| Ejecución | Resultado | Evidencia y alcance |
|---|---|---|
| Suite completa final | **792 aprobadas, 4 omitidas**, 274.24 s | `suite-final.xml`. Incluye PostgreSQL, SQLite, invitación concurrente, eventos y duración. Omitidas: tres casos de concurrencia específicos de PostgreSQL y uno de enumeraciones nativas, todos sobre SQLite. Avisos previos de Starlette y Keras/NumPy. |
| Cliente de entrenamiento | **21 aprobadas** | Vinculación y geometría; no certifica biomecánica. |
| Cliente de interacción | **11 aprobadas** | Reloj, estados, tablas y privacidad de tarjetas. |
| Construcción y HTML | **Correctos** | Diez páginas públicas y seis armazones privados sin datos; comunidad se carga separada. |
| Gmail real | **No disponible** | Diagnóstico detecta ausencia de las tres credenciales OAuth; no hubo conexión ni envío. |
| Navegador | **Recorrido parcial observado** | Crear grupo, meta, preparación y ocultación de invitación, consulta de denuncias; ambos temas a 320 px sin desbordamiento horizontal observado. No prueba teléfono físico ni participantes. |

La ejecución exploratoria anterior `suite-completa.xml` dio 790 aprobadas y 3
omitidas antes de incorporar los eventos persistentes. La regresión intermedia
`regresion-final.xml` contiene el fallo de precisión de tiempo, corregido después.
Se conservan como evidencia histórica; **`suite-final.xml` corresponde al estado
final**. No sumar estas ejecuciones ni sustituir el fallo intermedio silenciosamente.

Pruebas nuevas: aislamiento entre cuentas y grupos, consentimiento, campos de
puntos rechazados, código usado/rechazado/revocado/vencido, hash, límites, bloqueo
bilateral, denuncias, salida/expulsión, meta fija, pausa, calendario, duplicados,
retroactividad, otra cuenta y persistencia tras regeneración. Una carrera real
en PostgreSQL acepta solo un consumo del mismo código.

`preparar_fase6.py` crea otra base PostgreSQL con nombre único y cuentas ficticias;
no usa `.env` ni selecciona producción. La última base queda identificada en
`evidencias/fase6/base-ui.txt`. Cliente de revisión: `127.0.0.1:15176`; API:
`127.0.0.1:18160`, con ese origen permitido expresamente. Capturas:
`comunidad-oscuro-320.png`, `comunidad-claro-320.png` y `plancha-guardada-320.png`. Se observó una serie ficticia de plancha de 25 segundos guardada, con cero repeticiones y cero kg; el resultado recibió foco. Los 185 puntos y la insignia de esa respuesta pertenecen al juego personal anterior, no al reto social. No se expuso a la red local.

## Pendientes y continuidad

- **Gmail:** propietario sin cliente OAuth aún. `backend/comprobar_gmail.py`
  diagnostica sin imprimir secretos; tras autorizar según `CORREO_GMAIL.md`,
  `--enviar-a-remitente` permite una prueba dirigida solo al remitente elegido.
  Aceptación de API, llegada y recuperación completa se comprueban por separado.
- **Ejercicios:** [revisión documental](REVISION_TECNICA_EJERCICIOS.md) realizada;
  dictamen técnico de diez fichas, dosis de plancha y nivel del remo pendientes.
  Se precisaron jalón y curl; los borradores siguen sin publicar movimiento normal.
- **Recetas:** [expediente de 18 preparaciones](REVISION_RECETAS_PARA_PROFESIONAL.md)
  preparado; dictamen, composición, rendimientos y tolerancias sin validar.
- **Personas y teléfono:** [guion de piloto](PILOTO_FASE6_Y_TELEFONO.md) preparado;
  ninguna sesión humana o prueba física registrada. No disponibles según el autor.
- Validar reglas sociales y retención con el responsable; realizar teclado y
  lector de pantalla en recorridos completos, interrupción del servidor y carga.
  Respaldar y publicar primero en pruebas. La degradación de 50 usuarios de fase 0
  y los demás pendientes históricos siguen abiertos.

La fase 6 no se declara terminada. Los grupos de gimnasio moderados y la liga
pública siguen fuera de este piloto. Para tesis, trasladar MEJ-11 y MEJ-14 a una
copia versionada: alcance, reglas, modelo de datos, permisos, calendario,
idempotencia, migraciones, interfaces y resultados por versión. No atribuir
efectos de adherencia ni cambios físicos a estas funciones.
