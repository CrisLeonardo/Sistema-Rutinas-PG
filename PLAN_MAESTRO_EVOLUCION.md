# Plan maestro de evolución del sistema

Fecha de elaboración: 29 de octubre de 2026.

**Decisión vigente del autor, 30 de octubre de 2026:** conservar puntos, niveles
 e insignias **individuales**; amigos, grupos, invitaciones y retos colectivos
quedan **pospuestos**. Se retiraron sus accesos y se desactivó la API social,
conservando fuentes y datos. La fase 7 avanza sobre el producto individual, sin
esperar el piloto social. Se comprobaron integridad y restauración de 25 tablas,
se optimizó inferencia y se corrigió el instrumento de carga. El rendimiento
bajo 50 usuarios todavía varía entre ensayos y el primer plan desde proceso
nuevo tardó 7.46 s. Permanecen las validaciones humanas y externas pendientes.
Véase [FASE_7_VALIDACION_INDIVIDUAL.md](Sistema%20Rutinas%20PG/operaciones/FASE_7_VALIDACION_INDIVIDUAL.md).

**Antecedente de fase 6, 30 de octubre de 2026:** fase 6 implementada como piloto
local en `/avance/amigos`, con invitaciones, alias, metas semanales, eventos
idempotentes, objetivo colectivo, pausa, salida, bloqueos y moderación. Se
implementó además duración por serie para plancha, con referencia provisional de
20–30 segundos y sin convertir repeticiones históricas. Requiere migraciones
`0004_duracion_sostenes` y `0005_comunidad_privada`. Suite final del servidor:
792 aprobadas y 4 omitidas; cliente: 21 de entrenamiento y 11 de interacción;
construcción correcta. Véase
[FASE_6_COMUNIDAD_PRIVADA.md](Sistema%20Rutinas%20PG/operaciones/FASE_6_COMUNIDAD_PRIVADA.md).
La fase continúa abierta: el autor confirmó que todavía no tiene OAuth de Gmail,
teléfono físico ni revisores; las revisiones profesionales y el piloto con
participantes no se han realizado. La duración y las series de plancha siguen
pendientes de aprobación profesional. No hubo publicación ni migración de
producción. Los avances anteriores conservan su contexto histórico.

**Decisión del autor:** el nombre elegido es **Senda**. La fase 0 está en ejecución; su evidencia y pendientes se registran en `Sistema Rutinas PG/operaciones/FASE_0_LINEA_BASE.md`. El diseño del símbolo y la aplicación de marca corresponden a la fase 1. El autor confirmó que todos los servicios actuales son gratuitos.

**Avance de fase 1, 29 de octubre de 2026:** se implementó un prototipo separado
en `/prototipo/fase-1`, con tres bocetos vectoriales, dos direcciones visuales y
recorridos de portada, primer uso, inicio y sesión. La entrega, sus límites y la
evaluación pendiente con 5–8 personas están en
[FASE_1_IDENTIDAD_Y_EXPERIENCIA.md](Sistema%20Rutinas%20PG/operaciones/FASE_1_IDENTIDAD_Y_EXPERIENCIA.md).
El autor decidió conservar **A · Tierra y camino como modo claro** y
**B · Pulso y contraste como modo oscuro** de una misma identidad, tanto en la
portada como en el sistema. La paleta y la preferencia de tema ya se comparten
con las pantallas reales; la nueva distribución sigue en prototipo y la selección
del símbolo está pendiente. La fase permanece en revisión; no se han cerrado los
pendientes de fase 0 ni publicado una nueva identidad en producción.

Este plan convierte la propuesta de mejorar el sitio público, la aplicación, la marca, las explicaciones animadas y la participación social en entregas verificables. La recomendación es conservar la base funcional y construir una experiencia más útil y reconocible sobre ella. Primero se trabaja la identidad y el recorrido de entrada; después, el contenido y la experiencia de uso; finalmente, la competencia social y su validación local.

Las fases descritas abajo son la planificación inicial. El informe de fase 0 distingue el trabajo ejecutado, las comprobaciones y lo pendiente; este plan por sí solo no acredita resultados de pruebas ni mejoras de adherencia.

## 1. Base documental y alcance de la revisión

**Avance de fase 5, 30 de octubre de 2026:** respuestas de series y guardado,
cronómetro por fecha límite con vibración optativa, nuevas insignias con tarjeta
revisable, Mi senda con próxima acción y filtros, comparación de comidas y
gráficas con valores en texto. Once casos de interacción y 21 de entrenamiento
del cliente aprobados; compilación correcta. Implementación local sin migración
nueva ni cambios de reglas del servidor. Continúan pendientes teléfono físico,
participantes, publicación y los pendientes de fases anteriores. Véase
[FASE_5_INTERACCION_Y_SENDA.md](Sistema%20Rutinas%20PG/operaciones/FASE_5_INTERACCION_Y_SENDA.md).

**Avance de fase 4, 30 de octubre de 2026:** piloto local con restricciones
estructuradas, 18 recetas en borrador, siete días persistentes, cambios de comida
calculados y compras sumadas desde la semana. Requiere la migración
`0003_alimentacion_practica`. Suite completa: 759 aprobadas y 3 omitidas; la
regresión posterior de compras, plan y alimentación obtuvo 103 aprobadas y una
omitida. Recetas, datos y margen del ajuste siguen pendientes de revisión
profesional; no hay precios de campo nuevos ni despliegue. La revisión de las
diez fichas, Gmail y la duración de la plancha siguen abiertas. Véase
[FASE_4_ALIMENTACION_PRACTICA.md](Sistema%20Rutinas%20PG/operaciones/FASE_4_ALIMENTACION_PRACTICA.md).

**Avance de fase 3, 30 de octubre de 2026:** biblioteca conectada al catálogo,
consulta de técnica desde la sesión y diez fichas editoriales con fuentes y
demostraciones esquemáticas disponibles en `/prototipo/fase-3`. El autor revisará
el piloto; pidió simplificar la figura y se sustituyó por segmentos y
articulaciones con apoyos más claros. La reproducción normal sigue pendiente de
validación técnica. No hay sustitución automática de ejercicios ni verificación
nueva de equipamiento. El alcance y los pendientes se registran en el
[informe de fase 3](Sistema%20Rutinas%20PG/operaciones/FASE_3_ENTRENAMIENTO_VISUAL.md).

**Avance de fase 2, 30 de octubre de 2026:** sitio público con diez páginas,
primer uso conectado al plan, panel renovado y recuperación de acceso
implementados localmente. La suite ejecutada con PostgreSQL obtuvo 709 pruebas
aprobadas y 2 omitidas. El correo público elegido es `senda1986.gt@gmail.com`;
queda autorizar Gmail, verificar entrega real y publicar en pruebas tras aplicar
la migración 0002. La revisión humana, el teléfono físico y la medición del primer
plan siguen pendientes. Véase el
[informe de fase 2](Sistema%20Rutinas%20PG/operaciones/FASE_2_SITIO_Y_CUENTAS.md).
Este avance sustituye el estado de prototipo del panel descrito arriba; no
declara cerradas las condiciones de salida ni los pendientes anteriores.

Documento académico de referencia: `Tesis Final/Leonardo Zepeda - Proyecto de Graduacion II - Entrega 3 (667 pruebas).docx`, modificado el 23 de octubre de 2026 a las 16:56 según el sistema de archivos. Es el DOCX más reciente de la carpeta, excluidos los archivos temporales de Word. La fecha no se tomó del nombre. No se debe usar la entrega 2 ni el PDF de la entrega 3 como sustituto de esta versión al preparar cambios.

También se revisaron el plan de desarrollo existente, las auditorías y resúmenes de correcciones, las guías `PG2 C1 2026.pdf`, `PG2 C2 2026.pdf` y `PG2 Diseño del Sistema.pdf`, las rutas y pantallas del cliente, modelos y servicios del servidor, los catálogos iniciales y la configuración de la aplicación instalable. No se encontraron archivos `AGENTS.md` en el árbol revisado ni en los directorios superiores comprobados.

La revisión fue de contenido documental y código fuente. No incluyó una ejecución funcional del sistema, una auditoría visual de todas las pantallas ni una nueva ejecución de la batería de pruebas. El acceso al sitio publicado mediante la herramienta de consulta web no permitió verificar su estado actual; eso no demuestra que esté caído.

## 2. Diagnóstico que determina las prioridades

| Área | Evidencia actual | Trabajo recomendado |
|---|---|---|
| Entrada al producto | `frontend/src/App.jsx` envía `/` a `/acceso` o `/panel`. Ya hay registro y acceso. | Crear una portada pública y recorridos explicativos conectados con la autenticación existente. |
| Entrenamiento | Hay rutina, bitácora por serie, progresión y cronómetro. El catálogo inicial contiene 25 ejercicios. | Mejorar explicación, presentación, sustituciones y cobertura del equipamiento verificado. |
| Nutrición | Hay plan, menú diario, costos y compras. El catálogo inicial contiene 36 alimentos. | Incorporar recetas, variedad semanal, preferencias y restricciones alimentarias. |
| Motivación | `Senda.jsx`, `servicios/juego.py` y `motor/juego.py` implementan puntos, niveles e insignias personales. La tesis los documenta. | Mejorar su presentación y añadir retos sociales sobre esta base. |
| Salud | El perfil ya registra lesiones y condiciones médicas; el documento antiguo de pendientes no refleja todo el trabajo posterior. | Revisar las restricciones existentes y añadir el tratamiento explícito de alergias e intolerancias antes de ampliar las comidas. |
| Multimedia | Los modelos de ejercicio y alimento no contienen una biblioteca editorial de imágenes o demostraciones articuladas. | Diseñar datos, revisión y publicación del contenido multimedia. |
| Interacción | Hay temas, estados de carga, transiciones y preferencia de movimiento reducido. | Crear un lenguaje de animación consistente y más respuestas visibles a las acciones. |
| Instalación | Existe configuración PWA. Conserva el armazón y los recursos estáticos; no proporciona acceso completo al plan sin conexión. | Evaluar una etapa específica para entrenamiento sin conexión. |
| Marca | Nombre descriptivo y símbolo de edificio clásico con brillo verde. | Explorar una identidad ligada a movimiento, progreso y cercanía. |
| Operación | Los modelos usan creación de tablas y el plan histórico identifica migraciones pendientes. | Introducir migraciones y verificación en PostgreSQL antes de ampliar los modelos persistentes. |

Los números de ejercicios y alimentos corresponden a las listas iniciales del código; no representan el contenido actual de una base de datos publicada ni prueban verificación de campo.

Hay divergencias documentales: `PLAN.md` aún habla de despliegue pendiente y de cifras antiguas de pruebas, mientras la última tesis documenta una dirección publicada y 667 casos aprobados el 23 de octubre. `README.md` conserva referencias de interfaz que tampoco reflejan todas las decisiones posteriores. La cifra de 667 es evidencia histórica declarada en la tesis, no un resultado vuelto a obtener en esta revisión. La fase inicial debe reconciliar estos documentos con la versión que realmente se ejecute.

## 3. Propuesta de producto y posicionamiento

Propuesta de valor de trabajo: **entender qué hacer hoy, entrenar con una guía visual y comer con opciones que se consiguen cerca, mientras se comparte la constancia con amigos**.

Público inicial: personas adultas del municipio y usuarios del gimnasio participante, con prioridad para quien necesita orientación sencilla, tiene presupuesto limitado o está empezando. Los usuarios con experiencia también deben poder registrar su entrenamiento con rapidez.

Tres recorridos principales:

1. Visitante: comprende la propuesta, explora una demostración y crea su cuenta.
2. Usuario: abre su inicio, identifica la siguiente acción, consulta la técnica y registra su sesión o alimentación.
3. Participante social: acepta una invitación, entiende la meta semanal y ve su aporte sin publicar datos corporales.

La portada y la aplicación deben compartir marca, lenguaje y componentes. Pueden convivir en el mismo cliente React; inicialmente no hace falta crear otra base de usuarios ni otro servidor. Se revisará la representación estática de las páginas públicas si la indexación lo requiere.

## 4. Nombre e identidad visual

Los siguientes son conceptos creativos. No se ha comprobado disponibilidad de marcas, dominios ni nombres en redes; esa comprobación debe preceder a adoptar uno y comprar activos.

| Nombre | Idea que comunica | Dirección del símbolo | Consideración |
|---|---|---|---|
| **Brío** | Energía y disposición para actuar. | Trazo propio que sugiere una persona avanzando y una B; versión sólida y monocroma. | Primera recomendación por brevedad y amplitud: permite hablar de entrenamiento y alimentación. Evaluar escritura `Brio` en direcciones digitales. |
| **Senda** | Camino personal y progreso constante. | Dos trazos de un recorrido ascendente con una figura en movimiento. | Conecta con la función existente «Mi senda»; requiere distinguir el nombre del producto y el del módulo. |
| **Ímpetu** | Inicio, impulso y acción. | Símbolo compacto de avance, con una I construida mediante articulaciones. | Tiene una personalidad más deportiva; comprobar lectura y recuerdo del nombre. |
| **Nexo** | Entrenamiento acompañado y comunidad. | Dos formas enlazadas que también sugieren movimiento. | Apropiado si la comunidad pasa a ser central; palabra amplia que exige comprobar diferenciación. |

El autor eligió **Senda**. Se explorará su identidad en tres aplicaciones concretas: portada, icono instalado y pantalla de entrenamiento, comparando comprensión, recuerdo, legibilidad y asociación con el propósito. Las otras propuestas se conservan como antecedente de la decisión.

El símbolo actual sugiere una institución por su frontón y columnas; es una interpretación visual, no una medición con usuarios. Propongo una forma más reconocible a 24 y 32 píxeles, que funcione sin brillo y en un solo color. El muñeco de demostración puede pertenecer a la misma familia visual, pero el logo no necesita contener toda su anatomía.

Dirección inicial de diseño: fondos claros y oscuros bien resueltos, texto de alto contraste, un acento principal y un color reservado para logros. Evitar que toda la interfaz compita por llamar la atención. Preparar símbolo, nombre, versiones monocromas, tamaños mínimos, área de protección y los iconos PWA. El nombre comercial puede coexistir con el título académico aprobado; no se propone cambiar automáticamente este último.

## 5. Fases y condiciones de salida

Las duraciones son estimaciones preliminares de trabajo efectivo para una persona, con revisión documental incluida. No son fechas de entrega comprometidas; dependen de la validación de contenido, la disponibilidad de participantes y los resultados de la fase inicial. Las fases pueden dividirse en las iteraciones de tres semanas descritas en la tesis.

| Fase | Entrega | Dependencia | Estimación | Condición para terminar |
|---|---|---|---|---|
| 0 | Línea base del sistema y control de cambios de tesis. | Ninguna. | 2–4 días. | Estado reproducible, divergencias registradas y alcance inicial delimitado. |
| 1 | Identidad y prototipo de los recorridos principales. | Fase 0. | 4–7 días. | Nombre de trabajo, dos direcciones visuales comparadas y recorrido móvil comprensible. |
| 2 | Sitio público, cuentas y primera experiencia renovada. | Fase 1; proveedor de correo para recuperación. | 1–2 semanas. | Visitante puede comprender el producto, registrarse, entrar y recuperar acceso. |
| 3 | Biblioteca de ejercicio y piloto de muñecos articulados. | Fase 1; migraciones antes de ampliar datos. | 2–3 semanas para el piloto. | Diez ejercicios revisados con controles de reproducción e integración en la rutina. |
| 4 | Comidas, recetas y variedad semanal. | Migraciones, restricciones alimentarias y revisión de datos. | 2–3 semanas. | Semana coherente, sustituciones calculadas y compras consistentes. |
| 5 | Experiencia interactiva integrada y senda renovada. | Se inicia en fase 2 y se consolida con fases 3–4. | 1–2 semanas adicionales. | Acciones centrales tienen respuesta clara y siguen siendo rápidas y accesibles. |
| 6 (pospuesta) | Retos privados y piloto de comunidad local. | Fases 0, 2 y 5; reglas sociales definidas. | 2–3 semanas. | Invitación, participación, puntuación y salida funcionan con privacidad y límites. |
| 7 | Validación local, rendimiento y entrega académica. | Se realiza por incremento y culmina tras el piloto. | 1–2 semanas de preparación más 4 semanas de observación. | Evidencia real, incidencias atendidas y tesis alineada con la versión entregada. |

La suma orientativa es de 12–20 semanas de trabajo efectivo antes de la observación final. Se reestima al cerrar las fases 0 y 1; el catálogo completo de animaciones y la expansión pública pueden extender ese horizonte. Para una entrega académica cercana, limitar la primera versión a fases 0–3 y un solo reto privado después de validar su base. Las funciones futuras se presentan como ampliaciones, sin atribuirles resultados de la investigación ya realizada.

### Fase 0 Línea base y preparación

a) Identificar la revisión de código, las modificaciones locales existentes y el entorno que corresponde a la última evidencia de tesis. Hay cambios locales anteriores a este trabajo; deben preservarse.

b) Ejecutar y registrar las comprobaciones funcionales pertinentes, la construcción del cliente y una muestra de recorridos en teléfono y computadora. Registrar fecha, entorno y resultados; no trasladar cifras antiguas a una versión nueva sin medirla.

c) Contrastar requisitos, código, despliegue y documentos. Abrir una lista de divergencias, incluyendo registro de edad, privacidad, progresión, cálculos y datos provisionales. Las reglas de nutrición existentes requieren revisión profesional si se propone modificarlas; este plan no las valida clínicamente.

d) Preparar migraciones versionadas y una restauración ensayada en un entorno de pruebas. Es una dependencia para nuevas columnas, restricciones y relaciones; `create_all` no sustituye ese proceso.

e) Registrar presupuesto y equipo reales. No incorporar costos históricos del alojamiento como precios vigentes sin verificarlos.

### Fase 1 Marca y experiencia

Entregables: tres bocetos de símbolo para Senda; sistema de color, tipografía, ilustración y movimiento; prototipo de portada, primer uso, inicio y sesión de ejercicio.

El inicio responde «qué hago hoy» con una acción principal: iniciar sesión de entrenamiento, consultar la comida siguiente o registrar avance, según contexto. Añade resumen semanal, acceso a técnica y próximo logro. La información avanzada queda disponible sin ocupar el primer plano.

Evaluar con 5–8 personas del público inicial, mezclando principiantes y usuarios con experiencia. Ese tamaño sirve para detectar problemas de comprensión; no permite afirmar representatividad ni eficacia clínica. Registrar tareas, obstáculos y decisiones posteriores.

### Fase 2 Sitio público y cuentas

Mapa público propuesto: `/`, `/como-funciona`, `/ejercicios`, `/alimentacion`, `/comunidad`, `/preguntas-frecuentes`, `/sobre-el-proyecto`, `/privacidad`, `/terminos` y `/ayuda`, con registro y acceso existentes. Las secciones extensas pueden empezar dentro de una sola portada.

Contenido mínimo:

a) Beneficio concreto y botones «Crear cuenta» y «Ver cómo funciona», con acceso visible para quien ya tiene cuenta.

b) Demostración con datos ficticios identificados: una rutina, una explicación visual y una comida de ejemplo. No presentar una muestra como plan personalizado.

c) Proceso en pasos cortos: cuenta, perfil, plan y seguimiento. Explicar para quién es, qué se necesita y los límites del servicio.

d) Privacidad, ayuda, contacto realmente disponible y condiciones de uso. Si se comunica gratuidad, debe coincidir con la política real; la tesis actual describe acceso sin costo.

e) Recuperación de contraseña por correo con respuestas que no revelen cuentas, códigos o enlaces de uso único y vencimiento, límites de intentos y revocación de sesiones correspondiente. Reutilizar la autenticación actual. Evaluar verificación de correo y protección contra cuentas automáticas.

f) Metadatos y contenido públicos indexables; las pantallas personales permanecen protegidas y fuera de la indexación. Evitar publicar datos de demostración que pertenezcan a una persona real.

Criterio: una persona nueva comprende el servicio y obtiene su primer plan en menos de cinco minutos, como exige 4.5.3. Si hay espera por correo o infraestructura, medirla por separado y explicar cómo se cuenta el tiempo; no excluirla silenciosamente para declarar cumplimiento.

### Fase 3 Entrenamiento explicado visualmente

Crear una ficha por ejercicio: objetivo, equipo, dificultad, colocación inicial, fases, indicaciones breves, errores frecuentes, variantes y alternativas compatibles. La selección debe respetar las restricciones que aplica el motor; una sustitución no puede romper la rutina ni su volumen prescrito.

Propuesta técnica inicial: muñeco articulado vectorial en 2D mediante SVG y animación controlada desde React. Permite reutilizar articulaciones, cambiar colores y mostrar posiciones concretas. Comenzar con un piloto de diez ejercicios, elegidos según las rutinas más utilizadas y el equipamiento de campo. Los ejercicios cuya técnica no se entienda en una sola vista necesitarán vista frontal, lateral o material complementario; el 3D se evalúa después de medir el piloto.

Controles: reproducir, pausar, reiniciar, velocidad y avance por fases. Con movimiento reducido, ofrecer imágenes de inicio, transición y final con texto. La ilustración no observa al usuario ni corrige su postura real: no se presentará como evaluación corporal.

Cada movimiento tendrá versión, autoría o licencia, fecha de revisión y responsable de validación técnica. El entrenamiento depende de una revisión competente del contenido, no solo de que la animación se vea fluida. Usar una imagen estática cuando un recurso todavía no esté revisado.

Meta inicial: diez fichas animadas revisadas e integradas; ampliación posterior a 40–60 ejercicios solo cuando exista cobertura de equipo y capacidad editorial. Las cifras son objetivos de alcance, no contenido ya disponible. Cargar los recursos cuando se necesitan y conservar el acceso al texto aunque fallen.

### Fase 4 Alimentación práctica

Separar alimento, receta y porción. Registrar estado crudo o cocido, unidades, ingredientes y rendimiento; una imagen no acredita composición nutricional. Incorporar costo por porción, fecha y fuente del precio, preparación, tiempo y medidas caseras.

Primero: preferencias, alergias e intolerancias con datos estructurados y pruebas de exclusión, incluidos ingredientes de recetas y sustituciones. Mantener el bloqueo y la derivación de las condiciones que ya quedan fuera del alcance del sistema. No equiparar preferencia con alergia.

Después: semana de siete días, variedad por tiempo de comida, alternativas disponibles y recálculo del aporte y de compras. «Cambiar comida» debe recalcular porciones y verificar las tolerancias nutricionales acordadas; no reemplazar solo un nombre o una fotografía.

Priorizar recetas que usen alimentos verificados en El Progreso y costos que puedan mantenerse actualizados. Meta del piloto: 15–20 recetas revisadas, no centenares de variantes superficiales. Las fotografías propias o con licencia deben representar lo que la receta realmente contiene; una ilustración conceptual se identifica como tal.

### Fase 5 Animación e interacción

La animación se trabaja desde la fase 2, en cada componente nuevo. Esta fase unifica el resultado en los recorridos completos.

| Acción | Respuesta propuesta | Propósito |
|---|---|---|
| Completar una serie | Confirmación breve y avance de sesión. | Saber que el registro se guardó. |
| Iniciar descanso | Cronómetro visible; sonido o vibración solo si el usuario lo habilita y el equipo lo admite. | Facilitar el ritmo de la sesión. |
| Guardar una sesión | Resumen, puntos obtenidos y siguiente paso. | Hacer visible lo realizado. |
| Alcanzar una insignia | Revelado breve, descripción y opción de compartir una tarjeta revisable. | Dar significado al logro. |
| Cambiar una comida | Transición que conserva contexto y muestra porciones y costo recalculados. | Comprender el cambio. |
| Consultar evolución | Entrada gradual de la gráfica y valores accesibles en texto. | Facilitar la lectura. |
| Enviar un formulario | Estados de envío, error y éxito sin perder datos. | Dar confianza y permitir recuperación. |

Probar como punto de partida transiciones de 120–250 ms y celebraciones breves; ajustar según dispositivos reales. No retrasar el guardado para terminar una animación. Evitar acumular efectos en una misma pantalla. Respetar `prefers-reduced-motion`, ofrecer controles para las demostraciones continuas y no depender solo del color o el sonido. Objetivo de accesibilidad: WCAG 2.2 AA, con control de movimiento adicional inspirado en 2.3.3, que pertenece al nivel AAA.

### Fase 6 Amigos y comunidad

**Pospuesta por decisión del autor el 30-10-2026.** Lo siguiente se conserva como propuesta futura; no pertenece a la entrega individual actual.

Primera entrega: grupos privados por invitación, alias, reto semanal de constancia y objetivo colectivo. Segunda entrega: grupos de gimnasio con moderación y adhesión voluntaria. Una liga local pública solo se evalúa tras el piloto. No se necesita ubicación precisa ni contactos del teléfono.

Separar la experiencia histórica de Mi senda de los puntos de una temporada. Los premios existentes por sesiones, marcas o progreso no se trasladan automáticamente a una clasificación pública: podrían dar ventajas distintas y revelar información privada.

Prototipo de regla para debatir y probar: al inscribirse, cada participante conserva una meta semanal compatible con su plan, de 2 a 5 sesiones. Cada fecha válida aporta como máximo una sesión; el cumplimiento es `min(sesiones válidas / meta acordada, 1)`. El reto entrega hasta 100 puntos semanales según ese cumplimiento. No hay beneficio competitivo por superar el plan. La meta se fija al inicio de la semana y los cambios por lesión o interrupción tienen un procedimiento visible, sin publicar su motivo.

Ejemplo: una persona con meta de dos sesiones y otra con meta de cuatro alcanzan 100 puntos al completar sus respectivas metas. Se puede empatar y compartir la recompensa. Esta normalización es una propuesta de participación inclusiva, no una prueba de equivalencia del esfuerzo ni de actividad verificada.

Protecciones mínimas:

a) Puntuación calculada en el servidor, eventos idempotentes, límites y control de duplicados. Nunca aceptar un total de puntos enviado por el cliente.

b) Las sesiones autodeclaradas no permiten demostrar entrenamiento real. El piloto se describe como registro de constancia y no ofrece premios monetarios; anomalías deben poder revisarse.

c) Perfil social separado, privado al inicio. Mostrar solo alias y progreso del reto aceptado. No publicar peso, lesiones, patologías, calorías, cargas ni historial de medidas, aunque exista consentimiento general: RN-06 exige que los datos biométricos sean exclusivos del titular.

d) Invitar, aceptar, rechazar, salir, bloquear, denunciar y moderar, con reglas de convivencia visibles. Empezar sin mensajería abierta para reducir la carga de moderación.

e) No conceder premios por perder peso, restringir comida, aumentar cargas por encima del plan o entrenar durante el descanso indicado. Mantener los logros históricos al interrumpir una racha y facilitar el regreso.

Datos nuevos candidatos: perfil social, grupo, membresía, invitación, reto, participación y evento de puntuación. Definir permisos y caducidad antes de crear tablas. Los registros sociales se relacionan con la cuenta sin habilitar consultas al perfil biométrico de otra persona.

### Fase 7 Piloto y consolidación

**En ejecución con alcance individual.** Usar el guion `PILOTO_INDIVIDUAL_FASE7.md`; no incluir grupos o invitaciones como condición de esta validación.

Reclutar voluntarios adultos del público inicial con información clara de qué se registra. Evaluar tareas de cuenta, primer plan, interpretación del ejercicio, sustitución de comida y participación en un reto. Registrar dificultades, tiempo y satisfacción; atender fallos antes de ampliar la participación.

Contrastar retención, sesiones registradas y comprensión con una línea base. Una comparación antes/después o una muestra pequeña no prueba que la función cause cambios físicos ni permite afirmar superioridad clínica. Las conclusiones académicas deben ajustarse al diseño y a la evidencia realmente obtenidos.

## 6. Psicología y marketing como hipótesis comprobables

La experiencia debe apoyar autonomía, percepción de capacidad y vínculo social: permitir elegir metas y avisos, mostrar progreso comprensible y ofrecer compañía voluntaria. Son criterios de diseño inspirados en la teoría de la autodeterminación; su efectividad en este producto debe comprobarse con usuarios.

La evidencia de los ensayos STEP UP y BE ACTIVE respalda estudiar incentivos de juego para actividad física, pero sus participantes y actividades difieren del gimnasio local. No permite prometer que una medalla hará que todas las personas regresen. STEP UP es de 2019: sirve como antecedente de diseño en este plan, pero no se incorporará automáticamente a una tesis cuya rúbrica pide fuentes recientes. BE ACTIVE, de 2024, es una referencia más reciente para revisar, con la misma cautela de transferencia.

| Necesidad | Decisión propuesta | Indicador |
|---|---|---|
| Entender el valor antes de entregar datos | Demostración pública y explicación breve de beneficios. | Visitas que llegan a demostración y a registro. |
| Sentirse capaz al empezar | Pasos cortos y una primera sesión guiada. | Primer plan obtenido y primera sesión registrada. |
| Percibir progreso temprano | Resumen de sesión y avance semanal visible. | Comprensión del resumen y regreso con acción útil. |
| Tener compañía | Invitaciones y metas cooperativas. | Invitaciones aceptadas y participación voluntaria. |
| Recuperarse tras una pausa | Mensajes de regreso y ajuste de metas. | Usuarios que retoman sin abandonar el proceso. |

Embudo de adquisición propuesto: demostración local → visita a la portada → cuenta → perfil → primer plan → primera sesión → regreso la semana siguiente → invitación aceptada. Un código QR en el gimnasio y demostraciones breves son canales para probar con autorización del lugar; este plan no envía mensajes ni publica campañas.

Promesa de comunicación inicial: «Tu entrenamiento explicado paso a paso y comidas con opciones de tu localidad». Comprobar comprensión antes de convertirla en lema definitivo. Usar testimonios únicamente con permiso y resultados auténticos. No prometer transformación corporal en plazos arbitrarios, no inventar usuarios ni presentar alimentos o equipo provisional como verificados.

La atención se mide por acciones útiles y comprensión; el tiempo de pantalla por sí solo no es éxito. Los avisos son opcionales, ajustables y con horario de descanso. Las tarjetas para compartir permiten revisar qué información saldrá antes de publicarla.

## 7. Trazabilidad con la tesis

La marca comercial no reemplaza por defecto el título de investigación, la hipótesis, la población ni los objetivos aprobados. La ampliación social y el acceso sin conexión son cambios de alcance que deben quedar explicitados. RN-01 a RN-06 y las restricciones RE existentes se conservan hasta que una revisión fundamentada y documentada establezca otra cosa.

Si las decisiones de motivación, aprendizaje visual o participación social pasan a formar parte de la justificación académica, incorporar su fundamento verificable al Capítulo II. Distinguir ese sustento conceptual de una evaluación empírica del producto; añadir funciones no demuestra por sí mismo una nueva hipótesis.

La tesis más reciente utiliza la Tabla 35 para reglas del negocio y la Tabla 90 para el resumen de pruebas. Las referencias de `PLAN.md` a tablas de versiones anteriores deben reconciliarse; no copiar su numeración automáticamente.

| Cambio propuesto | Análisis y alcance | Diseño | Verificación y evidencia |
|---|---|---|---|
| Nombre y sitio público | IV: visión y nuevas historias; I solo si cambia el alcance aprobado. | V 5.5: prototipos y navegación; 5.2 si cambia integración o publicación. | VI: recorridos, capturas y acceso; manuales e iconos. |
| Recuperación de acceso | IV: criterios y seguridad. | V 5.3 y 5.6: correo, token, estados y permisos. | VI: vencimiento, reutilización, límites, revocación y no enumeración de cuentas. |
| Fichas y muñecos articulados | IV: catálogo, usabilidad y criterios nuevos. | V 5.3–5.5: recursos, datos, reproductor y navegación. | VI: correspondencia, revisión técnica, controles y rendimiento; manual de usuario. |
| Recetas y menú semanal | IV: requisitos de alimentación y reglas de sustitución. | V 5.3–5.4: entidades, unidades y cálculo. | VI: restricciones, porciones, aportes y compras; datos de campo en anexos. |
| Nuevas animaciones | IV 4.5: requisitos no funcionales. | V 5.5: movimiento, accesibilidad y prototipos. | VI: comprensión, teclado, movimiento reducido y tiempos. |
| Retos entre amigos | IV: historias, privacidad, riesgos y alcance; revisar I si se incorpora al objeto del estudio. | V 5.3, 5.4, 5.6 y 5.7: modelo social, autorizaciones y diagramas. | VI: aislamiento entre grupos, fraude básico, abandono, puntuación y moderación. |
| Uso sin conexión, posterior | I 1.6.2 limita el uso a conexión estable: requiere precisar qué operación se amplía. | V: caché, datos locales, sincronización, cierre de sesión y conflictos. | VI: modo avión, duplicados, vencimiento y borrado de datos locales. |
| Tecnología, correo o almacenamiento nuevos | III: herramientas usadas; IV 4.10: factibilidad y costos. | V: arquitectura, despliegue y seguridad. | VI: comprobación del despliegue y manual de instalación. |

Para cada incremento crear una ficha con: identificador, necesidad, requisito afectado, criterios de aceptación, datos y permisos, archivos modificados, apartados de tesis afectados, pruebas ejecutadas con fecha y entorno, capturas, limitaciones y versión entregada.

Antes de cerrar la documentación:

a) Trabajar a partir del DOCX de 667 pruebas en una copia versionada y conservar el archivo de referencia.

b) Describir como construido solo lo implementado; presentar lo demás como propuesta o trabajo futuro. Actualizar conclusiones solo si cambian resultados respaldados por evidencia.

c) Renovar capturas que ya no correspondan, diagramas, diccionario de datos, inventario de interfaces, navegación y manuales. Conservar coherencia entre cliente, servidor y tablas.

d) Actualizar los casos y totales de pruebas a partir de una ejecución real. Conservar la evidencia histórica y su versión; no tratar 667 como una meta fija ni sumar casos sin ejecutarlos.

e) Aplicar las reglas de las guías y correcciones: Times New Roman 12, interlineado 1.5, márgenes superior/inferior/derecho de 2.5 cm e izquierdo de 3 cm, enumeraciones alfabéticas, redacción en español, encabezados acompañados por contenido y sin quedar solos al final de página. Mantener los mínimos de extensión por capítulo aplicables.

f) Numerar y titular tablas y figuras, indicar su fuente y explicar los diagramas. Verificar las referencias con datos bibliográficos reales, formato APA y la antigüedad exigida por la rúbrica; no cambiar el año para aparentar vigencia.

g) Actualizar índices general, de tablas y de figuras; revisar referencias cruzadas. Renderizar y verificar la copia final antes de entregar. Estas reglas también deben aplicarse a contenido nuevo que se traslade desde este plan, cuyo formato Markdown no es el formato final de tesis.

## 8. Lista inicial de trabajo priorizada

Los identificadores `MEJ` son propios de esta propuesta y no renumeran las HU ni las RE existentes. Dividir cada elemento en historias pequeñas durante el refinamiento.

| ID | Trabajo | Prioridad | Criterio esencial |
|---|---|---|---|
| MEJ-01 | Reconciliar versión de tesis, código y operación. | P0 | Lista de divergencias y línea base verificable. |
| MEJ-02 | Preparar migraciones y recuperación. | P0 antes de cambios de datos | Ensayo en PostgreSQL con conservación de información. |
| MEJ-03 | Identidad y prototipo principal. | P1 | Dos propuestas comparadas en tareas reales. |
| MEJ-04 | Portada pública y demostración. | P1 | Contenido comprensible, accesible y conectado a cuentas. |
| MEJ-05 | Recuperar acceso. | P1 | Flujo completo y controles de seguridad comprobados. |
| MEJ-06 | Inicio y primer uso renovados. | P1 | Acción siguiente clara y primer plan dentro del objetivo de tiempo. |
| MEJ-07 | Diez fichas de ejercicio con animación. | P1 | Contenido revisado y representación utilizable sin movimiento. |
| MEJ-08 | Restricciones alimentarias. | P1 antes de ampliar recetas | Exclusiones efectivas en ingredientes y sustituciones. |
| MEJ-09 | Recetas y semana variada. | P2 | Aportes y lista de compras coherentes. |
| MEJ-10 | Interacciones y senda renovada. | P2 | Respuesta visible sin obstaculizar el registro. |
| MEJ-11 | Grupos y retos privados. | P2 | Permisos, invitaciones y puntuación limitados por servidor. |
| MEJ-12 | Piloto y cierre de evidencia. | P1 transversal | Hallazgos, medidas y documentación corresponden a la entrega. |
| MEJ-13 | Entrenamiento sin conexión. | P3 | Sincronización sin duplicados y limpieza por cuenta. |
| MEJ-14 | Duración explícita de ejercicios sostenidos, empezando por plancha. | P1 | Motor, unidades, registro e historial coherentes; duración revisada y migración sin convertir repeticiones históricas en segundos. |

P0 significa dependencia o problema que bloquea trabajo posterior; P1, valor principal de la primera entrega; P2, ampliación siguiente; P3, evolución posterior.

## 9. Medición de calidad y definición de terminado

Conservar las metas de la tesis: generación del plan inferior a tres segundos; consultas inferiores a dos segundos sobre tercera generación; al menos cincuenta usuarios concurrentes; primer plan en menos de cinco minutos; interfaz desde 320 hasta 1920 píxeles. Precisar condiciones y método antes de cada medición. Si la infraestructura real no cumple, registrar el resultado y resolverlo o documentar la limitación; no mover la meta sin justificar el cambio.

Medir además: registros que alcanzan el primer plan, primera sesión completada, regreso en siete y veintiocho días con una acción útil, finalización de tareas sin ayuda, abandono de formularios y comprensión de técnica. Definir denominadores y excluir cuentas de prueba. La telemetría no debe copiar medidas, condiciones médicas ni contenido de formularios a servicios de marketing.

Las animaciones y fotografías deben respetar un presupuesto de descarga que se fije con una medición inicial en teléfonos del público objetivo. Cargar imágenes y demostraciones bajo demanda, detener trabajo fuera de pantalla y probar con ahorro de datos. Revisar también las métricas web de carga, respuesta y estabilidad visual; no sustituyen las exigencias temporales específicas de la tesis.

Un incremento termina cuando cumple los criterios de su historia, las pruebas relevantes, revisión de seguridad y rendimiento, uso en teléfono y computadora, documentación y despliegue en pruebas, siguiendo 4.8.2 y el plan existente. Añadir revisión de contenido técnico para ejercicios y comidas y pruebas en PostgreSQL cuando cambien persistencia o consultas. No afirmar compatibilidad con un teléfono físico usando únicamente una emulación.

## 10. Primer incremento recomendado

Empezar con fases 0 y 1 y preparar inmediatamente la fase 2: línea base, dos direcciones de marca, prototipo de portada y nuevo inicio, mapa de navegación y ficha piloto de un ejercicio. Después construir el sitio público conectado con las cuentas existentes y extender el piloto hasta diez ejercicios revisados.

Esto produce una primera mejora visible y evaluable sin condicionar todo el avance a terminar recetas, animar el catálogo completo o abrir una comunidad pública. Las decisiones pendientes de nombre y estilo pueden resolverse durante la revisión de prototipos; no hace falta contratar servicios ni comprar dominios para empezar.

## 11. Fuentes para las decisiones de diseño

Fuentes locales: última entrega DOCX indicada en la sección 1; `Sistema Rutinas PG/PLAN.md`; código fuente de rutas, autenticación, catálogo, entrenamiento, perfil, juego y configuración PWA; guías docentes y resúmenes de correcciones conservados en `Tesis Final`. Las referencias a apartados se comprobaron en el contenido de la última entrega, sin asumir su paginación renderizada.

Fuentes externas consultadas el 29 de octubre de 2026:

a) [BE ACTIVE, ensayo aleatorizado, Circulation, 2024](https://pubmed.ncbi.nlm.nih.gov/38583084/). Apoya explorar incentivos de juego para actividad física en la población estudiada; no demuestra eficacia de este sistema.

b) [STEP UP, ensayo aleatorizado, 2019](https://pubmed.ncbi.nlm.nih.gov/31498375/). Antecedente para comparar apoyo, colaboración y competencia; fuera de la ventana reciente de la rúbrica académica.

c) [Deci y Ryan, teoría de la autodeterminación](https://selfdeterminationtheory.org/SDT/documents/2000_DeciRyan_PIWhatWhy.pdf). Antecedente conceptual de autonomía, competencia y vínculo; se requiere literatura reciente y compatible con la rúbrica antes de incorporarlo al marco teórico.

d) [W3C, controles de pausa para contenido en movimiento](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide) y [movimiento iniciado por interacción](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html). Fundamentan controles y preferencias de movimiento, distinguiendo los niveles de conformidad.

e) [Google, experiencia de carga, interacción y estabilidad](https://developers.google.com/search/docs/appearance/core-web-vitals). Referencia complementaria de medición web.
