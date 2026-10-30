# Línea base de Senda y resultados de la fase 0

Fecha: 29 de octubre de 2026, horario de Guatemala.

La preparación técnica de la fase 0 quedó ejecutada: se comprobó la batería
original, se construyó el cliente, se incorporó un historial de migraciones y se
ensayó la recuperación de PostgreSQL con datos ficticios. La revisión visual en
navegador y teléfono, y la certificación del despliegue publicado, siguen pendientes.
Esta distinción impide presentar la fase completa como validada de extremo a extremo.

## 1. Decisiones y arquitectura conservada

a) El autor eligió **Senda** como nombre. El símbolo, iconos y diseño de pantallas
se realizarán en la fase 1; no se hizo un cambio visual general en esta fase.

b) Se conservan React, Vite, FastAPI, SQLAlchemy, TensorFlow y Keras, PostgreSQL,
Docker y las configuraciones existentes de Render y Supabase. Alembic añade la
gestión de cambios del esquema sobre la misma base de datos.

c) El autor confirmó que todos los servicios actuales son gratuitos. El gasto
recurrente declarado es Q0.00 / US$0.00. No se contrataron servicios ni se comprobó
facturación desde los paneles de los proveedores. No se declara un dominio propio
pagado ni un disco persistente contratado. Los presupuestos históricos se
diferencian de estos gastos reales declarados.

d) No se ejecutaron migraciones sobre la base de producción, no se publicaron
cambios y no se tocaron datos reales. Las bases nuevas pertenecen al contenedor
`senda_fase0_postgres`, con PostgreSQL 16 y acceso local en el puerto 55432.

## 2. Revisión y entorno

El repositorio efectivo está dentro de `Sistema-Rutinas-PG`; la carpeta superior
tiene otro repositorio que solo ve este árbol como contenido no registrado.
La revisión de referencia del repositorio efectivo es
`f81d6ea0c3481e00c882b0ff7e1be8d259aed78f`, del 22 de septiembre de 2026.
El estado de trabajo contiene modificaciones posteriores que no están en ese
commit y no se descartaron ni se incorporaron a un commit durante esta fase.

Al comenzar ya existían cambios de informes y navegación en la API, el cliente,
sus dependencias y varios documentos. Entre los archivos modificados estaban
`backend/app/main.py`, `backend/app/api/v1/__init__.py`, `backend/pyproject.toml`,
`backend/uv.lock`, `frontend/src/App.jsx`, `ArmazonAdmin.jsx`, `Pildoras.jsx`,
`secciones.js`, `pantallas.css`, `AjustesCuenta.jsx` y `servicios/api.js`; también
había archivos nuevos de informes, pruebas, presentaciones y entregas de tesis.
Por ello el commit por sí solo no reproduce el estado comprobado.

El documento académico de referencia continúa siendo
`Tesis Final/Leonardo Zepeda - Proyecto de Graduacion II - Entrega 3 (667 pruebas).docx`,
modificado el 23 de octubre de 2026. No se editó ese DOCX; el registro de cambios
que deben trasladarse está en [CAMBIOS_TESIS_FASE_0.md](CAMBIOS_TESIS_FASE_0.md).

| Componente local | Versión comprobada |
|---|---|
| Sistema | Windows, ejecución de Python nativa |
| Python | 3.12.15 |
| FastAPI | 0.141.1 |
| SQLAlchemy | 2.0.51 |
| TensorFlow y Keras | 2.21.0 y 3.15.1 |
| NumPy | 2.5.2 |
| psycopg | 3.3.5 |
| pytest | 9.1.1 |
| Alembic, incorporado en esta fase | 1.20.1 |
| Vite y complemento PWA | 6.4.3 y 1.3.0 |
| PostgreSQL del ensayo | Rama 16, imagen `postgres:16-alpine` |

El entorno existente recibió Alembic y sus dependencias Mako y MarkupSafe. El
archivo de bloqueo conserva versiones resueltas; no se propuso sustituir el motor
neuronal ni actualizar sus bibliotecas para resolver avisos de obsolescencia.

## 3. Comprobaciones realizadas

| Comprobación | Resultado | Alcance y límite |
|---|---|---|
| Batería original del servidor | **667 aprobadas**, cero fallos | 265.66 segundos. Bases SQLite temporales; incluye las pruebas de entrenamiento neuronal. |
| Migraciones | **19 aprobadas, una omitida**, cero fallos | 20 casos recogidos: diez sobre SQLite y diez sobre PostgreSQL 16. La omitida verifica enumeraciones nativas y no aplica a SQLite. |
| Pruebas de despliegue, repetidas tras los cambios | **32 aprobadas**, cero fallos | Son un subconjunto de las 667 originales, no 32 casos nuevos. No prueban una publicación en Render. |
| Construcción del cliente | **Correcta**, incluida PWA | Se repitió después de corregir la conexión predeterminada. No acredita el comportamiento visual. |
| Compatibilidad del bloqueo con uv de Docker | **Exportación correcta con uv 0.5.11** | Lectura congelada y sin red del archivo actualizado. No equivale a construir o desplegar la imagen completa. |
| Recorridos de API sobre PostgreSQL | **45 comprobaciones correctas** | 28 antes y 17 después de restaurar, incluidas respuestas de rechazo esperadas. |
| Respaldo y restauración | **Contenido idéntico en quince tablas** | Comparación de filas y SHA-256 con datos ficticios; además se verificaron secuencias. |
| Revisión de esquema restaurado | **Cero diferencias** | Revisión `0001_esquema_inicial`, comprobada también con la herramienta de administración. |
| Revisión visual de escritorio y tamaños móviles | **Pendiente** | El navegador rechazó la autorización para abrir el entorno local. No se intentó otra vía de navegación. |
| Cincuenta usuarios concurrentes, comprobación local posterior | **No cumple en el ensayo realizado** | Se prepararon las cincuenta cuentas ficticias. Las seis operaciones superaron el umbral informado y hubo fallos en rutina, menú y registro de progreso. Investigar antes de afirmar cumplimiento. |
| Teléfono físico y tercera generación | **Pendiente** | Los resultados locales anteriores no sustituyen esas mediciones. |
| Despliegue actual y esquema productivo | **Sin certificar en esta fase** | No se accedió a paneles ni se migró producción. |

La generación de un plan con el modelo neuronal ya cargado tardó **0.5464 s** en
una comprobación local contra PostgreSQL. Es una observación individual, sin
latencia de red móvil ni concurrencia; no demuestra un percentil de servicio ni
el cumplimiento en producción. La carga inicial de TensorFlow se realizó aparte.

Se registraron avisos de obsolescencia de Starlette/httpx y de Keras/NumPy durante
las pruebas; no produjeron fallos. Se deja su evaluación para un incremento de
dependencias con regresión específica, sin mezclarla con el rediseño del producto.

## 4. Recuperación comprobada

Se crearon las bases `senda_fase0_origen_02f425069422` y
`senda_fase0_restaurada_02f425069422`, ambas locales y con datos ficticios.
El volcado personalizado PostgreSQL ocupó 60,703 bytes. Se restauró en una base
nueva mediante una transacción y detención ante errores; no se reemplazó ninguna
base previa.

Antes de modificar nuevamente la base restaurada, se verificó igualdad del
contenido completo de las quince tablas. A continuación se consultó la API y se
insertó una cuenta ficticia adicional para comprobar la continuidad de los IDs.
Las huellas documentan el instante de comparación: no se espera que sigan siendo
iguales después de los accesos y de las inserciones de comprobación.

El recorrido cubrió registro, acceso, rechazo de edad menor de 18, perfil, plan,
rutina, menú, compras, apertura y registro de sesión, progreso, recompensas,
informes en pantalla y descargas CSV, Excel y PDF. También comprobó falta de
sesión, denegación del área administrativa a un usuario, aislamiento de una sesión
de entrenamiento entre cuentas y rechazo del plan ante una condición excluida.

La reproducción está en [MIGRACIONES.md](MIGRACIONES.md) y en
`ensayar_fase0.py`. El ensayo conserva bases y respaldo para inspección y no se
presenta como validación de todos los procedimientos de recuperación productivos.

## 5. Cambios concretos de esta fase

a) Alembic, configuración, revisión inicial estática y comandos `estado`,
`comprobar`, `adoptar` y `actualizar`. La adopción rechaza estructuras distintas
y conserva los datos de negocio. La imagen Docker está preparada para incluirlos;
el arranque productivo conserva su mecanismo previo durante la transición.

b) Pruebas de creación desde cero, incorporación de una base poblada,
idempotencia, rechazo de actualización sin versión, diferencias de columna e
índice, valores enumerados nativos y reversión/recreación en bases desechables.

c) Corrección del cliente: sin `VITE_URL_API` se utilizaba
`http://localhost:8000/api/v1`; ahora se usa `http://127.0.0.1:8010/api/v1`,
coherente con `.env.example`, la guía y los puertos de desarrollo existentes.
El valor configurado expresamente en un despliegue sigue teniendo prioridad.

d) Correcciones de documentación: nombre elegido, interfaz sin Bootstrap,
versionado del modelo entrenado, costos gratuitos declarados y enlace al estado
actual desde el plan histórico. La tesis y los resultados históricos se conservan.

e) Evidencias locales excluidas de Git para evitar incorporar respaldos o
capturas con datos personales en trabajos posteriores.

## 6. Divergencias y decisiones pendientes

| ID | Divergencia o límite | Tratamiento |
|---|---|---|
| D-01 | El plan histórico declara despliegue pendiente; la tesis posterior documenta una dirección pública. | Se añadió contexto al plan. Confirmar la publicación actual antes de declararla vigente. |
| D-02 | README declaraba Bootstrap y modelo no versionado. | Corregido para reflejar CSS propio y artefacto neuronal versionado. |
| D-03 | La guía mezclaba gastos estimados de alojamiento pago con servicios actuales gratuitos. | Se corrigió el estado declarado. Trasladar la distinción al presupuesto y a la operación de la tesis. |
| D-04 | El cliente usaba otro puerto en ausencia de configuración. | Corregido y compilado. Recorrido visual pendiente de autorización del navegador. |
| D-05 | RN-01 dice «mayores de dieciocho»; la validación admite edad igual a 18. | Aclarar redacción como «18 años cumplidos o más» si ese es el alcance académico. No se modificó la regla de código. |
| D-06 | RN-03 describe proteína por peso corporal; las salvaguardas ajustan por peso de referencia y proporción energética. | La tesis debe distinguir cálculo de referencia y plan corregido. No se cambiaron fórmulas ni reglas clínicas. |
| D-07 | RN-04 habla de incremento de volumen; la progresión acota principalmente la carga en kg y la interfaz habla de peso. | Definir y documentar la magnitud exacta antes de afirmar equivalencia entre carga y volumen. No se alteró la prescripción. |
| D-08 | La respuesta de rutina muestra `volumen_de_referencia(perfil)` aunque la generación puede usar la salida neuronal. | Resolver la persistencia o la presentación del valor antes de ampliar el motor. No inventar una salida histórica del modelo. |
| D-09 | La lista histórica de pendientes no refleja todas las condiciones y lesiones ya implementadas. | Registrar lo existente; alergias e intolerancias alimentarias siguen siendo una ampliación distinta. |
| D-10 | Los catálogos iniciales son provisionales: 25 ejercicios y 36 alimentos. | Mantener identificación provisional hasta contar con levantamiento de campo, fuentes y fechas. |
| D-11 | PWA conserva el armazón; no equivale a rutina disponible sin conexión. | Mantener el límite actual de la tesis y tramitar la ampliación en su fase posterior. |
| D-12 | La creación automática de tablas no gestiona cambios de columnas existentes. | Se preparó Alembic. Incorporar los entornos existentes y cambiar el arranque en una entrega controlada. |
| D-13 | El plan cita numeraciones de tablas de versiones anteriores de tesis. | Usar los apartados y tablas del DOCX de referencia al hacer la actualización académica. |
| D-14 | La plantilla gratuita no habilita el disco persistente, mientras partes de la guía describen un modelo reentrenado en disco. | Confirmar la persistencia real antes de afirmar que ese artefacto sobrevive a reinicios o nuevas publicaciones. La imagen sí incluye el modelo inicial versionado. |

Estas divergencias son hallazgos de consistencia y límites de verificación; no
constituyen por sí mismos un dictamen clínico ni una auditoría completa de seguridad.

## 7. Alcance delimitado para el siguiente incremento

La fase 1 se centra en la identidad **Senda**, tres propuestas de símbolo,
portada pública, primer uso y nuevo inicio. Mantiene la base tecnológica actual.
No incluye sustituir autenticación, migrar de proveedor, introducir 3D, abrir
ligas públicas ni generar planes de tratamiento médico.

Antes de alterar datos persistentes se utiliza el procedimiento de migración;
antes de ampliar comidas se define el tratamiento de restricciones alimentarias.
Se conservan HU, RN y RE existentes, y se registran ampliaciones con identificadores
nuevos en el plan maestro.

## 8. Pendientes para cerrar toda la fase 0

a) Completar la revisión visual en navegador y un teléfono físico, con cuenta de
demostración y tareas registradas. La denegación de acceso al navegador impidió
obtener capturas en esta sesión; no se presenta emulación como teléfono real.

b) Comprobar la configuración y versión publicadas, medir arranque en frío,
tercera generación y concurrencia. No aplicar migraciones a producción sin el
respaldo real y el ensayo correspondiente a su esquema.

c) Revisar las divergencias D-05 a D-08 con las definiciones del proyecto y
trasladar las correcciones documentales al DOCX en una copia versionada.

d) Revisar el cambio completo en Git, conservar las modificaciones anteriores
del autor y registrar un incremento identificable antes de su despliegue.

## 9. Evidencia y reproducción

Evidencia local, bajo `operaciones/evidencias/fase0/`:

a) `pruebas-base.xml`: 667 casos originales ejecutados el 29 de octubre.

b) `pruebas-migraciones.xml`: resultado final de los veinte casos recogidos.

c) `pruebas-despliegue.xml`: repetición de los 32 casos de ese módulo.

d) `recuperacion-y-recorridos.json`: respuestas esperadas y obtenidas, tiempos,
huellas, conteos y revisión. No contiene tokens ni contraseñas.

e) `recuperacion-ficticia.dump`: respaldo del conjunto ficticio.

f) `manifiesto-linea-base.json`: commit de referencia, versiones y huellas de
179 archivos del estado de trabajo, incluido el DOCX conservado. Identifica el
contenido comprobado con sus cambios locales; no sustituye un commit ni un respaldo.

g) `requirements-docker.txt`: exportación congelada con la versión de uv que
utiliza el Dockerfile, como comprobación de lectura del bloqueo actualizado.

Los comandos de construcción son `npm run build` desde `frontend`; los de
regresión, `uv run pytest -q` desde `backend`. Para incluir los casos PostgreSQL,
configurar la conexión de pruebas según `MIGRACIONES.md`. Los resultados de este
informe corresponden a ejecuciones separadas y no se deben sumar como si fueran
una única nueva batería completa.

## 10. Estado al cerrar el chat

El autor indicó que continuará en otro chat. La fase 0 permanece abierta.
El navegador integrado siguió rechazando `http://127.0.0.1:15173` por un permiso
guardado o una política administrada, incluso después de ampliar el acceso general
del entorno. Edge no apareció entre los navegadores conectados. No se realizó
la comprobación visual ni se cambió de superficie para eludir el bloqueo.

Mientras se revisaban esos permisos se ejecutó `prueba_de_carga.py --usuarios 50
--url http://127.0.0.1:18110` contra la base ficticia local. La salida se conserva
en `evidencias/fase0/carga-local-50.txt`; terminó con código 1. La herramienta
informó tiempos p95 de 26.09 s para generar plan, 15.35 s para rutina, 33.00 s
para menú, 33.08 s para progreso, 6.28 s para reporte y 2.32 s para historial.
Registró, respectivamente, 0, 1, 11, 18, 0 y 0 fallos. Son cifras del instrumento
existente, con un proceso Uvicorn y PostgreSQL local, no resultados de producción.
La duración que imprime ese instrumento incluye la preparación de cuentas.

No se investigó ni corrigió todavía la causa de la degradación. El siguiente
chat debe revisar los errores del servidor y el método de medición antes de
repetir la carga, conservar la evidencia de este intento y reflejar su resultado
en la actualización de la tesis. Las 667 pruebas funcionales aprobadas siguen
siendo un resultado distinto; no acreditan el rendimiento concurrente.

Retomar desde este informe, el registro de cambios de tesis y el plan maestro.
Mantener Docker y la arquitectura existente, el nombre Senda y los servicios
gratuitos declarados. No hay publicación ni migración de producción realizada.
