# Fase 7: validación de la entrega individual

30 de octubre de 2026, Guatemala. **Fase en ejecución; entrega técnica local.**
Por decisión del autor, amigos, grupos, invitaciones y retos colectivos quedan
pospuestos. La validación actual se concentra en cuenta, planes, entrenamiento,
alimentación y Mi senda individual. No depende de terminar el piloto social.

No se realizó evaluación con personas, teléfono físico, revisión profesional,
envío real de Gmail ni publicación. El autor confirmó que todavía no dispone
de esos recursos. El avance técnico no equivale a cerrar toda la fase 7.

## Alcance individual aplicado

- Se retiraron «Con amigos» de Avance y Más y la carga del módulo social del
  cliente. `/avance/amigos` lleva a `/avance/senda` para conservar los enlaces
  anteriores. La página pública antigua `/comunidad` presenta Mi senda individual.
- La API social responde 404 y no figura en OpenAPI con la configuración actual.
  `COMUNIDAD_HABILITADA=false` es el valor predeterminado. Registrar entrenamiento
  no invoca ni escribe eventos sociales en este estado.
- Puntos, niveles, insignias, rachas y registros individuales conservan sus reglas
  y sus datos. No se trasladaron puntos colectivos a Mi senda ni se recalibraron
  premios. El navegador mostró los **185 puntos anteriores y Primer paso** de la
  cuenta ficticia usada en fase 6, sin ofrecer grupos.
- El código del piloto social, sus pruebas aisladas y la migración 0005 se
  conservan como antecedentes. No se borraron tablas ni datos. Mantener la revisión
  del esquema en 0005 no implica que la función social esté disponible.

## Rendimiento: cambios y evidencia completa

La generación de una sola entrada usaba `model.predict`, que prepara el mecanismo
de lotes. Se utiliza `model(entrada, training=False)`, conservando pesos,
normalización, redondeo, fórmulas y memoria de predicciones. La [documentación
oficial de Keras](https://keras.io/api/models/model_training_apis/#predict-method)
recomienda la llamada directa para entradas pequeñas. La equivalencia se comprobó
con seis perfiles y el modelo versionado real; otra prueba comparó las respuestas
en ejecución concurrente. Esto no constituye validación clínica del modelo.

La API limita las solicitudes activas que usan la base a **cinco por proceso**,
igual que las conexiones persistentes del pool actual. Las restantes esperan
asíncronamente, antes de ocupar un hilo o conexión. Los máximos de la base no se
aumentaron: cinco persistentes más cinco de desbordamiento. Salud y preflight
permanecen fuera de esta espera. `SOLICITUDES_ACTIVAS_BD` permite de 1 a 10;
el valor comprobado final es 5. La comparación entre ensayos sugiere menor
contención; no identifica por sí sola la causa exacta de la degradación histórica.
Referencias: [pool de SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/pooling.html)
y [hilos de Starlette](https://www.starlette.io/threadpool/), consulta 30-10-2026.

Se corrigió `prueba_de_carga.py`: cuentas únicas por ejecución, preparación y
calentamiento separados, p95 por rango más cercano, tiempos y clases de fallos
sin cuerpos ni tokens, denominadores completos y archivo JSON. La versión 3 exige
cero fallos, todas las cuentas solicitadas y **cada petición observada** dentro
del límite. Un p95 adecuado no oculta una petición lenta. No se cambian los
límites de 3 s para plan/progreso y 2 s para consultas del instrumento.

Escenario: 50 cuentas ficticias, seis operaciones en secuencia por cuenta,
300 solicitudes HTTP en total, un proceso Uvicorn, PostgreSQL 16 en Docker local
y el modelo cargado. Las 50 cuentas inician su recorrido simultáneamente; no
significa 50 instrucciones SQL ejecutándose al mismo tiempo. El tiempo medido
incluye la espera de admisión de la API. Se reinició el servidor entre escenarios
para no reutilizar todas las predicciones del ensayo previo. Una entrada se
repite por el calentamiento; las restantes son diferentes en cada recorrido.
No se simula red 3G ni se mide Render/Supabase.

| Ensayo (archivo JSON) | Configuración | p95 plan | p95 menú | Máximo menú | Evaluación estricta de la evidencia |
|---|---|---:|---:|---:|---|
| `carga-antes.json` | predict; sin admisión | 3.29 s | 4.44 s | 6.03 s | No cumple todos los límites |
| `carga-inferencia.json` | llamada directa; sin admisión | 2.14 s | 2.46 s | 3.60 s | No cumple todos los límites |
| `carga-final.json` | admisión 8, ensayo 1 | 1.74 s | 1.08 s | 1.16 s | Dentro de límites en ese ensayo |
| `carga-validacion-final.json` | admisión 8, repetición | 1.91 s | 3.84 s | 4.32 s | No cumple todos los límites |
| `carga-cinco.json` | admisión 5, ensayo 1 | 1.77 s | 0.95 s | 0.98 s | Dentro de límites en ese ensayo |
| `carga-cinco-repeticion.json` | admisión 5, repetición | 2.27 s | 1.74 s | 2.21 s | No cumple todos los límites |

Las tres primeras evidencias usan el instrumento v2; las tres siguientes usan v3. La evaluación de esta tabla se recalculó con el criterio estricto para todas las filas, sin modificar sus archivos originales. Todos prepararon 50 cuentas y obtuvieron 300 respuestas sin errores HTTP.

| Operación, configuración final 5 (repetición) | p95 | Máximo | Límite |
|---|---:|---:|---:|
| plan | 2.27 s | 2.46 s | 3 s |
| rutina | 1.50 s | 1.64 s | 2 s |
| menu | 1.74 s | 2.21 s | 2 s |
| progreso | 2.64 s | 2.70 s | 3 s |
| reporte | 2.27 s | 2.39 s | 2 s |
| perfil | 1.37 s | 2.01 s | 2 s |

**Conclusión de rendimiento: mejora local, sin cumplimiento estable acreditado.**
La repetición con cinco solicitudes activas completó 300 respuestas sin errores,
pero excedió 2 s en menú, reporte e historial. Se conservan todos los ensayos,
incluidos los favorables y los fallidos. No seleccionar solo un resultado
favorable para cerrar el requisito de cincuenta usuarios.

## Arranque y primera generación

`medir_arranque_fase7.py` creó un proceso propio local y lo cerró al finalizar.
Salud respondió a los **4.93 s** desde la creación del proceso. El primer plan
tardó **7.46 s**, con origen `red_neuronal`; el siguiente, **0.043 s**. Ambos
devolvieron 201. El primer plan **no cumple el límite de 3 s**. La carga inicial
del modelo sigue siendo un pendiente; no se eliminó de la evidencia ni se cambió
por una fórmula para aparentar cumplimiento. La caché de archivos del sistema
operativo no se controló: es un ensayo de proceso nuevo, no de máquina recién
encendida. Evidencia: `arranque.json` y `servidor-arranque.log`.

## Integridad, recuperación y pruebas

Suite completa con la configuración final (admisión 5 y comunidad apagada):
**812 aprobadas, 4 omitidas**, cero fallos, **268.84 s**, en
`evidencias/fase7/suite-configuracion-final.xml`. Incluye SQLite y PostgreSQL
local. Las cuatro omisiones son casos específicos de concurrencia o enumeraciones
que no corresponden al recorrido SQLite. Se mantienen los avisos de obsolescencia
previos de Starlette y Keras/NumPy; no causaron fallos.

La suite anterior con admisión 8 (`suite-final.xml`, 812 aprobadas y 4 omitidas,
276.34 s), la focalizada de retiro social (55 aprobadas) y la focalizada de
optimización (12 aprobadas) son ejecuciones separadas. No se suman a la suite final.
El manifiesto tras retirar accesos sociales contiene 263 archivos y queda en
`estado-tras-retiro-social.json`; ninguno falta al comprobarlo al final. El primer
intento de manifiesto (`estado-inicial.json`) quedó vacío y no se usa como prueba
de conservación ni como inventario del estado previo.


Se comprobó el retiro social, falta de acceso a rutas desactivadas, lectura de
puntos propios y aislamiento entre cuentas. Los tests del piloto social se
ejecutan habilitándolo solo dentro de su fixture; no reactivan la entrega normal.
Las pruebas del límite asíncrono cubren cola, respuesta sin alterar, salud durante
saturación, liberación por excepción y cancelación. Los tests del instrumento
comprueban muestra incompleta, errores, percentil y un valor extremo que no puede
ocultarse con el p95. No se hicieron nuevas migraciones ni cambios de dosis.

`ensayar_respaldo_fase7.py` respaldó la base ficticia identificada en
`evidencias/fase7/base-ui.txt`, la restauró en otra base nueva y comparó filas y
SHA-256 de las **25 tablas de negocio**: idénticas en ese instante. Revisión
`0005_comunidad_privada`, cero diferencias de esquema y secuencia de usuarios
correcta. Respaldo: **171,791 bytes**. Se verificaron después plan, rutina, menú,
Mi senda y bitácora, y el 404 social. La comparación precede a esas consultas;
el inicio de sesión posterior puede modificar último acceso. No se restauró
sobre una base anterior ni se eliminó la fuente. Evidencia: `restauracion.json`
y respaldo `.dump` local, excluidos de Git. Los ensayos de carga posteriores
añadieron cuentas ficticias a la fuente; no se afirma igualdad después de ellos.

## Revisión de interfaz y construcción

Navegador integrado con cuenta ficticia, sobre la base de fase 6 conservada:
redirección de la ruta antigua a Mi senda, 185 puntos y una insignia anteriores,
cinco pestañas de Avance sin «Con amigos» y Más sin acceso a grupos. Revisados
modo claro y oscuro. Mi senda no mostró desbordamiento horizontal en 320, 1280
y 1920 px (anchos de contenido observados: 305, 1265 y 1905 px). Es una revisión
parcial de escritorio con cambios de tamaño; no acredita todos los recorridos
ni el uso de un teléfono físico. Los tamaños temporales se restauraron.

Cliente: 21 pruebas de entrenamiento y 11 de interacción aprobadas. Construcción
y verificador correctos; diez páginas públicas y seis armazones privados sin
datos. El artefacto final no contiene el módulo `ComunidadPrivada` ni su hoja de
estilos separada. Se conservaron las fuentes del piloto, sin importarlas.
Capturas bajo `evidencias/fase7/senda-individual-*.png`.

## Pendientes para cerrar la fase

| Trabajo | Situación y condición de cierre |
|---|---|
| Carga de 50 usuarios | Pendiente de estabilidad: conservar fallos de tiempo, perfilar espera/SQL, revisar capacidad real y comprobar el entorno publicado. |
| Primera generación desde proceso nuevo | 7.46 s observados; resolver o documentar la limitación antes de declarar el requisito cumplido. |
| Participantes | No disponibles. Usar [guion individual](PILOTO_INDIVIDUAL_FASE7.md), medir tareas sin ayuda y primer plan completo; ninguna sesión ficticia cuenta como persona. |
| Observación | Cuatro semanas aún no iniciadas. Definir denominadores, exclusiones y fechas con el responsable; no atribuir adherencia o causalidad sin datos. |
| Teléfono y red móvil | No disponibles. Probar dispositivo real, temporizador, interrupciones, instalación y conexión; emulación no acredita estas condiciones. |
| Gmail | Sin cliente OAuth ni autorización; entrega y recuperación real pendientes. |
| Ejercicios y recetas | Revisión documental preparada; dictamen profesional, plancha y tolerancias pendientes. |
| Accesibilidad | Revisión parcial; faltan lector de pantalla y recorridos completos con usuarios. |
| Publicación | Ninguna en este incremento. Respaldar y verificar entorno de pruebas antes de migrar/publicar; conservar comunidad apagada. |
| Tesis | [Cambios y texto propuesto](CAMBIOS_TESIS_FASE_7.md) preparados; DOCX de referencia intacto. Falta copia versionada, integración y revisión visual. |

Los informes de fases 0–6 son evidencia histórica. Este cambio de alcance no
cierra sus pendientes externos. Los grupos podrán reconsiderarse en otra entrega,
sin ser una condición para validar el producto individual actual.
