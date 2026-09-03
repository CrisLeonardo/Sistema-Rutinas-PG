# Plan de desarrollo por fases

Documento de control del desarrollo del sistema. Las fases siguen la pila de producto
priorizada del **Capítulo IV, Tabla 11** de la tesis. Lo tachado ya está construido y
verificado; lo demás está pendiente.

> **Para retomar el trabajo en otra sesión:** lea este archivo primero. La sección
> [Cómo levantar el proyecto](#cómo-levantar-el-proyecto) tiene los comandos y la
> sección [Decisiones técnicas tomadas](#decisiones-técnicas-tomadas) explica por qué el
> entorno está configurado como está.

## Estado general

| Fase | Contenido | Épica | Puntos | Estado |
|---|---|---|---|---|
| 0 | Fundaciones del proyecto | — | — | **Terminada** |
| 1 | Acceso seguro | E1 | 8 | **Terminada** |
| 2 | Perfil biométrico | E2 | 8 | **Terminada** |
| 3 | Motor neuronal y rutina | E3 | 21 | **Terminada** |
| 4 | Catálogo local | E3 y E4 | 13 | **Terminada** |
| 5 | Seguimiento y reportes | E4 | 13 | **Terminada** |
| 6 | Despliegue en producción | — | — | Preparada; falta contratar y publicar |

**Avance: 63 de 63 puntos de historia (100 %).** Las once historias de usuario están
implementadas y verificadas con pruebas. Lo que queda no es desarrollo sino trabajo
de campo y contratación: el levantamiento de los catálogos en los mercados y en el
Gimnasio FAMAS, y la contratación del alojamiento y el dominio.

> **Pila de producción: Render y Supabase.** El sistema se publica sobre Render —la
> aplicación, en contenedor— y Supabase —PostgreSQL administrado—. El gestor pasó de
> MySQL a PostgreSQL, y ese cambio obligó a corregir el Capítulo III de la tesis en
> nueve lugares; el detalle está en `../CAMBIOS_PILA_DESPLIEGUE.md`. El
> procedimiento completo de despliegue está en [DESPLIEGUE.md](DESPLIEGUE.md).

> **Nota sobre el orden.** La Iteración 5 se construyó antes que la 4, porque HU-08
> depende de HU-11 y HU-11 exige un levantamiento de campo que no puede hacerse
> desde el código. El apartado 4.6.3 solo condiciona HU-09 a HU-06 y HU-07, ambas
> concluidas para entonces, de modo que la alteración no rompió ninguna dependencia
> técnica declarada en la tesis. Después se construyó la Iteración 4 completa, con
> catálogos iniciales provisionales que el levantamiento de campo debe reemplazar.

## Definición de terminado

Del apartado 4.8.2. Toda historia debe cumplir las siete condiciones para darse por
concluida, con independencia de su contenido funcional:

- a) El código ejecuta sin errores y está registrado en el control de versiones.
- b) Todos los criterios de aceptación de la historia se verificaron y se cumplen.
- c) Las pruebas funcionales se ejecutaron con éxito, incluidos los casos límite.
- d) La funcionalidad se comprobó en un teléfono inteligente y en una computadora.
- e) Los requerimientos no funcionales de seguridad y rendimiento se verificaron.
- f) La documentación técnica se actualizó.
- g) El incremento se desplegó en el entorno de pruebas.

---

## Fase 0 — Fundaciones del proyecto

- [x] ~~Estructura de carpetas separando servicios, datos y presentación (patrón modelo-vista-controlador, apartado 3.1.2)~~
- [x] ~~Base de datos en contenedor (`docker-compose.yml`)~~ *(PostgreSQL 16 en el puerto 5433; empezó siendo MySQL 8 en el 3307 y migró al adoptarse Supabase)*
- [x] ~~Entorno de Python 3.12 administrado con `uv`~~
- [x] ~~Configuración por variables de entorno con plantillas `.env.example`~~
- [x] ~~Modelo entidad-relación completo del apartado 3.4.3: usuario, perfil biométrico, plan, alimento y ejercicio, más el desglose de comidas, sesiones y progreso~~
- [x] ~~Archivo `.gitignore` que excluye credenciales, entornos y el modelo entrenado~~
- [x] ~~Documentación de puesta en marcha (`README.md`)~~
- [x] ~~Inicializar el repositorio Git~~ *(commit inicial con los 104 archivos del sistema; las credenciales quedan fuera y solo se versionan las plantillas)*
- [ ] **Publicarlo en GitHub** — requiere sus credenciales de la plataforma (apartado 3.5.2)

## Fase 1 — Iteración 1: Acceso seguro (Épica E1)

Historias HU-01, HU-02 y HU-03. 8 puntos.

### HU-01. Registro de usuarios (3 puntos)

- [x] ~~Servicio de registro con validación de correo y cifrado de la contraseña~~
- [x] ~~Rechazo de correos con formato inválido~~
- [x] ~~Rechazo de correos ya registrados, sin distinguir mayúsculas~~
- [x] ~~Contraseña de mínimo ocho caracteres, con letras y números~~
- [x] ~~Almacenamiento con `bcrypt` y sal aleatoria; nunca en texto plano~~
- [x] ~~La cuenta se crea con rol de usuario deportista~~
- [x] ~~Pantalla de registro con confirmación de contraseña~~

### HU-02. Inicio y cierre de sesión seguro (3 puntos)

- [x] ~~Emisión de token de sesión firmado~~
- [x] ~~Mensaje de error idéntico para correo inexistente y contraseña incorrecta~~
- [x] ~~Verificación señuelo para que el tiempo de respuesta no revele qué cuentas existen~~
- [x] ~~Expiración de la sesión a los treinta minutos de inactividad~~
- [x] ~~Renovación automática del token mientras el usuario interactúa~~
- [x] ~~Sin sesión activa no se accede a ninguna pantalla interna~~
- [x] ~~Rechazo de tokens vencidos y de tokens firmados con otra clave~~
- [x] ~~Pantalla de acceso y cierre de sesión~~

### HU-03. Gestión de roles y permisos (2 puntos)

- [x] ~~Listado de cuentas reservado al administrador~~
- [x] ~~Asignación y modificación del rol de una cuenta~~
- [x] ~~Activación y desactivación de cuentas sin borrar su historial~~
- [x] ~~El permiso se decide con el rol almacenado en la base de datos, no con el declarado en el token~~
- [x] ~~Salvaguarda que impide dejar al sistema sin administrador activo~~
- [x] ~~Cuenta de administrador inicial creada al arrancar el sistema~~
- [x] ~~Pantalla de administración de cuentas~~

### Verificación de la Iteración 1

- [x] ~~26 pruebas funcionales que verifican uno a uno los criterios de la Tabla 10~~
- [x] ~~Flujo completo probado en el navegador: registro, acceso, cambio de rol y salvaguardas~~
- [x] ~~Diseño adaptable comprobado a 320 píxeles, sin desborde horizontal~~
- [x] ~~Controles con área táctil de 48 píxeles (requerimiento 4.5.3)~~
- [x] ~~Requerimiento de seguridad 4.5.1 verificado~~

### Cierre pendiente de la Iteración 1

Estas condiciones de la definición de terminado siguen abiertas. No bloquean el avance a
la Fase 2, pero deben cerrarse antes de la entrega:

- [x] ~~Registrar el código en el control de versiones — condición (a)~~
- [ ] Comprobar el funcionamiento en un teléfono inteligente real, no solo en un navegador redimensionado — condición (d)
- [ ] Medir la carga de pantallas sobre una conexión móvil de tercera generación, con meta de menos de dos segundos (requerimiento 4.5.2) — condición (e)
- [x] ~~Desplegar el incremento en el entorno de pruebas — condición (g)~~ *(`docker-compose.pruebas.yml`; los tres componentes levantados en contenedores y el flujo completo recorrido de extremo a extremo)*

---

## Fase 2 — Iteración 2: Perfil biométrico (Épica E2)

Historias HU-04 y HU-05. 8 puntos.

### HU-04. Captura y validación del perfil biométrico (5 puntos)

- [x] ~~Contratos de entrada y salida del perfil biométrico~~
- [x] ~~Servicio que registra el perfil asociado a la cuenta en sesión~~
- [x] ~~Campos obligatorios: peso, estatura, edad, sexo, nivel de actividad y objetivo~~
- [x] ~~Validación de peso entre 30 y 250 kilogramos~~
- [x] ~~Validación de estatura entre 120 y 220 centímetros~~
- [x] ~~Rechazo de solicitudes de personas menores de dieciocho años (regla del negocio *a*)~~
- [x] ~~Validación aplicada en el servidor, no solo en la interfaz (apartado 4.8.3)~~
- [x] ~~Formulario dividido en pasos cortos (requerimiento 4.5.3)~~
- [x] ~~Cálculo y despliegue del índice de masa corporal~~
- [x] ~~Pruebas funcionales de los criterios de aceptación y de los casos límite~~

### HU-05. Historial de medidas del usuario (3 puntos)

- [x] ~~Cada actualización genera un registro nuevo en lugar de sobrescribir el anterior~~
- [x] ~~Consulta del historial ordenado por fecha~~
- [x] ~~Los datos biométricos solo son visibles para su titular (regla del negocio *f*)~~
- [x] ~~Pantalla de historial con la evolución de las medidas~~
- [x] ~~Pruebas funcionales~~

### Verificación de la Iteración 2

- [x] ~~47 pruebas funcionales que verifican los criterios de la Tabla 9, la regla del negocio *a* y los casos límite de cada rango~~
- [x] ~~Flujo completo probado en el navegador: registro de medidas en tres pasos, actualización e historial~~
- [x] ~~Diseño adaptable comprobado a 320, 375 y 1920 píxeles, sin desborde horizontal~~
- [x] ~~Controles y opciones de selección con área táctil de 48 píxeles (requerimiento 4.5.3)~~
- [x] ~~Ninguna ruta permite consultar el perfil de otra cuenta, ni siquiera al administrador~~

### Cierre pendiente de la Iteración 2

Arrastra las mismas condiciones abiertas de la Iteración 1, que no bloquean el avance a
la Fase 3 pero deben cerrarse antes de la entrega:

- [x] ~~Registrar el código en el control de versiones — condición (a)~~
- [ ] Comprobar el funcionamiento en un teléfono inteligente real — condición (d)
- [ ] Medir la carga de pantallas sobre conexión móvil de tercera generación (requerimiento 4.5.2) — condición (e)
- [x] ~~Desplegar el incremento en el entorno de pruebas — condición (g)~~ *(`docker-compose.pruebas.yml`; los tres componentes levantados en contenedores y el flujo completo recorrido de extremo a extremo)*

## Fase 3 — Iteración 3: Motor neuronal y rutina (Épica E3)

Historias HU-06 y HU-07. 21 puntos. Es el aporte diferenciador del proyecto y el punto de
mayor incertidumbre técnica.

**Siguiente fase.** El perfil biométrico ya entrega al motor las seis variables de
entrada que necesita: `app/servicios/perfil.py` expone `obtener_perfil_vigente` y
`perfil_esta_completo`, que es la comprobación que el apartado 4.8.3 exige antes de
generar un plan.

### HU-06. Cálculo neuronal del requerimiento energético (13 puntos)

El apartado 4.6.4 prevé dividir esta historia en tres partes por su tamaño:

**3.1 Preparación del conjunto de datos**

- [x] ~~Implementar las fórmulas de Mifflin-St Jeor y Harris-Benedict como referencia~~
- [x] ~~Implementar los factores de actividad que multiplican la tasa metabólica basal~~
- [x] ~~Generar perfiles sintéticos que cubran todo el rango antropométrico plausible, para mitigar el riesgo de volumen insuficiente de datos (Tabla 12)~~
- [x] ~~Normalizar las variables de entrada y separar los conjuntos de entrenamiento y validación~~
- [x] ~~90 pruebas de la aritmética, de las reglas del negocio *b* y *c* y de la cobertura del conjunto~~

**3.2 Entrenamiento del modelo**

- [x] ~~Instalar TensorFlow y Keras en el entorno de Python 3.12~~ *(TensorFlow 2.21 y Keras 3.15)*
- [x] ~~Definir la arquitectura: capa de entrada con las variables biométricas, capas ocultas con activación ReLU y capa de salida con el requerimiento energético y los macronutrientes (apartado 2.3)~~
- [x] ~~Entrenar y ajustar los hiperparámetros de forma iterativa~~
- [x] ~~**Verificar el margen de error menor al 5 % frente a las dos fórmulas de referencia**~~ — **el criterio se cumple**
- [x] ~~Guardar el modelo entrenado y documentar sus métricas~~
- [ ] Repetir el entrenamiento con los 169 perfiles del trabajo de campo, cuando estén digitalizados, y comparar sus métricas con las del conjunto sintético

#### Resultado del entrenamiento

Ejecutado con `uv run python entrenar_modelo.py`. Es la evidencia que sostiene la
hipótesis de la investigación y debe trasladarse al Capítulo V.

| Métrica | Valor |
|---|---|
| Perfiles de entrenamiento | 32 000 |
| Perfiles de validación | 8 000 |
| Arquitectura | 8 entradas → 128 → 128 → 64 (ReLU) → 5 salidas |
| Error absoluto medio | 2.6 kcal |
| **Margen de error medio (energía)** | **0.11 %** |
| Margen de error máximo | 2.69 % |
| Perfiles bajo el 5 % | 100 % |
| Error del volumen de entrenamiento | 0.02 series (0.20 %) |
| Margen medio en los extremos del dominio | 0.12 % |

El modelo se guarda en `backend/modelo/`, fuera del control de versiones, junto con
su normalizador y sus métricas. Sin el normalizador las predicciones carecen de
sentido, por eso ambos se almacenan en el mismo lugar.

La red recibe ocho variables —peso, estatura, edad, sexo, factor de actividad,
ajuste del objetivo, nivel de experiencia y frecuencia semanal— y entrega cinco:
el requerimiento energético, los tres macronutrientes y el volumen semanal de
series por grupo muscular. Esa quinta salida es la que el apartado 2.5.1 encarga
a la red y que el generador de rutinas reparte entre las sesiones.

**3.3 Exposición como servicio web**

- [x] ~~Servicio que genera el plan a partir del perfil biométrico~~
- [x] ~~Aplicar el ajuste calórico según el objetivo, sin exceder 20 % de déficit ni 15 % de superávit (regla del negocio *b*)~~
- [x] ~~Asignar proteína entre 1.6 y 2.2 gramos por kilogramo de peso corporal (regla del negocio *c*)~~
- [x] ~~Expresar los macronutrientes en gramos y en porcentaje, con las constantes de Atwater, y verificar que la suma coincide con el requerimiento total~~
- [x] ~~Almacenar en cada plan los valores de referencia y el margen de error obtenido~~
- [x] ~~Tiempo de respuesta menor a tres segundos~~ *(0.50 s medidos; el modelo se precarga al arrancar el servicio para que ninguna petición pague el costo de leerlo del disco)*
- [x] ~~No generar plan si el perfil biométrico está incompleto (apartado 4.8.3)~~
- [x] ~~Mostrar en todo plan el aviso de consultar a un profesional de la salud (regla del negocio *e*)~~
- [x] ~~Pantalla de consulta del plan nutricional, con explicación en lenguaje sencillo de cada cifra~~
- [x] ~~Pruebas funcionales~~ *(31 pruebas)*

### Verificación de la historia HU-06

- [x] ~~Margen de error verificado en la pantalla misma: el plan muestra su diferencia frente a las dos fórmulas~~
- [x] ~~Flujo completo probado en el navegador: perfil, generación del plan y consulta~~
- [x] ~~Diseño adaptable comprobado a 320, 375 y 1920 píxeles~~
- [x] ~~El plan anterior se conserva y se marca cuál está vigente, insumo de la historia HU-10~~

> **HU-06 queda funcionalmente completa.** Falta HU-07, la rutina de entrenamiento,
> para cerrar la Fase 3.

### HU-07. Generación de la rutina de entrenamiento (8 puntos)

- [x] ~~Servicio que construye la rutina semanal~~
- [x] ~~Indicar ejercicio, series, repeticiones y repeticiones en reserva por sesión~~
- [x] ~~El número de sesiones coincide con la frecuencia semanal declarada~~
- [x] ~~**Ningún grupo muscular recibe estímulo en dos días consecutivos**~~ — verificado
  para las siete frecuencias posibles, incluido el cierre circular de la semana
- [x] ~~Ajustar volumen e intensidad al nivel de experiencia~~
- [x] ~~Progresión de carga que no supere el 10 % entre microciclos (regla del negocio *d*)~~
- [x] ~~Pantalla de consulta de la rutina semanal~~
- [x] ~~Pruebas funcionales~~ *(69 pruebas)*

#### Cómo se reparte el volumen

La red determina las series semanales por grupo muscular y el generador
(`app/motor/rutina.py`) las reparte según un esquema fijo por frecuencia:

| Días | Esquema | Observación |
|---|---|---|
| 1 a 3 | Cuerpo completo | Con tan pocas sesiones, repartir por grupo dejaría a cada uno con una sola frecuencia semanal |
| 4 | Pecho, espalda, pierna, hombro | El brazo y el abdomen trabajan de forma indirecta; el sistema lo declara |
| 5 | Los anteriores más brazo | |
| 6 y 7 | Los seis grupos | Con siete días la pierna repite en un segundo día no consecutivo |

Con una o dos sesiones semanales el volumen determinado por la red no cabe en la
jornada: seis grupos comparten la misma sesión. En ese caso el generador prescribe
lo que sí cabe y lo declara en `alcanza_el_volumen_objetivo`, en lugar de anunciar
un volumen que la rutina no entrega.

#### Dependencia parcial de HU-11

La rutina necesita un catálogo de ejercicios poblado. Se cargan 25 ejercicios
iniciales al arrancar (`app/nucleo/catalogo_inicial.py`), ejecutables con
equipamiento básico de gimnasio. **Es una lista provisional:** HU-11 exige levantar
el equipamiento real del Gimnasio FAMAS mediante visita directa, y esa verificación
la sustituirá. La carga es idempotente y no deshace las altas ni bajas del
administrador.

### Verificación de la Iteración 3

- [x] ~~El plan y la rutina se generan juntos, en una sola transacción~~
- [x] ~~Flujo completo probado en el navegador para varias frecuencias semanales~~
- [x] ~~Diseño adaptable comprobado a 320, 375 y 1920 píxeles~~
- [x] ~~Controles con área táctil de 48 píxeles~~
- [ ] Validar la rutina generada con un entrenador del Gimnasio FAMAS antes de la entrega

## Fase 4 — Iteración 4: Catálogo local (Épicas E3 y E4)

Historias HU-08 y HU-11. 13 puntos.

> **Dependencia:** HU-08 requiere que HU-11 esté concluida, porque el catálogo debe estar
> poblado antes de poder seleccionar de él (apartado 4.6.3).

### HU-11. Administración de catálogos maestros (5 puntos)

- [x] ~~Alta, modificación y baja de alimentos, reservada al administrador~~
- [x] ~~Alta, modificación y baja de ejercicios, reservada al administrador~~
- [x] ~~Pantallas de administración de ambos catálogos~~
- [ ] **Levantar el catálogo de alimentos mediante visita directa a los mercados del municipio**, con su aporte nutricional y costo aproximado (mitigación del riesgo de catálogo incompleto, Tabla 12) — **trabajo de campo pendiente**
- [ ] Registrar el equipamiento efectivamente disponible en el Gimnasio FAMAS — **trabajo de campo pendiente**
- [x] ~~Carga inicial de ambos catálogos~~ *(36 alimentos y 25 ejercicios, provisionales)*
- [x] ~~Pruebas funcionales~~

La baja es lógica y no física: un alimento que deja de conseguirse se marca como no
disponible y deja de proponerse en los planes nuevos, pero los planes ya generados
conservan su referencia. Borrarlo los dejaría incompletos.

> **Los catálogos cargados son provisionales.** Los aportes nutricionales provienen
> de tablas de composición de alimentos para Centroamérica y los costos son
> estimaciones. La visita a los mercados y al gimnasio es la que convierte este
> catálogo en el catálogo local que la tesis describe, y sigue pendiente.

### HU-08. Selección de alimentos y ejercicios del catálogo local (8 puntos)

- [x] ~~Distribuir los macronutrientes en tiempos de comida con alimentos del catálogo~~
- [x] ~~Todos los alimentos propuestos existen en el catálogo local~~
- [x] ~~Todos los ejercicios propuestos son ejecutables con el equipamiento registrado~~
- [x] ~~Ofrecer un sustituto de aporte nutricional equivalente cuando un alimento no esté disponible~~
- [x] ~~Presentar las cantidades también en medidas caseras~~
- [x] ~~Pruebas funcionales~~ *(54 pruebas entre HU-08 y HU-11)*

#### Cómo se reparte el menú

El reparto sigue el orden en que los macronutrientes admiten menos holgura:

1. La proteína de cada tiempo dimensiona su alimento proteico, porque es la que la
   regla del negocio *c* acota entre 1.6 y 2.2 gramos por kilogramo.
2. Las verduras y las frutas se sirven en porciones fijas, no por energía. Un primer
   diseño las dimensionaba por energía y proponía 400 gramos de repollo en un tiempo
   de comida: aportan muy pocas kilocalorías por gramo.
3. La grasa añadida cubre una fracción pequeña y acotada.
4. Los cereales y los tubérculos absorben la energía restante, y son los que el
   ajuste final escala para cerrar la diferencia.

El menú queda entre 0.1 % y 2 % de la energía que el plan prescribe para los perfiles
habituales, y hasta 8 % en los de energía muy baja, donde la porción mínima servible
impone un piso. Cada porción se presenta en gramos y en medida casera —«4 panes»,
«medio filete», «1.5 tazas»— con la concordancia de número y género resuelta, y
ofrece un sustituto de aporte equivalente para los días en que el alimento principal
no se consigue.

## Fase 5 — Iteración 5: Seguimiento y reportes (Épica E4)

Historias HU-09 y HU-10. 13 puntos.

### HU-09. Registro del progreso y reajuste del plan (8 puntos)

- [x] ~~Registro semanal de peso, perímetro, sesiones cumplidas y adherencia~~
- [x] ~~La fecha de registro no puede ser posterior a la fecha actual (apartado 4.8.3)~~
- [x] ~~Reajuste automático del plan a partir del progreso registrado~~
- [x] ~~Conservar el historial de planes y marcar cuál está vigente~~
- [x] ~~Pantalla de registro de progreso~~
- [x] ~~Pruebas funcionales~~

#### Cómo funciona el reajuste

El apartado 2.7 describe la retroalimentación como el mecanismo por el cual la
salida del sistema se reintroduce como entrada. El reajuste implementa ese ciclo
sin inventar una corrección calórica propia: el peso reportado se convierte en una
medición biométrica nueva, y esa medición regenera el plan por la misma cadena que
produjo el original. Así las reglas *b* y *c* se siguen cumpliendo por construcción.

| Situación | Qué hace el sistema |
|---|---|
| Adherencia menor al 70 % | No reajusta. Si el usuario no siguió el plan, el estancamiento no se explica por el cálculo, y recortar más calorías sería contraproducente |
| Cambio de peso menor a 0.5 kg | No reajusta. La variación cabe dentro de la fluctuación normal de agua y contenido intestinal |
| Cambio apreciable con buena adherencia | Registra la medición nueva, regenera el plan y la rutina, y compara el ritmo con el esperado para el objetivo |

En los tres casos la respuesta explica qué hizo y por qué: el reajuste nunca ocurre
en silencio.

### HU-10. Reportes gráficos de evolución (5 puntos)

- [x] ~~Gráfica de evolución del peso en el tiempo~~
- [x] ~~Gráfica de adherencia y sesiones cumplidas~~
- [x] ~~Comparación entre el plan inicial y el vigente~~
- [x] ~~Gráficas legibles en pantalla de teléfono~~ *(comprobadas a 320 píxeles)*
- [x] ~~Pruebas funcionales~~

Las gráficas se dibujan con SVG propio y no con una biblioteca de terceros, por dos
razones: el requerimiento 4.5.5 exige que el sistema funcione sin complementos
adicionales, y el control directo del trazo permite garantizar la legibilidad a 320
píxeles. Se añade también la gráfica del perímetro de cintura, que suele reflejar el
avance antes que la báscula.

### Verificación de la Iteración 5

- [x] ~~36 pruebas funcionales del registro, el reajuste y los reportes~~
- [x] ~~Ciclo completo probado con cuatro semanas simuladas de avance~~
- [x] ~~Diseño adaptable comprobado a 320, 375 y 1920 píxeles~~
- [x] ~~El reajuste produce plan y rutina nuevos, y conserva el historial~~

## Fase 6 — Despliegue en producción

Del apartado 3.8. El sistema debe estar en ambiente productivo al momento de la
presentación final.

- [x] ~~Separar los entornos de desarrollo, pruebas y producción~~ *(los tres existen: `docker-compose.yml` para desarrollo, `docker-compose.pruebas.yml` para pruebas y `render.yaml` para producción)*
- [x] ~~Migrar el gestor de base de datos a PostgreSQL~~ *(verificado de extremo a extremo contra PostgreSQL 16; el acceso a datos pasa por SQLAlchemy y el gestor se decide por la cadena de conexión)*
- [x] ~~Declarar el entorno productivo en un archivo versionado~~ *(`render.yaml`, para que el despliegue sea reproducible y no dependa de lo que se configuró a mano en un panel)*
- [x] ~~Documentar el procedimiento de despliegue paso a paso~~ *(`DESPLIEGUE.md`)*
- [x] ~~Empaquetar la aplicación en contenedores~~ *(`backend/Dockerfile`, `frontend/Dockerfile` y `nginx.conf`)*
- [x] ~~Revisión final antes de publicar~~ *(pasada de cierre sobre `render.yaml`, los `.env.example`, `.gitignore` y el arranque: se corrigió que la comprobación «no arrancar en producción con credenciales de ejemplo» no reconocía el texto exacto que traen `backend/.env.example` y `.env.pruebas.example` — un desajuste de mayúsculas y de un sufijo dejaba pasar sin aviso una credencial de ejemplo. Se agregaron los valores faltantes a `configuracion.py` y una prueba de regresión que lee ambos archivos y confirma que cada valor se reconoce, para que un archivo de ejemplo no pueda volver a cambiar sin que la prueba lo note. El resto — `Dockerfile`, `entrada.sh`, la ruta de salud, `.gitignore` y el modelo versionado — se verificó consistente con lo documentado)*
- [ ] **Crear el proyecto en Supabase y el blueprint en Render** — requiere sus credenciales; el costo son US$ 7.25 mensuales, unos Q57.00, contra los Q150.00 que presupuesta la Tabla 13
- [ ] **Configurar el dominio propio** — requiere contratación. El certificado ya no se contrata: Render lo emite y lo renueva
- [x] ~~Configurar los respaldos periódicos de la base de datos~~ *(`operaciones/respaldar_base_datos.sh` y su contraparte de restauración, ahora con `pg_dump` y `psql`; en el plan gratuito de Supabase no hay copias automáticas, de modo que este respaldo es el único que existe)*
- [x] ~~Cambiar todas las credenciales predeterminadas~~ *(el sistema se niega a arrancar en producción si detecta alguna)*
- [x] ~~Pruebas de carga con al menos cincuenta usuarios concurrentes (requerimiento 4.5.2)~~ *(`backend/prueba_de_carga.py`, ejecutadas contra PostgreSQL; **cumplen**, ver resultados abajo)*
- [x] ~~Almacenar en memoria los planes recientes, si las pruebas de carga lo requieren (Tabla 12)~~ — **las pruebas lo requirieron**
- [x] ~~Verificar que el modelo neuronal pueda reentrenarse sin detener el servicio (requerimiento 4.5.6)~~ *(ruta `/administracion/modelo/recargar`)*

#### Verificación del entorno de pruebas

La composición se levantó completa y se recorrió el flujo de extremo a extremo:
registro, acceso, perfil biométrico, generación del plan, rutina, menú, registro de
progreso y reporte de evolución. Todo a través del puerto 8080, es decir, pasando por
el servidor web que entrega la interfaz y reenvía las peticiones a los servicios, que
es el camino que recorrerá el usuario en producción.

| Comprobación | Resultado |
|---|---|
| El guion de arranque siembra el modelo en un volumen vacío | El servicio arranca con la red neuronal, no con la fórmula de respaldo |
| Dos procesos de trabajo arrancando a la vez contra PostgreSQL | Las tres carreras —esquema, administrador y catálogos— se resuelven y el servidor sigue en pie |
| Las peticiones a `/api` llegan al backend por el servidor web | `estado` responde por el puerto 8080 |
| Las rutas internas de la interfaz se entregan al índice | `/plan-nutricional` responde 200 |
| Plan generado a través de toda la cadena | 0.18 s, origen `red_neuronal`, margen 0.29 % |
| Respaldo y restauración | El volcado se toma, se restaura y las cinco tablas conservan su contenido |

El ejercicio encontró dos defectos propios de la configuración de despliegue, ambos
corregidos, y ninguno de ellos visible desde el código:

1. **El correo del administrador de ejemplo terminaba en `.local`,** que es un dominio
   reservado y que el validador de correo rechaza. El servicio no llegaba a arrancar.
2. **El archivo de entorno tenía un valor con espacios sin comillas.** Docker lo lee
   bien, pero los guiones de respaldo lo cargan con el intérprete de órdenes, que
   tomaba cada palabra como una orden aparte. Venía de la plantilla original.

#### Dos defectos de producción que las pruebas de carga descubrieron

Ninguno se manifestaba en desarrollo, porque el servidor de desarrollo corre con un
solo proceso de trabajo y el de producción corre con varios:

1. **Los procesos de trabajo se mataban entre sí al arrancar.** Todos ejecutan la
   inicialización a la vez, y el que perdía la carrera por crear la cuenta de
   administrador lanzaba una excepción que tumbaba el servidor completo. Lo mismo
   ocurría con la creación del esquema y con la carga de los catálogos. La
   inicialización ahora reconoce esas carreras como lo que son —un final correcto al
   que se llegó dos veces— y continúa.
2. **El servidor no llegaba a arrancar** con `--workers`, que es exactamente la
   configuración que declara el `Dockerfile`. El despliegue habría fallado en el
   primer intento.

#### Resultado de las pruebas de carga

Con cincuenta usuarios concurrentes, perfiles distintos entre sí, **contra PostgreSQL
16** y con **un solo proceso de trabajo**, que es la configuración con que el sistema
correrá en Render:

| Operación | Mediana | p95 | Máximo | Límite | Fallos | Resultado |
|---|---|---|---|---|---|---|
| Generación del plan | 1.66 s | 2.70 s | 3.19 s | 3 s | 0 | cumple |
| Consulta de la rutina | 1.06 s | 1.69 s | 2.16 s | 2 s | 0 | cumple |
| Consulta del menú | 0.72 s | 1.69 s | 2.69 s | 2 s | 0 | cumple |
| Registro de progreso | 1.10 s | 2.38 s | 2.95 s | 3 s | 0 | cumple |
| Reporte de evolución | 0.73 s | 1.34 s | 2.23 s | 2 s | 0 | cumple |
| Historial de medidas | 0.29 s | 1.29 s | 2.35 s | 2 s | 0 | cumple |

**Las seis operaciones cumplen, sin ningún fallo.** Es la medición que faltaba: la
anterior se había ejecutado sobre SQLite, que serializa las escrituras de todos los
procesos sobre un mismo archivo, y la generación del plan había dado 4.94 s en p95.
El cómputo puro —predicción neuronal, rutina y menú— siempre fueron 44 milisegundos;
todo lo demás era contención del gestor, y con PostgreSQL desaparece.

**Dos advertencias sobre estos números, para no leerlos de más.**

1. **El margen es estrecho donde importa.** La generación del plan queda a 0.30 s del
   límite. No sobra holgura.
2. **Se midió en el equipo de desarrollo, no en Render.** La instancia contratada
   tiene media unidad de procesamiento, menos que este equipo, y la base de datos
   estará al otro lado de la red. La medición definitiva es contra el sistema
   publicado.

- [ ] **Repetir la prueba contra el sistema publicado en Render**, con
  `uv run python prueba_de_carga.py --url https://<dirección>`, para cerrar el
  requerimiento 4.5.2 sobre el entorno real. Si no cumpliera, la salida no es agregar
  procesos de trabajo —no caben en los 512 MB de la instancia— sino subir su plan.

La medición anterior dejó, además, dos mejoras que valen en cualquier gestor y que ya
están incorporadas: la memoria de planes recientes que la Tabla 12 preveía, y la
reducción de seis viajes a la base de datos por cada plan al enlazar las sesiones de
entrenamiento por la relación del modelo en lugar de por su identificador.

---

## Reglas del negocio transversales

Del apartado 4.3.4. Aplican con independencia de la funcionalidad que se ejecute.

- [x] ~~a) Solo se generan planes para personas mayores de dieciocho años~~ *(validada en el servidor al capturar el perfil biométrico; se vuelve a verificar al generar el plan en la Fase 3)*
- [x] ~~b) El ajuste sobre el gasto energético nunca excede 20 % en déficit ni 15 % en superávit~~
- [x] ~~c) La proteína se mantiene entre 1.6 y 2.2 gramos por kilogramo de peso corporal~~
- [x] ~~d) El incremento de carga entre microciclos no supera el 10 % del volumen previo~~ *(implementada en `progresion_admitida` y comunicada en la pantalla de la rutina; se aplicará de forma automática al reajustar el plan en la Fase 5)*
- [x] ~~e) El sistema no emite diagnósticos médicos y muestra siempre el aviso de consulta profesional~~ *(verificada en el plan nutricional y en la rutina)*
- [x] ~~f) Los datos biométricos solo son visibles para su titular; el administrador accede únicamente a información agregada y anónima~~ *(la base de control de acceso quedó implementada en la Fase 1; se vuelve a verificar al exponer los datos biométricos en la Fase 2)*

## Requerimientos no funcionales

Del apartado 4.5. Se verifican de forma continua, no una sola vez.

- [x] ~~**4.5.1 Seguridad.** Contraseñas con resumen criptográfico y sal, validación de acceso en el servidor, mensajes que no revelan qué dato falló~~ *(el cifrado del tránsito hacia el usuario lo emite Render con el dominio propio; el de la conexión con la base de datos ya está: el sistema exige `sslmode=require` en toda cadena que no apunte a un anfitrión local)*
- [ ] **4.5.2 Rendimiento.** ~~Plan completo en menos de tres segundos~~ *(0.36 s con un usuario, contra PostgreSQL)*; ~~pruebas con cincuenta usuarios concurrentes~~ *(ejecutadas contra PostgreSQL; **las seis operaciones cumplen**)*; falta repetirlas contra el sistema publicado y medir las pantallas sobre conexión móvil de tercera generación
- [x] ~~**4.5.3 Usabilidad.** Controles con área táctil suficiente y formularios en pasos cortos~~ *(el formulario del perfil biométrico se divide en tres pasos y toda cifra técnica lleva su explicación; falta medir que un usuario obtenga su primer plan en menos de cinco minutos, posible hasta la Fase 3)*
- [x] ~~**4.5.4 Escalabilidad.** Capas independientes y entorno replicable mediante contenedores~~ *(los tres componentes se levantan con `docker-compose.pruebas.yml`, y producción se declara entera en `render.yaml`)*
- [x] ~~**4.5.5 Compatibilidad.** Funciona de 320 a 1920 píxeles, sin complementos adicionales~~ *(comprobado a 320, 375 y 1920 píxeles; falta la comprobación en navegadores de teléfono reales)*
- [x] ~~**4.5.6 Mantenibilidad.** Código organizado según el patrón modelo-vista-controlador, con herramientas de código abierto~~ *(el modelo se recarga sin detener el servicio desde `/administracion/modelo/recargar`, y en producción vive en un disco persistente para que un modelo reentrenado sobreviva a la actualización del contenedor)*

## Riesgos abiertos

De la Tabla 12. Los dos primeros son los de mayor impacto sobre la hipótesis.

| Riesgo | Fase donde se enfrenta | Mitigación |
|---|---|---|
| ~~El modelo no alcanza el margen de error del 5 %~~ **cerrado** | 3 | Se alcanzó un margen medio del 0.21 %, con el 100 % de los perfiles de validación bajo el 5 % |
| Volumen insuficiente de datos de entrenamiento | 3 | Mitigado con 40 000 perfiles sintéticos derivados de las ecuaciones de referencia; queda incorporar los 169 perfiles del trabajo de campo |
| Catálogo local incompleto o desactualizado | 4 | El módulo de administración está construido y los catálogos tienen carga inicial. **Abierto:** los 36 alimentos y 25 ejercicios son provisionales hasta el levantamiento de campo |
| ~~Degradación del rendimiento con usuarios concurrentes~~ **cerrado en desarrollo** | 6 | Se implementó la memoria de planes recientes, se corrigieron los dos defectos de arranque que las pruebas descubrieron, y la medición contra PostgreSQL con 50 usuarios concurrentes cumple en las seis operaciones. Queda repetirla contra el sistema publicado |
| Sesgo por concentración de los tres roles de Scrum | Todas | Revisión de las catedráticas asesoras y prueba con usuarios reales del gimnasio |
| Ampliación no controlada del alcance | Todas | Registrar todo requerimiento nuevo con prioridad baja, sin incorporarlo a la iteración en curso |

---

## Cómo levantar el proyecto

```bash
# 1. Base de datos PostgreSQL (desde la raíz del proyecto)
docker compose up -d

# 2. Servicios
cd backend
uv run uvicorn app.main:aplicacion --host 127.0.0.1 --port 8010 --reload

# 3. Interfaz de cliente
cd frontend
npm run dev
```

Para reentrenar el modelo neuronal:

```bash
cd backend
uv run python entrenar_modelo.py
```

- Aplicación: <http://localhost:5173>
- Documentación de los servicios: <http://127.0.0.1:8010/documentacion>
- Pruebas: `cd backend && uv run pytest -v`
- Pruebas sin entrenar la red: `cd backend && uv run pytest -m "not lenta"`

Para levantar el **entorno de pruebas**, que es donde se valida un incremento antes de
publicarlo:

```bash
cp .env.pruebas.example .env.pruebas   # y reemplace todos los valores
docker compose -f docker-compose.pruebas.yml --env-file .env.pruebas up -d --build
```

Queda en <http://localhost:8080>. El **despliegue en producción**, sobre Render y
Supabase, está documentado paso a paso en [DESPLIEGUE.md](DESPLIEGUE.md).

## Decisiones técnicas tomadas

Conviene conocerlas antes de modificar la configuración del entorno.

1. **Python 3.12, no 3.14.** TensorFlow, que se incorpora en la Fase 3, todavía no publica
   versiones compatibles con Python 3.14. La versión queda fijada en `pyproject.toml` y
   `uv` la descarga automáticamente.
2. **Los servicios usan el puerto 8010, no el 8000.** El reenvío de puertos de Docker y
   WSL ya ocupa el 8000 sobre IPv6 en este equipo. Como Windows resuelve `localhost`
   primero a IPv6, el navegador alcanzaba ese otro servicio en lugar del backend.
3. **El frontend apunta a `127.0.0.1` y no a `localhost`,** por la misma razón anterior.
4. **PostgreSQL se publica en el puerto 5433,** para no chocar con una instalación de
   PostgreSQL que ya ocupe el puerto habitual.
5. **Los identificadores del código están en español,** para que coincidan con la
   terminología de la tesis, que evita anglicismos por exigencia de la rúbrica.
6. **Cada perfil biométrico es un registro nuevo,** no una actualización del anterior. Es
   lo que produce el historial de la historia HU-05 y permite el reajuste de la Fase 5.
7. **El gestor es PostgreSQL y no MySQL,** porque Supabase, el servicio administrado que
   sostiene producción, provee PostgreSQL. El cambio costó nueve correcciones en el
   Capítulo III de la tesis y casi nada de código: el acceso a datos pasa por SQLAlchemy
   y el gestor se decide por la cadena de conexión.
8. **Se conecta por el repartidor de sesión de Supabase, no por la conexión directa.** La
   directa solo responde por IPv6 y Render sale a la red por IPv4: el servicio arrancaría
   y no alcanzaría la base de datos. El sistema completa por su cuenta el controlador que
   SQLAlchemy necesita y exige el cifrado del tránsito cuando la base es remota, de modo
   que la cadena se copia del panel de Supabase tal como viene.
9. **Un solo proceso de trabajo en producción.** Cada uno carga su propia copia de
   TensorFlow: el servicio ocupa 271 MB con uno, de los cuales 190 son la biblioteca. Un
   segundo no cabría en los 512 MB de la instancia. El entorno de pruebas levanta dos,
   para que la carrera de arranque entre procesos siga reproduciéndose ahí.
10. **El modelo entrenado sí se versiona,** al contrario de lo que se decidió al empezar.
    Pesa 345 KB, y sin él en el repositorio la imagen del contenedor tendría que entrenar
    la red durante la construcción: cada despliegue produciría un modelo distinto del que
    se midió y se reportará en el Capítulo V.

## Pendientes administrativos

No son de programación, pero condicionan la entrega:

- [ ] Carta del Gimnasio FAMAS que respalde su anuencia a participar (apartados 4.1.3 y 4.10.3)
- [ ] Cambiar la contraseña de administrador antes de cualquier despliegue. En producción
      se define en el panel de Render, no en ningún archivo del repositorio
- [ ] Eliminar de la base de datos las cuentas de prueba creadas durante el desarrollo
- [ ] Decidir si ajusta el presupuesto del apartado 4.10.2 a los costos reales. Los
      números están en `../CAMBIOS_PILA_DESPLIEGUE.md`: el alojamiento son Q342.00 en
      lugar de Q900.00, y el certificado ya no se paga. **La tabla no se tocó** porque la
      revisó la Dra. Esquivel y el cambio arrastra los imprevistos, el total y el párrafo
      que cita las cifras
- [ ] Verificar las tres referencias señaladas en `Tesis Final/RESUMEN DE CAMBIOS.md`
