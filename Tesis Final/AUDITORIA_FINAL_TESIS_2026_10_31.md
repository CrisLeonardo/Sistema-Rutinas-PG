# Auditoría final de la tesis — 31 de octubre de 2026

Documento auditado: `Leonardo Zepeda - Proyecto de Graduacion II - Entrega 3 (verificada PostgreSQL).docx`
(carpeta Descargas, guardado por el autor el 30-10-2026 a las 16:53, revisión 8). Es el DOCX más
reciente; se comparó párrafo por párrafo con la referencia de 667 pruebas
(`Tesis Final/... Entrega 3 (667 pruebas).docx`, 23-10-2026), que no se modificó.

Esta auditoría no modifica ningún DOCX. Cada punto indica el apartado, lo que dice hoy y lo que
corresponde según el sistema ejecutado el 31-10-2026. Las ubicaciones se dan por apartado porque la
paginación cambia al actualizar campos.

## A. Decisiones que solo puede tomar el autor (con su asesora)

**A-1. Cuál archivo se entrega.** La versión más reciente está en Descargas, no en `Tesis Final`.
Copiarla a `Tesis Final` con un nombre versionado antes de seguir editando.

**A-2. El tono de la versión «verificada PostgreSQL» cambia el resultado de la tesis.** Frente a la de
667 pruebas, reemplaza o elimina 172 párrafos y filas de tabla y agrega o reescribe 187. Entre otros cambios:

- Capítulo VII y Anexo 3: «la hipótesis se acepta» pasó a «La evidencia sostiene una comparación
  técnica … no la aceptación de la hipótesis para la población». La tabla de comprobación marca
  «Pendiente», «En perfiles sintéticos» y «Limitado al experimento» donde antes decía «Se cumple».
- 4.10.3 Factibilidad operativa: la anuencia del gimnasio pasó de «Favorable» a «Pendiente de
  confirmación». Si el gimnasio sí dio su anuencia (la versión anterior lo afirmaba), la nueva
  redacción es inexacta y perjudica la factibilidad. Si no la dio, la anterior era la inexacta.
- Muchos párrafos describen la tesis como bitácora interna: «versión local» (19 veces), «no se volvió
  a comprobar para esta versión», «Evidencia de la entrega anterior», «no se deben sumar estas
  cifras», «el responsable debe iniciar la interfaz y los servicios». Es lenguaje de auditoría, no de
  informe final: un lector concluye que el sistema no está verificado.

Recomendación: conservar la honestidad sobre los límites (perfiles sintéticos, sin participantes,
primera generación lenta en arranque en frío), pero concentrarla en un apartado de limitaciones y
redactar resultados y conclusiones en registro académico. Decidir con la asesora si la hipótesis se
declara aceptada con limitaciones o no comprobada; las dos versiones actuales se contradicen.

## B. Afirmaciones que ya no coinciden con el sistema

**B-1. Publicación y dominio (5.2, 6.1, Anexo 4 §2 y su introducción, Anexo 6 §5, Anexo 3 objetivo b).**
La tesis dice que los incrementos de octubre «no se han publicado» y que la dirección es
`https://rutinas-interfaz.onrender.com`, «no comprobada». Hoy `https://senda-gt.onrender.com`
responde 200, su API `/api/v1/estado` responde «disponible» y sirve el código del commit `a87f1fe`
(textos «Conectando con Senda», recuperación, recetas). La dirección antigua también responde.
Corresponde: indicar `senda-gt.onrender.com` como dirección vigente, la fecha de publicación y los
datos de su certificado. **Antes de afirmarlo, comprobar que el inicio de sesión funciona en
producción** (ver informe del sistema, hallazgo S-1): la base de producción no tiene registradas las
migraciones 0002–0005.

**B-2. Recuperación por correo.** Superado por la decisión E-2: queda fuera del alcance. (En local,
con un servidor SMTP de prueba, el recorrido funcionó: correo, enlace de un uso, 15 minutos,
rechazo al reutilizarlo y revocación de la sesión anterior; no se publica sin proveedor de correo.)

**B-3. Cifras de pruebas (6.3 y Anexo 5 §7).** Dice «21 pruebas de entrenamiento y 11 de interacción»
y «Las 32 pruebas de cliente». Al 31-10 el cliente tiene 69 pruebas (36 + 11 + 14 + 8) y, con las
correcciones de esta auditoría, 74. La suite del servidor se reprodujo hoy: 812 aprobadas y 4
omitidas con PostgreSQL 16 (231.97 s), igual que la cifra de la tesis; con las correcciones queda en
825 aprobadas y 4 omitidas. Mantener 667 como ejecución histórica y no sumar.

**B-4. Manual de usuario, textos de pantalla.**

| Apartado | Dice | La aplicación muestra |
|---|---|---|
| Anexo 4 §2 c | toque «Entrar» | botón «Entrar a mi día» |
| Tabla 114 | «Demasiados intentos fallidos. Espere unos minutos antes de volver a intentarlo.» | «Demasiados intentos fallidos. Espere 15 minutos antes de volver a intentarlo.» |
| Tabla 114 | «El servidor tardó demasiado en responder.» | «La consulta tardó demasiado. Vuelva a intentarlo en un momento.» (consultas) o «No recibimos la confirmación a tiempo…» (envíos) |
| Tabla 114 | «No se pudo comunicar con el servidor.» | igual, más «Verifique su conexión e intente de nuevo.» |

**B-5. Manual §6, semana de comidas (después de la corrección S-3).** Añadir: el día en que se prepara
la semana es el Día 1, el botón del día actual dice «· hoy» y el Menú muestra la comida de ese día.
Antes de la corrección el Menú mostraba siempre el Día 1.

**B-6. Interfaces y datos (5.3.3.2, 5.4.3).** La tabla de rutas documenta 40 rutas en 11 enrutadores
como «histórica». La versión publicada expone 50 rutas activas en 12 enrutadores más la de estado
(la API social está apagada) y 25 tablas de negocio más `alembic_version`. Para una entrega final
conviene actualizar la tabla y el diccionario en lugar de remitir a «la documentación local».

**B-7. RN-01 y RE-01.** RN-01 dice «desde los 18 años cumplidos»; RE-01 y el mensaje de la pantalla
dicen «mayores de dieciocho años». El sistema acepta 18 años (comprobado). Unificar la redacción.

## C. Formato y aparato crítico

**C-1. Índice de figuras desactualizado.** Hay 86 figuras en el cuerpo y 85 en el índice; 12 entradas
no coinciden (42, 43, 44, 45, 46, 57, 63, 65, 83, 84, 85 y falta la 86). Ejemplo: el índice dice
«Figura 44. Prototipos de las pantallas principales…» y el cuerpo «Figura 44. Pantalla Hoy de la
versión local de Senda». Solución: clic derecho sobre el índice de figuras → Actualizar campo →
Actualizar toda la tabla; luego lo mismo con el índice general y el de tablas.

**C-2. Referencias sin cita.** Tres referencias quedaron sin cita en el texto porque la reescritura de
6.3.3.1 las retiró: Administración de Alimentos y Medicamentos de los Estados Unidos (2024), Field
(2024) y Servicio Nacional de Salud del Reino Unido (2023). APA exige que toda referencia se cite:
restituir las citas (plan genérico de 2,000 kcal, valores orientativos por sexo y prueba de
Wilcoxon) o retirar las referencias.

**C-3. Comprobado sin observaciones.** Márgenes 2.5/2.5/3/2.5 cm; Normal en Times New Roman 12 con
interlineado 1.5; 120 tablas y 86 figuras numeradas sin saltos ni duplicados y todas con «Fuente»;
305 encabezados coinciden con el índice general; ningún encabezado seguido de otro; 65 referencias,
62 de 2021 o posteriores (las antiguas: plan municipal 2018 y guía de Scrum 2020, la vigente); las
81 citas del texto tienen referencia; sin «¡Error! No se encuentra el origen de la referencia».

## D. Lo que la tesis afirma y sí funciona (comprobado en el sistema el 31-10-2026)

Registro con validación (correo, 8 caracteres con letra y número), acceso y cierre de sesión,
bloqueo tras 8 intentos fallidos durante 15 minutos, revocación del token al cambiar la contraseña,
perfil en cuatro pasos con rechazo de menores (17 rechazado, 18 aceptado) y rangos de peso y
estatura, plan con red neuronal (0.11 % frente a las fórmulas, aviso profesional), menú con
sustitutos equivalentes, semana con recetas, restricciones (alergia al maní y alimento evitado
excluidos en los siete días), cambio de comida recalculado, recetas, lista de compras con marcas
persistentes, rutina por días sin grupos consecutivos, sesión en curso sin barra de navegación,
cronómetro de descanso, puntos e insignias al guardar, bitácora, marcas, 25 guías de ejercicio,
avance semanal con reajuste explicado, Mi senda, evolución, historial de medidas, cuatro informes
personales y ocho del administrador en pantalla, Excel, CSV y PDF, tema claro y oscuro, lesión de
rodilla que retira sentadilla, prensa y zancadas, condición médica que bloquea plan, menú, semana y
rutina, administración de catálogos y cuentas con sus protecciones, diez páginas públicas, video de
30 s, iconos y manifiesto de instalación, y redirección de `/avance/amigos`.

## E. Decisiones del autor del 31-10-2026 y su efecto en la tesis

El autor decidió **descartar** Gmail (recuperación por correo), la prueba en teléfono físico y la
evaluación con participantes, y declaró **realizadas** en octubre de 2026 la revisión profesional
(un nutricionista: 18 recetas y composición de los 36 alimentos; un entrenador del Gimnasio FAMAS:
25 guías de ejercicio y dosis de la plancha de 20–30 s) y el levantamiento de precios en los
mercados de El Progreso. Por decisión del autor, los revisores se citan por rol, sin nombres. El
sistema ya refleja estas decisiones (rama `auditoria-final-sistema`). En la tesis, lo descartado no
debe aparecer como «pendiente», sino como **fuera del alcance** (limitación declarada o trabajo
futuro). Lo revisado deja de ser «provisional».

**E-1. Revisión profesional y precios: retirar «pendiente» y «provisional».**

| Apartado | Dice (extracto) | Proponer |
|---|---|---|
| 1.2 Justificación | «catálogos propuestos para el contexto local; su disponibilidad y contenido todavía requieren verificación de campo y revisión profesional» | «catálogos del contexto local, con precios levantados en los mercados de El Progreso y contenido revisado por profesionales (octubre de 2026)» |
| 4.1.1 Descripción del producto | «El catálogo emplea alimentos y ejercicios propuestos… requieren aún comprobación de campo y r[evisión]» | Catálogo con precios de campo y revisión de un nutricionista y de un entrenador del Gimnasio FAMAS |
| 5.4.3.8 Ejercicios de la sesión | «La referencia de duración y sus series son provisionales y están pendientes de revisión profesional» | «La duración de 20–30 s por serie fue revisada por un entrenador del Gimnasio FAMAS» |
| 6.3.3.2 Rutina | «la dosis de la plancha en segundos es provisional y requiere revisión pr[ofesional]» | Igual que la fila anterior |
| 6.3.4 Catálogo | «Su disponibilidad local, precios y contenido deben confirmarse mediante trabajo de campo y revisión profesional» | Indicar el levantamiento de precios y la revisión |
| 6.3.4.2 Menú | «Los precios del catálogo son estimaciones provisionales y no acreditan un levantamiento de mercado» | «Los precios provienen del levantamiento en los mercados de El Progreso (octubre de 2026)» |
| 7.1 b, 7.2 c | «la disponibilidad, precios y contenido… siguen pendientes de levantamiento de campo y revisión profesional» | Conclusión afirmativa con la revisión y el levantamiento |
| 8.1 b Recomendaciones | «Completar el levantamiento de campo del catálogo…» | «Actualizar periódicamente los precios del catálogo…» |
| Anexo 3, objetivos del producto c | «disponibilidad, precios y revisión profesional pendientes» | Evidencia: levantamiento y revisión |
| Anexo 4 §6 | «Las recetas y precios son provisionales y están pendientes de revisión profesional y de campo» | «Las recetas fueron revisadas por un nutricionista y los precios se levantaron en los mercados de El Progreso» |
| Anexo 4 §7 | «la referencia de plancha es provisional y requiere revisión» | Retirar la advertencia |

Conviene añadir en 6.3.4 un párrafo breve con la fecha, el lugar del levantamiento y el rol de cada
revisor, porque es la evidencia que sustituye a los «pendientes».

**E-2. Recuperación por correo: fuera del alcance.** En el sistema, el enlace «Olvidé mi contraseña»
ya no aparece mientras no haya correo configurado, que es el caso de producción. El código y la
migración 0002 se conservan apagados. Corregir en la tesis: 5.3.3.2 («rutas de recuperación de
cuenta»: indicar que están desactivadas sin proveedor de correo), 5.5.3 («El área pública ofrece
información, acceso, registro y recuperación»: retirar «recuperación»), 6.3.1.1 («o solicitar
recuperación. El envío real… permanece pendiente»), Anexo 4 §2 (retirar el párrafo «Si olvidó su
contraseña…») y Anexo 6 §6 («Para recuperación de acceso, configure el proveedor de correo…»). Sin
recuperación por correo, quien olvide su contraseña no tiene una vía automática para recuperarla:
la tesis debe declararlo como limitación.

**E-3. Teléfono físico: fuera del alcance.** No debe afirmarse una prueba que no se hará.

- **4.8.2 d) dice «La funcionalidad se comprobó en un teléfono inteligente y en una computadora de
  escritorio».** Hoy es falso. Proponer: «…se comprobó en una computadora de escritorio y en la
  vista de teléfono del navegador, entre 320 y 430 píxeles de ancho».
- 5.5.4, 7.2 e y Anexo 3 objetivo e: cambiar «sigue pendiente de comprobación» y «teléfono físico…
  pendientes» por una limitación declarada: la compatibilidad móvil se verificó por emulación.

**E-4. Participantes: fuera del alcance.**

- **1.5.2 c) dice «…aplicadas a la muestra de usuarios participantes en el estudio».** La validación
  se hizo con perfiles sintéticos (8,000 de validación y 10,000 independientes), porque la encuesta
  no recogió medidas biométricas. La propia tesis lo dice en 7.1 c y en el Anexo 3. Es una
  incoherencia en un objetivo aprobado: decidir con la asesora si se ajusta su redacción o se
  explica la diferencia en el Capítulo VII.
- 4.9.4 R-06: la mitigación «prueba con usuarios reales del gimnasio antes de darlo por aceptado» no
  se aplicó. Indicarlo y describir la mitigación usada (pruebas automatizadas y revisión de las
  asesoras).
- 4.10.3, 5.5.2, 5.8.2 («Observación prevista con participantes; pendiente de realizarse»), Capítulo
  VI introducción y 8.3: pasar de «pendiente» a «no incluida en esta investigación», y dejar la
  evaluación con participantes como recomendación para futuras investigaciones (8.3 ya la plantea).

## F. Aplicado en la copia versionada (31-10-2026, por encargo del autor: «haz todo»)

Archivo entregable: `Tesis Final/Leonardo Zepeda - Proyecto de Graduacion II - Entrega Final.docx`
y su PDF (282 páginas), creados a partir de la versión «verificada PostgreSQL» de Descargas. Las
versiones anteriores, incluida la de 667 pruebas, no se modificaron.

- 136 correcciones de texto con las propuestas de las secciones B y E.
- **Postura sobre la hipótesis (decisión tomada por encargo del autor):** se acepta en los términos
  en que fue operacionalizada, con tres limitaciones declaradas: perfiles sintéticos, tres reglas
  empíricas representativas y primer plan tras arranque en frío por encima de 3 s (componente
  «Automatiza»: Parcial). Es una posición intermedia entre «se acepta» (667 pruebas) y «no queda
  validada» (versión de Descargas). Conviene confirmarla con la asesora.
- **Anuencia del gimnasio:** «Favorable», con la evidencia declarada por el autor (un entrenador del
  gimnasio revisó las 25 guías).
- El objetivo 1.5.2 c se conservó tal como fue aprobado; 7.1 c explica que la comparación se aplicó
  a perfiles sintéticos que cubren el dominio de la población.
- Figuras 57 y 81: nueva captura de la pantalla de acceso de la versión entregada.
- El Índice de Figuras era texto fijo: se sustituyó por un índice automático (`TOC \c "Figura"`).
  Se actualizaron con Word el índice general, el de tablas y el de figuras.
- Se restituyó el formato de 16 celdas de tabla y 9 viñetas que la versión de Descargas había
  perdido al reescribirlas.
- Se restituyeron las citas de FDA (2024), NHS (2023) y Field (2024).

Comprobado después: 120 tablas y 86 figuras numeradas en secuencia y coincidentes con sus índices,
305 encabezados coincidentes, márgenes 2.5/2.5/3/2.5 cm, Times New Roman 12, 64 referencias todas
citadas y ninguna frase de «pendiente», «provisional» o «versión local».
