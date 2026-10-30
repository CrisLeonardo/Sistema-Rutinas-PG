# Guía de contenido para la presentación del Proyecto de Graduación II

> **Para quién es este archivo:** para Claude Design (o cualquier herramienta que arme las diapositivas).
> **Qué contiene:** únicamente el *contenido* —textos, cifras, orden de las diapositivas y qué imagen corresponde a cada una—, tomado de la tesis vigente (*Entrega 3*, 12 de octubre de 2026) y del sistema real en ejecución.
> **Qué NO contiene:** ninguna indicación de diseño (colores, tipografías, plantillas, composición, animaciones). Eso se pide aparte.
> **Idioma:** español de Guatemala. Mantener el vocabulario de la tesis.

Carpetas que acompañan a esta guía (deben viajar juntas con ella):

- `capturas/` — 32 capturas del sistema funcionando, tomadas para esta presentación.
- `figuras_tesis/` — 30 figuras (diagramas y gráficas) extraídas de la tesis, para apoyar las diapositivas.

---

## 0. Reglas de honestidad (leer antes de armar nada)

1. **Las capturas son de un entorno local con datos de demostración**, no de producción. Los nombres (Lucía Morales, Carlos Pérez, etc.) son ficticios. Las cifras que se ven en pantalla (por ejemplo 1,893 kcal, 67.5 kg) pertenecen a esa usuaria ficticia; **no** son resultados de investigación y no deben presentarse como tales. Poner siempre el rótulo «Captura del sistema con datos de demostración».
2. **Las cifras de validación** (margen de error de 0.11 %, 658 pruebas, 0.36 s, etc.) son las de la tesis y sí son resultados medidos. Están en la sección 3 de esta guía, con su origen.
3. **Estado del despliegue en producción:** el sitio estático `https://rutinas-interfaz.onrender.com` responde, pero **el servicio de cálculo no responde**. La tesis (apartado 6.1) atribuye la causa a la suspensión del proyecto gratuito de base de datos en Supabase; el 22 de octubre de 2026 se comprobó de nuevo que la ruta `/api/v1/estado` no contesta. No afirmar que el sistema está «en producción atendiendo usuarios». Decir: «desplegado en la nube y pendiente de reactivar la base de datos antes de la puesta en marcha con usuarios reales».
4. **Límites de la validación que deben declararse** (están en la tesis): los 8,000 + 10,000 perfiles evaluados son **sintéticos** (la encuesta no recogió medidas biométricas); los «métodos empíricos» se representaron con tres reglas de uso común; la usabilidad (escala 1–5) y el efecto sobre la constancia real de los usuarios **quedan pendientes** del grupo piloto.
5. No inventar cifras. Si una diapositiva necesita un número que no está en esta guía, dejarlo fuera.

---

## 1. Datos de identificación (para la portada)

| Campo | Valor |
|---|---|
| Título aprobado | **Sistema web con redes neuronales para automatizar regímenes nutricionales y rutinas de entrenamiento en El Progreso, Jutiapa** |
| Estudiante | Cristopher Leonardo Zepeda Esquivel |
| Carné | 0905-22-18060 |
| Universidad | Universidad Mariano Gálvez de Guatemala, Campus Jutiapa |
| Facultad | Facultad de Ingeniería en Sistemas de Información |
| Curso | Proyecto de Graduación II |
| Docente | Dra. Sheyla Yadira Esquivel |
| Docente auxiliar | Licda. Evelyn Amalia Aguilar Ordóñez |
| Fecha | Jutiapa, octubre de 2026 |
| Institución participante | Gimnasio Fama’s Fitness Club, zona urbana de El Progreso, Jutiapa |
| Dirección del sistema | https://rutinas-interfaz.onrender.com |

---

## 2. Estructura propuesta (24 diapositivas + apéndice)

Los diez apartados que exige la cátedra están marcados con **[1]…[10]**; el resto son agregados que la guía considera fundamentales.

| N.º | Diapositiva | Apartado exigido |
|---|---|---|
| 1 | Portada | [1] Título aprobado |
| 2 | El problema en El Progreso | agregado (contexto) |
| 3 | Formulación del problema y preguntas de investigación | [2] |
| 4 | Objetivos | [3] |
| 5 | Hipótesis y variables | [4] |
| 6 | La muestra | [5] |
| 7 | Lo que dijo la muestra y cómo moldeó el sistema | [5] (continuación) |
| 8 | El proyecto: qué es y cómo funciona | [6] |
| 9 | Arquitectura del sistema | [6] (continuación) |
| 10 | Módulo 1 · Autenticación y seguridad | [7] |
| 11 | Módulo 2 · Perfil biométrico | [7] |
| 12 | Módulo 3 · Motor neuronal: el plan nutricional | [7] |
| 13 | Módulo 3 · Rutina de entrenamiento | [7] |
| 14 | Módulo 4 · Catálogo de alimentos y ejercicios | [7] |
| 15 | Módulo 5 · Seguimiento y adaptabilidad | [7] |
| 16 | Informes | [7] (complemento) |
| 17 | Herramientas utilizadas | [8] |
| 18 | Resultados de la validación | agregado (evidencia) |
| 19 | Implementación en producción | [9] |
| 20 | Factibilidad e inversión | agregado |
| 21 | Aporte del proyecto | [10] |
| 22 | Límites y trabajo futuro | agregado (honestidad científica) |
| 23 | Conclusiones | agregado |
| 24 | Cierre y preguntas | agregado |
| A1–A4 | Apéndice (demostraciones extra) | opcional |

**Si el tiempo es corto**, las diapositivas que pueden fusionarse o quitarse sin perder ninguno de los diez apartados son: 7 (fusionar con 6), 16 (fusionar con 15), 20 (fusionar con 21) y 23 (fusionar con 24).

---

## 3. Cifras verificadas (única fuente de números para las diapositivas)

### 3.1 La muestra y el trabajo de campo (tesis, apartado 1.13)

| Dato | Valor |
|---|---|
| Población estimada | 300 usuarios concurrentes de centros de acondicionamiento físico del municipio |
| Muestra | **169 usuarios** (muestreo probabilístico aleatorio simple) |
| Fórmula | n = (N · Z² · σ²) / ((N − 1) · e² + Z² · σ²) con N = 300, Z = 1.96 (95 %), σ = 0.5, e = 0.05 → n ≈ 169 |
| Instrumento | Cuestionario digital estructurado de **18 reactivos** en 3 secciones: datos generales (3), hábitos de entrenamiento y nutrición (8), acceso a la tecnología y disposición de uso (7) |
| Sexo | 59.2 % masculino · 39.1 % femenino · 1.8 % prefirió no indicar |
| Edad | 39.6 % de 18 a 24 años · 30.2 % de 25 a 30 · **89.9 % menor de 41 años** |
| Sin plan de entrenamiento definido | **53.8 %** (solo 17.2 % tiene uno hecho por un entrenador certificado) |
| Sin plan nutricional definido | **69.8 %** (solo 10.1 % tiene uno hecho por un nutricionista) |
| Nunca ha recibido asesoría profesional | 74.0 % (52.1 % nunca + 21.9 % por razones económicas) |
| Dificultades por no tener plan (varias respuestas) | estancamiento 56.2 % · confusión sobre qué y cuánto comer 43.8 % · lesiones por mala ejecución 32.0 % · abandono temporal 23.1 % |
| Capacidad de gasto en asesoría | 76.3 % puede gastar menos de Q400 al mes; 13 % no puede pagar |
| Costo de asesoría privada | Q400 a Q800 al mes = 18 % a 37 % del ingreso laboral promedio de Jutiapa (Q2,175.10) |
| Objetivo principal | 40.8 % perder peso o grasa · 29.0 % ganar masa muscular |
| Conocimiento de calorías y macronutrientes | 60.3 % se ubica en los niveles más bajos (1 y 2 de 5) |
| Dispositivo principal | **72.2 % teléfono inteligente** |
| Facilidad percibida para usar una plataforma web | 57.4 % (niveles 4 y 5) |
| Disposición a usar el sistema | **81.7 %** (43.2 % «definitivamente sí» + 38.5 % «probablemente sí»); solo 6.5 % reacio |
| Mayor beneficio percibido | ahorro en asesorías 36.7 % · planes en cualquier momento 24.3 % · seguimiento automático 21.9 % |
| Función adicional más pedida | recordatorios automáticos 69.8 % · lista de compras 40.8 % |
| Disposición según género | 82.0 % hombres y 81.8 % mujeres: la aceptación no depende del género |

### 3.2 El modelo neuronal y su validación (tesis, apartados 6.3.3.1 y Anexo 3)

| Dato | Valor |
|---|---|
| Entradas del modelo | **8**: peso, estatura, edad, sexo, nivel de actividad, objetivo, nivel de experiencia, días de entrenamiento por semana |
| Capas ocultas | 3, de **128, 128 y 64** neuronas |
| Salidas | **5**: energía (kcal), proteína, carbohidrato, grasa y series semanales por grupo muscular |
| Entrenamiento | 32,000 perfiles de entrenamiento + 8,000 de validación · 400 épocas · TensorFlow y Keras |
| Error absoluto medio (energía) | **2.6 kcal** (0.02 series en el volumen de entrenamiento) |
| Margen de error medio frente a Mifflin-St Jeor y Harris-Benedict | **0.11 %** |
| Margen máximo | 2.69 % (validación) · 3.69 % (evaluación independiente de 10,000 perfiles con otra semilla) |
| Perfiles con margen menor al 5 % | **100 %** |
| Criterio de aceptación fijado en los objetivos | margen menor al 5 % |
| Métodos empíricos comparados | plan genérico de 2,000 kcal (29.74 % de error medio) · valor por sexo 2,000/2,500 kcal (28.05 %) · regla de 30 kcal por kg (17.31 %) |
| Red neuronal en esa misma comparación | 0.12 % de error medio; más precisa en 99.5 % a 99.7 % de los perfiles |
| Prueba estadística | Wilcoxon de rangos con signo: z = 37.7, p < 0.001 |
| Error medio de los métodos empíricos expresado en energía | 419 a 773 kcal diarias (frente a 2.5 kcal de la red) |
| Tiempo de generación del plan | **0.36 s** con un usuario · **2.70 s** (percentil 95) con 50 usuarios concurrentes · 0 fallos · criterio: menos de 3 s |
| Pruebas automatizadas | **658 casos aprobados, 0 fallidos**, en 18 archivos (tesis, ejecución del 12 de octubre de 2026; reconfirmado el 22 de octubre de 2026 sobre el código actual: 658 aprobados en 5 min 4 s) |
| Distribución de las pruebas | motor neuronal 296 · catálogo 102 · seguimiento 86 · perfiles 68 · autenticación 47 · despliegue 32 · informes 27 |

**Decisión sobre la hipótesis (tesis, Anexo 3):** *se acepta*. Se descompuso en cuatro componentes —automatiza (0.36 s), de forma precisa (0.11 %), personalizada (8 variables + lesiones + condiciones médicas) y superando a los métodos empíricos (p < 0.001)— y los cuatro se cumplen.

### 3.3 El sistema (tesis, capítulos IV, V y VI; verificado contra el código)

| Dato | Valor |
|---|---|
| Módulos funcionales | **5**: autenticación y seguridad · perfiles de usuario · motor neuronal · catálogo de alimentos y ejercicios · seguimiento y adaptabilidad |
| Metodología | Scrum (iterativo e incremental): 11 historias de usuario, 4 épicas (E1 Acceso seguro · E2 Perfil biométrico · E3 Generación de planes · E4 Seguimiento y administración) |
| Arquitectura | cliente-servidor en 3 capas (presentación · lógica y servicios · persistencia), patrón Modelo-Vista-Controlador, API REST con intercambio en JSON |
| Código | 19 pantallas · 11 enrutadores de API · 15 tablas en la base de datos |
| Catálogo local | **36 alimentos** (con costo en quetzales y medida casera) y **25 ejercicios** (con equipamiento) |
| Reglas del negocio clave | RN-02 ajuste calórico: déficit hasta 20 % y superávit hasta 15 % · RN-03 proteína entre 1.6 y 2.2 g por kg · RN-04 la carga no sube más de 10 % entre microciclos · RN-05 aviso de consulta profesional en todo plan · RN-06 el administrador nunca ve datos biométricos individuales |
| Salvaguarda de salud | con una condición médica severa declarada (cardiopatía, hipertensión no controlada, diabetes, enfermedad renal, trastorno alimentario) el sistema **no genera plan** y remite a un profesional; con una lesión (hombro, codo o muñeca, espalda baja, rodilla, tobillo) la rutina omite los ejercicios que cargan esa zona |
| Seguridad | contraseñas cifradas · sesión con vencimiento a 30 min de inactividad (aviso 2 min antes) · bloqueo de 15 min tras 8 intentos fallidos en 5 min · permisos comprobados en el servidor · HTTPS |
| Senda de adherencia | 10 niveles, 18 insignias, puntos por constancia |
| Informes | 8 informes (4 personales y 4 de administración), cada uno en 5 formas: pantalla, Excel, CSV, PDF e impresión |
| Interfaz | funciona de 320 a 1,920 píxeles de ancho · instalable en el teléfono (aplicación web progresiva) · tema claro y oscuro · áreas táctiles de al menos 44 px |

### 3.4 Producción y costos (tesis, apartados 3.8, 4.10, 6.1 y 6.2)

| Dato | Valor |
|---|---|
| Proveedor de nube | Render, región Ohio (us-east-2), la más cercana a Guatemala |
| Componentes | (1) sitio estático «rutinas-interfaz» con la interfaz compilada; (2) servicio web «rutinas-servicios» en contenedor Docker con Uvicorn + FastAPI + TensorFlow, un proceso de trabajo; (3) PostgreSQL 16 administrado por Supabase, con copias de seguridad |
| Infraestructura como código | archivo `render.yaml` versionado: el entorno es reproducible |
| Comunicación | el sitio estático reenvía la ruta `/api/*` al servicio: un solo dominio, sin peticiones de origen cruzado |
| Verificación de salud | ruta `/api/v1/estado`; si no responde, Render cancela la publicación y conserva la versión anterior |
| Certificado | HTTPS con renovación automática; el acceso sin cifrar redirige (301) a la versión segura |
| Plan de implementación | **6 fases en 8 semanas**: (1) preparación del entorno · (2) despliegue técnico · (3) carga de datos maestros · (4) verificación en producción · (5) capacitación y puesta en marcha · (6) seguimiento y estabilización |
| Responsables | estudiante investigador (técnico) · administración del gimnasio (dueña del proceso) · entrenador del gimnasio (valida rutinas) · grupo piloto (aceptación) · catedráticas asesoras (supervisión académica) |
| Estado a octubre de 2026 | hecho: repositorio publicado, dos servicios creados en Render, interfaz responde en su dirección pública, dominio y certificado verificados. Pendiente: reactivar la base de datos, pasar el servicio al plan de pago (el gratuito se suspende a los 15 min sin tráfico), cargar el catálogo levantado en campo y ejecutar las fases 3 a 6 con el gimnasio |
| Presupuesto total (valor de los recursos) | Q26,695, de los cuales Q24,000 son las 480 horas del investigador (valoradas a Q50/h) |
| Desembolso monetario real | **Q2,695** |
| Costo de operación una vez construido | Q1,150 por semestre (alojamiento y dominio) |
| Ahorro estimado para la comunidad | con 100 usuarios en el primer año: entre Q480,000 y Q960,000 (asesoría de Q400 a Q800 mensuales por persona) |
| Metas del negocio | 100 usuarios en el primer mes en el gimnasio · 80 % de planes calificados como útiles · respuesta de plan menor a 3 s |

---

## 4. Inventario de recursos visuales

### 4.1 Capturas del sistema (`capturas/`)

Formato: las capturas «móvil» miden 780 × 1688 px (pantalla de teléfono, 390 × 844 con densidad doble); las «largas» tienen 780 px de ancho y la altura necesaria para mostrar la pantalla completa; las «escritorio» miden 2880 × 1800 px.

Cuentas de demostración: **Lucía Morales** (mujer de 28 años, 165 cm, 70 kg al inicio y 67.5 kg tras seis semanas de seguimiento; objetivo perder grasa; principiante; 4 días por semana), **Carlos Pérez** (hombre de 24 años, intermedio, 5 días, lesión de rodilla), **Daniela Castillo** (cuenta nueva, sin datos), **Roberto Aguilar** (declaró diabetes) y el administrador.

| Archivo | Qué muestra | Tipo |
|---|---|---|
| `01_acceso.png` | Pantalla de inicio de sesión | móvil |
| `02_registro.png` | Registro de cuenta, paso 1 de 2 (nombre, correo, contraseña con regla visible) | móvil |
| `03_panel_primer_uso.png` | Pantalla «Hoy» de una cuenta nueva: los tres pasos iniciales | móvil |
| `04_panel_hoy.png` | Pantalla «Hoy»: energía y macronutrientes del día, sesión de entrenamiento, nivel de la senda | móvil |
| `05_medidas_paso1_cuerpo.png` | Formulario de medidas, paso 1 de 4: peso, estatura, edad, sexo e índice de masa corporal en vivo | móvil |
| `05_medidas_paso2_actividad.png` | Paso 2 de 4: nivel de actividad y objetivo | móvil |
| `05_medidas_paso3_entrenamiento.png` | Paso 3 de 4: experiencia y días de entrenamiento por semana | móvil |
| `05_medidas_paso4_salud.png` | Paso 4 de 4: lesiones y condiciones médicas | móvil |
| `06_plan_nutricional.png` | Plan generado por la red neuronal: energía diaria, gasto en reposo y con actividad, agua, reparto de macronutrientes, comprobación contra Mifflin-St Jeor y Harris-Benedict, ajustes de seguridad y aviso profesional | larga |
| `07_menu_diario.png` | Menú del día en cinco tiempos de comida, en gramos y medida casera, con costo del día | larga |
| `08_lista_compras.png` | Lista de compras semanal por categoría, con costo estimado y casillas para marcar | larga |
| `09_rutina_semanal.png` | Rutina semanal: sesión del día, distribución por día de la semana, aviso «ningún músculo se entrena dos días seguidos» | larga |
| `10_sesion_en_curso.png` | Sesión de entrenamiento en curso (sin barra de navegación): carga sugerida, repeticiones y peso por serie | móvil |
| `10_sesion_series_marcadas.png` | La misma sesión con tres series marcadas y el cronómetro de descanso activo | móvil |
| `11_bitacora.png` | Bitácora: racha, volumen de la semana, evolución de una marca y sesiones registradas | larga |
| `11_marcas_de_carga.png` | Marcas: carga más alta movida en cada ejercicio, con su evolución | larga |
| `12_avance_registro_peso.png` | Registro semanal de peso, cumplimiento del plan y sesiones | larga |
| `13_evolucion.png` | Evolución: curva de peso, sesiones por semana, cumplimiento y cintura | larga |
| `14_historial_medidas.png` | Historial de medidas: medición vigente y mediciones anteriores | larga |
| `15_senda_nivel.png` | Senda: nivel, puntos y progreso hacia el siguiente nivel | móvil |
| `15_senda_insignias.png` | Senda: insignias obtenidas y bloqueadas por categoría | móvil alto |
| `16_informes.png` | Informes personales: selector de informe, botones Excel, CSV, PDF e Imprimir, y el informe en pantalla | larga |
| `17_mas_ajustes.png` | Sección «Más»: accesos directos, tema oscuro, vibración del cronómetro, cambio de contraseña | larga |
| `18_tema_oscuro_hoy.png` | Pantalla «Hoy» con el tema oscuro activado | móvil |
| `19_escritorio_hoy.png` | Pantalla «Hoy» en computadora (diseño adaptable) | escritorio |
| `19_escritorio_evolucion.png` | Evolución en computadora | escritorio |
| `20_rutina_con_lesion.png` | Rutina de una persona con lesión de rodilla, con el aviso de que se omiten los ejercicios que cargan esa zona | larga |
| `21_condicion_medica_panel.png` | Pantalla «Hoy» de una cuenta con condición médica severa declarada | móvil |
| `21_condicion_medica_plan.png` | El sistema se niega a generar el plan y remite a un profesional de la salud | móvil |
| `22_admin_catalogos.png` | Administración de catálogos: 36 alimentos con calorías, proteína, costo y estado | escritorio |
| `23_admin_cuentas.png` | Administración de cuentas: roles, estado, indicadores de cuentas | escritorio |
| `24_admin_informes.png` | Informes del administrador: indicadores de uso agregados y anónimos | escritorio |

### 4.2 Figuras de la tesis (`figuras_tesis/`)

| Archivo (prefijo) | Contenido | Figura en la tesis |
|---|---|---|
| `fig01_…` | Ubicación del gimnasio Fama’s Fitness Club en el mapa satelital | 1 |
| `fig02_…` `fig03_…` | Distribución de los encuestados por género y por rango de edad | 2, 3 |
| `fig05_…` | Tipo de plan de entrenamiento que poseen los encuestados | 5 |
| `fig06_…` | Tipo de plan nutricional que poseen los encuestados | 6 |
| `fig08_…` | Dificultades por la falta de un plan profesional | 8 |
| `fig09_…` | Capacidad de gasto mensual en asesoría profesional | 9 |
| `fig12_…` | Nivel de conocimiento sobre calorías y macronutrientes | 12 |
| `fig13_…` | Dispositivo más utilizado para acceder a internet | 13 |
| `fig15_…` | Disposición a utilizar el sistema web propuesto | 15 |
| `fig16_…` | Mayor beneficio percibido del sistema | 16 |
| `fig23_…` | Estructura de una red neuronal artificial multicapa | 23 |
| `fig29_…` | Diagrama de contexto del sistema | 29 |
| `fig31_…` | Diagrama de flujo del proceso de generación y reajuste del plan | 31 |
| `fig34_…` | Arquitectura en tres capas | 34 |
| `fig36_…` | Arquitectura técnica y despliegue (cliente · Render · Supabase) | 36 |
| `fig37_…` | Diagrama de componentes y paquetes | 37 |
| `fig41_…` | Modelo conceptual de datos | 41 |
| `fig42_…` `fig43_…` | Modelo entidad-relación, partes 1 y 2 | 42, 43 |
| `fig46_…` | Mapa de navegación del sistema | 46 |
| `fig49_…` | Casos de uso por actor | 49 |
| `fig51_…` | Diagrama de secuencia de la generación del plan | 51 |
| `fig53_…` | Proceso **actual** para obtener un plan (sin el sistema) | 53 |
| `fig54_…` | Proceso **sistematizado** para obtener un plan (con el sistema) | 54 |
| `fig55_…` | Fases del plan de implementación en producción (8 semanas) | 55 |
| `fig56_…` | Casos de prueba automatizados por módulo | 56 |
| `fig62_…` | Precisión de la red neuronal frente a los métodos empíricos | 62 |
| `fig79_…` | Salida del guion de evaluación de la precisión del modelo | 79 |
| `fig80_…` | Salida de la ejecución de las pruebas automatizadas | 80 |

---

## 5. Contenido diapositiva por diapositiva

Cada diapositiva trae: **mensaje central**, **contenido** (textos y cifras que deben aparecer), **recursos** (archivos) y **notas del expositor** (lo que se dice en voz alta; no va en pantalla).

---

### Diapositiva 1 — Portada · [1] Título aprobado

**Mensaje central:** presentar el proyecto con su título aprobado.

**Contenido:**
- Título aprobado (completo, exactamente como figura en la sección 1).
- Estudiante, carné, curso, universidad, facultad, campus, docentes y fecha (sección 1).

**Recursos:** ninguno obligatorio. Opcional: `capturas/04_panel_hoy.png`.

**Notas del expositor:** saludo, nombre y una frase: «Este proyecto lleva la planificación de la nutrición y del entrenamiento, que hoy cuesta entre Q400 y Q800 al mes, a cualquier teléfono de El Progreso».

---

### Diapositiva 2 — El problema en El Progreso (contexto)

**Mensaje central:** hay demanda de actividad física, pero no hay orientación profesional al alcance de la mayoría.

**Contenido:**
- Creciente interés por el bienestar físico y por los centros de acondicionamiento en El Progreso, Jutiapa.
- La asesoría privada de nutrición y entrenamiento cuesta **Q400–Q800 al mes**: entre el **18 % y el 37 %** del ingreso laboral promedio de Jutiapa (Q2,175.10).
- Resultado: la gente recurre a métodos empíricos o a planes genéricos de internet que no consideran su metabolismo ni su historial de lesiones.
- Lo que mostró el trabajo de campo (169 personas): **53.8 %** entrena sin plan · **69.8 %** come sin plan · **74 %** nunca ha tenido asesoría profesional.
- Consecuencias que reportan: estancamiento (56.2 %), confusión sobre qué y cuánto comer (43.8 %), lesiones (32.0 %).

**Recursos:** `figuras_tesis/fig05_…`, `fig06_…`, `fig08_…`, `fig09_…`; opcional `fig53_…` (proceso actual sin el sistema).

**Notas del expositor:** el problema no es falta de interés, es falta de acceso. El 76.3 % no puede gastar Q400 o más en asesoría.

---

### Diapositiva 3 — Formulación del problema · [2]

**Mensaje central:** la pregunta que guía toda la investigación.

**Contenido:**
- **Formulación:** «¿De qué manera la implementación de un sistema web basado en redes neuronales automatiza y optimiza los regímenes nutricionales y las rutinas de entrenamiento de las personas del municipio de El Progreso, Jutiapa?»
- Tres preguntas de investigación derivadas:
  1. ¿Qué precisión puede alcanzar una red neuronal para calcular dietas y rutinas frente a los métodos tradicionales del municipio?
  2. ¿Qué datos biométricos y de estilo de vida son esenciales para que los planes sean individualizados y no genéricos?
  3. ¿De qué manera una plataforma web interactiva facilita la constancia en las metas de salud frente al registro físico o no sistemático?
- Elementos del problema: desinformación biométrica del usuario, ausencia de control de cargas progresivas, déficit en la estructuración de macronutrientes.

**Recursos:** ninguno obligatorio.

**Notas del expositor:** adelantar que las tres preguntas se responden más adelante con evidencia (diapositivas 12, 18 y 22).

---

### Diapositiva 4 — Objetivos · [3]

**Mensaje central:** un objetivo general y tres específicos, cada uno medible.

**Contenido:**
- **Objetivo general:** implementar un sistema web basado en redes neuronales para la automatización de regímenes nutricionales y rutinas de entrenamiento personalizadas, con el propósito de optimizar la precisión y el seguimiento de los planes de salud física de las personas del municipio de El Progreso, Jutiapa.
- **Específicos:**
  a) Diseñar un modelo de red neuronal artificial que procese las variables biométricas del usuario para calcular requerimientos calóricos exactos y estructurar cargas de entrenamiento adaptadas al perfil.
  b) Desarrollar una plataforma web adaptable que integre un catálogo de alimentos y ejercicios acordes a la disponibilidad de El Progreso, Jutiapa.
  c) Validar la precisión del sistema mediante evaluaciones comparativas frente a fórmulas de cálculo metabólico estandarizadas.
- Cumplimiento (una línea por objetivo, con la cifra): a) modelo de 8 entradas y 5 salidas, error medio de 2.6 kcal · b) plataforma instalable con 36 alimentos y 25 ejercicios, 102 casos de catálogo aprobados · c) margen medio de 0.11 %, 100 % de los perfiles bajo el 5 %.

**Recursos:** ninguno obligatorio.

**Notas del expositor:** los tres objetivos corresponden a tres etapas: modelo, plataforma, validación.

---

### Diapositiva 5 — Hipótesis y variables · [4]

**Mensaje central:** la hipótesis se formuló de manera comprobable y se aceptó con evidencia.

**Contenido:**
- **Hipótesis:** «La implementación de un sistema web basado en redes neuronales automatiza de forma precisa y personalizada la generación de regímenes nutricionales y rutinas de entrenamiento para las personas del municipio de El Progreso, Jutiapa, superando significativamente la precisión de los métodos empíricos y manuales tradicionales empleados actualmente.»
- **Variable independiente:** sistema web basado en redes neuronales (dimensiones: arquitectura y accesibilidad · precisión algorítmica).
- **Variable dependiente:** automatización de regímenes nutricionales y rutinas de entrenamiento (dimensiones: nutrición deportiva · cargas de entrenamiento).
- **Tipo y diseño:** investigación cuantitativa, prospectiva, transversal, descriptiva y explicativa; diseño experimental (se compara la salida de la red con las fórmulas metabólicas validadas sobre los mismos perfiles). Métodos científico e inductivo.
- **Comprobación (cuatro componentes):** automatiza → 0.36 s · precisa → 0.11 % de error medio · personalizada → 8 variables + lesiones + condiciones · supera a los empíricos → 0.12 % frente a 17.31 %–29.74 %, p < 0.001. **Decisión: la hipótesis se acepta** (con los límites de la diapositiva 22).

**Recursos:** `figuras_tesis/fig62_…` (precisión frente a métodos empíricos).

**Notas del expositor:** descomponer la hipótesis en cuatro partes es lo que permite decir «se acepta» con criterios y no con impresiones.

---

### Diapositiva 6 — La muestra · [5]

**Mensaje central:** la muestra se calculó con una fórmula estadística, no por conveniencia.

**Contenido:**
- **Población:** 300 usuarios concurrentes de centros de acondicionamiento físico de El Progreso (población económicamente activa, hombres y mujeres).
- **Muestra: 169 usuarios.** Muestreo probabilístico aleatorio simple; nivel de confianza 95 %, margen de error 5 %, probabilidad 0.5.
- Fórmula: n = (N · Z² · σ²) / ((N − 1) · e² + Z² · σ²) = 288.12 / 1.7079 ≈ **169**.
- **Instrumento:** cuestionario digital de 18 reactivos en tres secciones (datos generales · hábitos de entrenamiento y nutrición · acceso a la tecnología y disposición de uso).
- **Perfil de los encuestados:** 59.2 % hombres y 39.1 % mujeres; 89.9 % menores de 41 años; 72.2 % usa principalmente el teléfono inteligente.
- **Sede:** gimnasio Fama’s Fitness Club (zona urbana de El Progreso), que también será sede de las pruebas con usuarios.

**Recursos:** `figuras_tesis/fig01_…` (mapa del gimnasio), `fig02_…`, `fig03_…`.

**Notas del expositor:** aclarar que la encuesta midió hábitos y disposición, no medidas corporales; por eso la validación del modelo usó perfiles sintéticos (se declara en la diapositiva 22).

---

### Diapositiva 7 — Lo que dijo la muestra y cómo moldeó el sistema · [5]

**Mensaje central:** cada hallazgo de la encuesta se tradujo en una decisión de diseño.

**Contenido (hallazgo → decisión):**
- 72.2 % usa teléfono → interfaz pensada primero para pantalla pequeña, controles amplios y formularios en pasos cortos; instalable como aplicación.
- 60.3 % sabe poco de calorías → el usuario aporta datos simples y el sistema hace todo el cálculo; cada recomendación trae una explicación breve.
- 40.8 % quiere bajar de peso y 29.0 % ganar músculo → el objetivo es una variable obligatoria del modelo (déficit o superávit controlado).
- 46.7 % entrena de 3 a 4 días → la frecuencia semanal es dato de entrada y la rutina tiene exactamente esas sesiones.
- 76.3 % no puede pagar Q400 o más → el sistema es gratuito para el usuario.
- 81.7 % dispuesto a usarlo → demanda real; la aceptación es igual en hombres (82.0 %) y mujeres (81.8 %).
- 40.8 % pidió lista de compras y 69.8 % recordatorios → la lista de compras con costo se construyó; los recordatorios quedan como trabajo futuro.
- Los mayores de 40 años perciben más dificultad → tipografía legible, formularios secuenciales y ayuda contextual como requisito de accesibilidad.

**Recursos:** `figuras_tesis/fig13_…`, `fig15_…`, `fig16_…`, `fig12_…`.

**Notas del expositor:** esta diapositiva conecta la investigación de campo con el producto: nada del diseño es arbitrario.

---

### Diapositiva 8 — El proyecto: qué es y cómo funciona · [6]

**Mensaje central:** una plataforma web gratuita que calcula y actualiza sola el plan de alimentación y de entrenamiento de cada persona.

**Contenido:**
- **Visión:** para las personas que asisten a centros de acondicionamiento físico del municipio y no pueden costear asesoría profesional, una plataforma web gratuita que calcula y actualiza automáticamente sus planes de salud física, fundamentando cada recomendación en fórmulas metabólicas validadas y en los alimentos y el equipamiento realmente disponibles en el municipio.
- **Cómo funciona (ciclo de cinco pasos):**
  1. La persona se registra, sin costo.
  2. Captura su perfil (peso, estatura, edad, sexo, actividad, objetivo, experiencia, días por semana, lesiones y condiciones).
  3. La red neuronal calcula energía, macronutrientes y volumen de entrenamiento; el sistema arma el menú con alimentos del catálogo local y la rutina semanal.
  4. La persona entrena y registra su peso y sus sesiones cada semana.
  5. El sistema compara el ritmo real con el esperado y **reajusta el plan solo cuando los datos lo justifican**.
- **Dos tipos de usuario:** deportista (sus propios datos) y administrador (catálogos y cuentas; nunca ve datos biométricos).
- **Alcances y límites:** apoyo al acondicionamiento físico y la nutrición deportiva estándar; **no emite diagnósticos ni trata patologías crónicas severas**; depende de la veracidad de los datos ingresados y de conexión a internet; geográficamente limitado a El Progreso.
- **Metodología:** Scrum, iterativa e incremental (11 historias de usuario, 4 épicas).

**Recursos:** `figuras_tesis/fig54_…` (proceso sistematizado), `fig31_…` (flujo de generación y reajuste), `fig29_…` (contexto), `capturas/04_panel_hoy.png`.

**Notas del expositor:** contrastar `fig53_…` (proceso actual: pagar una consulta, recibir un plan impreso, no poder reajustarlo) con `fig54_…` (registrarse, recibir el plan en segundos y que se corrija solo).

---

### Diapositiva 9 — Arquitectura del sistema · [6]

**Mensaje central:** tres capas independientes que se comunican por contratos explícitos.

**Contenido:**
- **Presentación** (navegador del usuario): interfaz en React; no contiene reglas de negocio.
- **Lógica y servicios:** API REST en FastAPI (Python); reglas del dominio, motor neuronal y validaciones; 11 enrutadores.
- **Persistencia:** PostgreSQL 16 (15 tablas) y el archivo del modelo entrenado.
- Comunicación: JSON sobre HTTPS. El cliente nunca habla directamente con la base de datos.
- Patrón Modelo-Vista-Controlador; el motor neuronal se invoca a través de un motor de cálculo, de modo que puede sustituirse por las fórmulas de referencia si el modelo falla (el usuario siempre recibe un plan válido).
- Nueve componentes: interfaz, control de acceso, perfil biométrico, motor neuronal, generador de planes, catálogos, seguimiento y reajuste, bitácora de entrenamiento, senda y recompensas.

**Recursos:** `figuras_tesis/fig34_…` (tres capas), `fig36_…` (arquitectura técnica), `fig37_…` (componentes y paquetes), `fig41_…` / `fig42_…` / `fig43_…` (datos), `fig46_…` (mapa de navegación), `fig51_…` (secuencia de generación del plan).

**Notas del expositor:** la separación en capas permitió probar el motor sin levantar la base de datos; por eso las 658 pruebas corren en minutos.

---

### Diapositiva 10 — Módulo 1: Autenticación y seguridad · [7]

**Mensaje central:** acceso seguro y datos biométricos protegidos.

**Contenido:**
- Registro e inicio de sesión con correo y contraseña (mínimo ocho caracteres, con letras y números).
- Contraseñas almacenadas cifradas; sesión con vencimiento a los 30 minutos de inactividad y aviso dos minutos antes.
- Bloqueo de 15 minutos tras ocho intentos fallidos en cinco minutos.
- Control de acceso por roles (deportista y administrador); los permisos se comprueban en el servidor, no solo en la interfaz.
- Regla RN-06: el administrador no puede ver datos biométricos de nadie; solo cifras agregadas y anónimas.
- Pruebas: 47 casos aprobados.

**Recursos:** `capturas/01_acceso.png`, `capturas/02_registro.png`, `capturas/23_admin_cuentas.png`.

**Notas del expositor:** mostrar que el administrador gestiona roles y estado de cuentas, pero el sistema le impide desactivar su propia cuenta o dejar al sistema sin administrador.

---

### Diapositiva 11 — Módulo 2: Perfil biométrico · [7]

**Mensaje central:** ocho datos esenciales, capturados en cuatro pasos cortos, con el historial conservado.

**Contenido:**
- Formulario en **4 pasos**: (1) medidas: peso, estatura, edad, sexo; (2) actividad y objetivo; (3) experiencia y días de entrenamiento; (4) salud: lesiones y condiciones médicas.
- Validación de rangos en el servidor (peso 30–250 kg, estatura 120–220 cm, edad desde 18 años). Índice de masa corporal calculado al instante, como referencia y no como diagnóstico.
- **Cada actualización se guarda como una medición nueva**; las anteriores no se borran (historial).
- **Salvaguardas de salud:** una lesión (hombro, codo o muñeca, espalda baja, rodilla, tobillo) hace que la rutina omita los ejercicios que cargan esa zona; una condición médica severa hace que el sistema no genere el plan y remita a un profesional.
- Respuesta a la pregunta de investigación 2: los datos esenciales son ocho, más lesiones y condiciones que restringen el plan.
- Pruebas: 68 casos aprobados.

**Recursos:** `capturas/05_medidas_paso1_cuerpo.png`, `05_medidas_paso2_actividad.png`, `05_medidas_paso3_entrenamiento.png`, `05_medidas_paso4_salud.png`, `capturas/14_historial_medidas.png`, `capturas/21_condicion_medica_plan.png`.

**Notas del expositor:** la captura `21_…` demuestra una decisión ética del diseño: ante una diabetes declarada, el sistema prefiere no calcular.

---

### Diapositiva 12 — Módulo 3: Motor neuronal y plan nutricional · [7]

**Mensaje central:** una red neuronal que calcula en una sola pasada la energía, los macronutrientes y el volumen de entrenamiento.

**Contenido:**
- **Red:** 8 entradas → capas de 128, 128 y 64 neuronas → 5 salidas (energía, proteína, carbohidrato, grasa y series semanales por grupo muscular). Entrenada con 32,000 perfiles y validada con 8,000.
- **Salvaguardas clínicas** sobre la salida: déficit calórico hasta 20 %, superávit hasta 15 %, proteína entre 1.6 y 2.2 g por kg, aviso de consulta profesional en todo plan.
- **Transparencia en pantalla:** cada plan declara su comprobación frente a Mifflin-St Jeor y Harris-Benedict y explica los ajustes que hizo y por qué.
- **Precisión:** error medio de 2.6 kcal; margen medio de 0.11 % frente a las fórmulas; 100 % de los perfiles por debajo del 5 %.
- **Frente a los métodos empíricos:** 0.12 % de error contra 17.31 %–29.74 % (419 a 773 kcal diarias de error contra 2.5 kcal); la red es más precisa en más del 99.5 % de los perfiles (Wilcoxon, p < 0.001).
- **Rendimiento:** plan en 0.36 s; 2.70 s en el percentil 95 con 50 usuarios simultáneos.
- Pruebas del motor: 296 casos aprobados.

**Recursos:** `capturas/06_plan_nutricional.png`, `figuras_tesis/fig23_…` (estructura de una red multicapa), `figuras_tesis/fig62_…`, `figuras_tesis/fig79_…`.

**Notas del expositor:** responder aquí la pregunta de investigación 1. Explicar que la captura muestra a una usuaria ficticia y que la red es la misma para todas las personas.

---

### Diapositiva 13 — Módulo 3: Rutina de entrenamiento · [7]

**Mensaje central:** la rutina se arma sola, respeta la recuperación y evoluciona con lo que la persona levanta.

**Contenido:**
- Rutina semanal con **tantas sesiones como días declarados** (de 1 a 7); ningún grupo muscular se entrena en días consecutivos.
- Cada ejercicio indica series, repeticiones y repeticiones en reserva (cuántas podría hacer aún antes del fallo).
- Volumen e intensidad según el nivel: el principiante recibe menos volumen y ningún ejercicio de nivel superior.
- **Sobrecarga progresiva (RN-04):** el sistema sugiere la carga de la sesión siguiente a partir de lo registrado, sin subir más de 10 % entre microciclos.
- **Sesión en curso:** modo de enfoque sin barra de navegación, repeticiones y peso por serie, cronómetro de descanso con vibración opcional.
- **Lesiones:** los ejercicios que cargan la zona lesionada se omiten y la pantalla lo explica.
- Pruebas de rutina y progresión incluidas en los 296 casos del motor.

**Recursos:** `capturas/09_rutina_semanal.png`, `capturas/10_sesion_en_curso.png`, `capturas/10_sesion_series_marcadas.png`, `capturas/20_rutina_con_lesion.png`, `capturas/11_marcas_de_carga.png`.

**Notas del expositor:** la pantalla de sesión en curso indica que el registro se guarda en el teléfono mientras la persona entrena.

---

### Diapositiva 14 — Módulo 4: Catálogo de alimentos y ejercicios · [7]

**Mensaje central:** los planes son viables porque se construyen solo con lo que existe en el municipio.

**Contenido:**
- **Catálogo local:** 36 alimentos (con aporte nutricional, costo en quetzales y medida casera) y 25 ejercicios (con grupo muscular, nivel y equipamiento).
- **Menú del día** en cinco tiempos de comida, en gramos y en medidas caseras (taza, pieza, puño); el menú queda a pocos puntos porcentuales de lo que el plan pide.
- **Sustitutos:** si no se consigue un alimento, el sistema propone uno de aporte equivalente que sí está en el catálogo.
- **Lista de compras** semanal por categoría, con costo estimado y casillas para marcar lo comprado.
- **Administración (rol administrador):** agregar, editar y dar de baja alimentos y ejercicios; la baja retira el elemento de los planes nuevos sin borrarlo de los ya generados.
- Pendiente declarado: confirmar el catálogo con el levantamiento de campo en mercados y en el gimnasio.
- Pruebas: 102 casos aprobados.

**Recursos:** `capturas/07_menu_diario.png`, `capturas/08_lista_compras.png`, `capturas/22_admin_catalogos.png`.

**Notas del expositor:** la lista de compras fue la segunda función más pedida en la encuesta (40.8 %).

---

### Diapositiva 15 — Módulo 5: Seguimiento y adaptabilidad · [7]

**Mensaje central:** el sistema cierra el ciclo: cada avance semanal puede producir un plan nuevo.

**Contenido:**
- **Registro semanal en una sola pantalla:** peso, cumplimiento del plan de comidas, sesiones completadas y cintura (opcional).
- **Reajuste automático condicionado:** el plan solo se recalcula cuando el cambio de peso es apreciable y la adherencia es suficiente; el sistema explica siempre qué hizo y por qué. Los planes anteriores se conservan en el historial.
- **Evolución:** gráficas de peso, sesiones por semana, cumplimiento y cintura.
- **Bitácora y marcas:** cada serie registrada alimenta la progresión de carga y las marcas personales.
- **Senda:** 10 niveles, 18 insignias y puntos que reconocen la constancia (semana completa, balanza fiel, plan al día, descanso respetado).
- Respuesta a la pregunta de investigación 3: la plataforma convierte cada avance en una respuesta; el efecto sobre la constancia real se medirá con el grupo piloto.
- Pruebas: 86 casos aprobados.

**Recursos:** `capturas/12_avance_registro_peso.png`, `capturas/13_evolucion.png`, `capturas/11_bitacora.png`, `capturas/15_senda_nivel.png`, `capturas/15_senda_insignias.png`.

**Notas del expositor:** en los datos de demostración (seis semanas de seguimiento simuladas), el sistema reajustó el plan en cuatro semanas; en las dos semanas con variación pequeña de peso lo dejó igual y lo explicó («variación dentro de la fluctuación normal»).

---

### Diapositiva 16 — Informes

**Mensaje central:** la información sale del sistema en el formato que la persona necesite.

**Contenido:**
- **8 informes:** 4 personales (evolución del progreso, plan nutricional vigente, historial de medidas, bitácora de entrenamiento) y 4 de administración (indicadores de uso, cuentas registradas, catálogo de alimentos, catálogo de ejercicios).
- **5 formas de obtenerlos:** en pantalla, Excel, CSV, PDF e impresión. Las cinco parten del mismo informe: la cifra en pantalla es exactamente la del archivo.
- El informe de indicadores de uso solo contiene conteos y promedios; ningún dato individual (regla RN-06).
- Uso previsto: llevar el informe de evolución en PDF a la consulta con un profesional de la salud.
- Pruebas: 27 casos aprobados.

**Recursos:** `capturas/16_informes.png`, `capturas/24_admin_informes.png`.

**Notas del expositor:** frente al registro en papel, ningún dato se pierde y todo puede exportarse.

---

### Diapositiva 17 — Herramientas utilizadas · [8]

**Mensaje central:** pila tecnológica gratuita, madura y bien documentada.

**Contenido (capa → tecnología → función):**
| Capa | Tecnología | Función |
|---|---|---|
| Presentación | React 19, HTML, CSS con variables de diseño, aplicación web progresiva | Interfaz adaptable e instalable |
| Lógica y servicios | Python 3.12, FastAPI, Uvicorn, API REST con JSON | Exponer servicios y coordinar peticiones |
| Inteligencia artificial | TensorFlow y Keras | Entrenar y ejecutar la red neuronal |
| Persistencia | PostgreSQL 16, Supabase Studio | Almacenar perfiles, catálogos y planes |
| Pruebas | pytest (658 casos), Postman, prueba de carga con 50 usuarios | Verificar cada criterio de aceptación |
| Informes | openpyxl (Excel), fpdf2 (PDF) | Exportar los informes |
| Apoyo al desarrollo | Visual Studio Code, Git y GitHub, Node.js, Docker | Editar, versionar, ejecutar y empaquetar |
| Nube | Render (sitio estático + contenedor), Supabase (base de datos) | Despliegue en producción |

- Criterios de selección: pertinencia técnica, madurez, documentación oficial, compatibilidad entre componentes y **ausencia de costo de licenciamiento**.
- Metodología de desarrollo: Scrum.

**Recursos:** `figuras_tesis/fig36_…` (arquitectura técnica con las tecnologías de cada componente).

**Notas del expositor:** la decisión de no usar un marco de estilos de terceros eliminó cerca de 200 KB de descarga en conexiones móviles.

---

### Diapositiva 18 — Resultados de la validación (evidencia)

**Mensaje central:** el sistema cumple los criterios que se fijaron antes de construirlo.

**Contenido:**
| Criterio | Meta | Resultado |
|---|---|---|
| Margen frente a Mifflin-St Jeor y Harris-Benedict | menor al 5 % | **0.11 %** medio; 100 % de los perfiles bajo el 5 % |
| Superar a los métodos empíricos | diferencia significativa | 0.12 % contra 17.31 %–29.74 %; p < 0.001 |
| Tiempo de generación del plan | menos de 3 s | **0.36 s** (2.70 s en el percentil 95 con 50 usuarios) |
| Disponibilidad en la prueba de carga | sin fallos | 100 % de las peticiones atendidas |
| Pruebas funcionales automatizadas | todas aprobadas | **658 de 658** |
| Variables procesadas | — | 8 + lesiones + condiciones médicas |

- Evaluación independiente: 10,000 perfiles con una semilla distinta a la del entrenamiento; margen máximo de 3.69 %.
- Los 5 objetivos del producto tienen casos de prueba que los respaldan (CP-01 a CP-83).

**Recursos:** `figuras_tesis/fig62_…`, `figuras_tesis/fig56_…`, `figuras_tesis/fig79_…`, `figuras_tesis/fig80_…`.

**Notas del expositor:** terminar con la advertencia de honestidad: estos perfiles son sintéticos; la validación con datos reales es la siguiente etapa (diapositiva 22).

---

### Diapositiva 19 — Implementación en producción · [9]

**Mensaje central:** un plan de seis fases en ocho semanas, con una infraestructura reproducible y un dominio seguro.

**Contenido:**
- **Infraestructura (ya construida):** sitio estático en Render con la interfaz compilada · servicio web en contenedor Docker (Uvicorn + FastAPI + TensorFlow) · PostgreSQL 16 administrado por Supabase con copias de seguridad. Región Ohio (la más cercana a Guatemala).
- **Un solo dominio:** `https://rutinas-interfaz.onrender.com`; el sitio reenvía `/api/*` al servicio; HTTPS con certificado de renovación automática y redirección de HTTP a HTTPS.
- **Despliegue reproducible:** todo el entorno está declarado en el archivo `render.yaml` versionado; el sistema se niega a arrancar en producción con credenciales de ejemplo; verificación de salud en `/api/v1/estado` (si falla, se conserva la versión anterior).
- **Plan de implementación (8 semanas):**
  1. Preparación del entorno (S1)
  2. Despliegue técnico (S1–S2)
  3. Carga de datos maestros: catálogo levantado en mercados y equipamiento del gimnasio (S2–S3)
  4. Verificación en producción: pruebas funcionales y de carga, dominio, certificado y respaldo (S3)
  5. Capacitación y puesta en marcha con el personal y un grupo piloto del gimnasio (S4)
  6. Seguimiento y estabilización: monitoreo, respaldo semanal, reentrenamiento con datos reales (S5–S8)
- **Responsables:** estudiante investigador · administración del gimnasio · entrenador (valida rutinas) · grupo piloto · catedráticas asesoras.
- **Estado actual (decirlo con franqueza):** hecho — repositorio, servicios en Render, interfaz publicada, dominio y certificado. Pendiente — reactivar la base de datos de Supabase, pasar el servicio al plan de pago y ejecutar las fases 3 a 6 con el gimnasio.
- **Operación:** el usuario solo necesita un navegador (o instalar la aplicación en su teléfono); no requiere instalar programas.

**Recursos:** `figuras_tesis/fig36_…` (arquitectura y despliegue), `figuras_tesis/fig55_…` (fases en ocho semanas), `capturas/17_mas_ajustes.png` (opciones de la cuenta; la instalación en el teléfono se explica en el manual de usuario).

**Notas del expositor:** explicar por qué el plan gratuito de Render no sirve para la puesta en marcha (suspende el servicio a los 15 minutos sin tráfico) y por qué eso está registrado como paso explícito de la fase 2.

---

### Diapositiva 20 — Factibilidad e inversión

**Mensaje central:** el proyecto es factible técnica, económica y operativamente, y su costo de operación es mínimo.

**Contenido:**
- **Técnica:** tecnologías gratuitas y de código abierto; requisitos mínimos para el usuario (teléfono con 2 GB de memoria, navegador actualizado, 2 Mbps).
- **Económica:** valor total de los recursos Q26,695, de los cuales Q24,000 corresponden a las 480 horas del investigador; **desembolso monetario real: Q2,695**; **costo de operación: Q1,150 por semestre**.
- **Beneficio:** una asesoría cuesta Q4,800–Q9,600 al año por persona; con 100 usuarios en el primer año el ahorro agregado sería de Q480,000–Q960,000.
- **Operativa:** 81.7 % dispuesto a usar el sistema; 72.2 % con teléfono inteligente; el gimnasio manifestó su anuencia; la administración de catálogos no requiere personal adicional.
- **Metas del negocio:** 100 usuarios en el primer mes · 80 % de planes calificados como útiles · plan en menos de 3 s.

**Recursos:** ninguno obligatorio.

**Notas del expositor:** aclarar que el ahorro es una estimación de mercado y que la mano de obra se valoró solo por transparencia presupuestaria.

---

### Diapositiva 21 — Aporte del proyecto · [10]

**Mensaje central:** un aporte académico, técnico y social medible.

**Contenido:**
- **Técnico:** un modelo de red neuronal entrenado y validado que traduce variables antropométricas en requerimientos energéticos y cargas de entrenamiento con error medio de 0.11 %, y una plataforma web funcional, probada con 658 casos y lista para instalarse en el teléfono.
- **Local:** catálogos de alimentos y ejercicios adaptados al municipio (36 y 25), con costos en quetzales y medidas caseras; un conjunto de datos primarios (169 personas) sobre hábitos de entrenamiento, nutrición y adopción tecnológica que no existía y queda disponible para futuras investigaciones.
- **Social:** reduce la barrera económica (Q400–Q800 mensuales) y los riesgos de lesión y de descompensación por entrenar sin guía; beneficiarios directos: personas económicamente activas que asisten a centros de acondicionamiento físico; indirectos: los propietarios de los gimnasios (retención de clientes) y el sistema de salud local.
- **Académico:** un precedente metodológico de cómo la ingeniería en sistemas de información resuelve problemas de salud pública local, con la hipótesis sometida a una prueba estadística y los límites declarados.
- **Responsable:** un sistema que no diagnostica, que se niega a calcular ante una condición médica severa y que acompaña cada plan con su aviso profesional.

**Recursos:** `figuras_tesis/fig54_…` (proceso sistematizado), `capturas/04_panel_hoy.png`.

**Notas del expositor:** cerrar el bloque con la idea: el aporte no es solo una aplicación, es acercar la planificación profesional a quien hoy no puede pagarla.

---

### Diapositiva 22 — Límites y trabajo futuro

**Mensaje central:** qué demostró el trabajo, qué no, y cuál es el siguiente paso.

**Contenido:**
- **Lo que se demostró:** precisión del cálculo, tiempo de respuesta, seguridad y funcionamiento de cinco módulos con 658 pruebas.
- **Lo que no se demostró todavía:**
  - La validación usó perfiles sintéticos (la encuesta no recogió medidas biométricas) → validar con datos reales y compararlos con la valoración de un nutricionista o con una medición del gasto en reposo.
  - Los métodos empíricos se representaron con tres reglas de uso común.
  - La usabilidad (escala 1–5) y el efecto sobre la constancia real quedan pendientes del grupo piloto.
  - El catálogo debe confirmarse con visitas a mercados y al gimnasio.
- **Trabajo futuro (de la tesis):** estudio con grupo de control durante un mesociclo completo · actividad medida con relojes o pulseras (28.4 % lo considera útil) · recordatorios automáticos (69.8 % los pidió) · conversación con un especialista (42.6 %) · extender catálogo y validación a otros municipios de Jutiapa · reentrenar el modelo con datos reales con consentimiento informado.
- **Recomendaciones operativas:** contratar el plan de pago y repetir la prueba de carga contra el sistema publicado · reactivar y mantener activa la base de datos · registrar un dominio propio para el gimnasio · actualizar precios del catálogo cada trimestre · revisar las rutinas del grupo piloto con el entrenador.

**Recursos:** ninguno obligatorio.

**Notas del expositor:** declarar los límites antes de que los pregunten fortalece la credibilidad de la tesis.

---

### Diapositiva 23 — Conclusiones

**Mensaje central:** el objetivo general se cumplió y la hipótesis se aceptó, con límites declarados.

**Contenido:**
- Se diseñó y entrenó una red de tres capas ocultas (128, 128 y 64) que procesa 8 variables y entrega en una sola predicción energía, macronutrientes y volumen de entrenamiento, con error medio de 2.6 kcal.
- Se desarrolló una plataforma adaptable e instalable, con 36 alimentos y 25 ejercicios, cuyos menús y rutinas se construyen solo con el catálogo local.
- La validación frente a Mifflin-St Jeor y Harris-Benedict dio un margen medio de **0.11 %**, con el 100 % de los perfiles bajo el 5 %, y superó con significancia estadística a tres métodos empíricos.
- El cálculo quedó automatizado (0.36 s), las rutinas respetan volumen, intensidad y frecuencia, y el seguimiento reajusta el plan solo cuando los datos lo justifican.
- El acceso es gratuito, seguro y desde el teléfono; 658 de 658 pruebas aprobadas.
- **La hipótesis se acepta; el objetivo general se cumple.**

**Recursos:** ninguno obligatorio.

**Notas del expositor:** leer las conclusiones en el mismo orden que los objetivos.

---

### Diapositiva 24 — Cierre y preguntas

**Mensaje central:** agradecer, invitar a preguntas y, si hay conexión, mostrar el sistema.

**Contenido:**
- «Gracias»; nombre del estudiante y datos de contacto institucional que prefiera el estudiante.
- Dirección del sistema: https://rutinas-interfaz.onrender.com
- Invitación a preguntas.

**Recursos:** opcional `capturas/04_panel_hoy.png`.

**Notas del expositor:** si se va a hacer una demostración en vivo, **reactivar antes la base de datos de Supabase y probar el inicio de sesión**; si no está disponible, usar el apéndice y las capturas.

---

## 6. Apéndice (opcional, para preguntas del tribunal)

### A1 — El sistema en computadora
Mensaje: el mismo sistema se adapta de 320 a 1,920 px. **Recursos:** `capturas/19_escritorio_hoy.png`, `capturas/19_escritorio_evolucion.png`.

### A2 — Tema oscuro y accesibilidad
Contenido: tema claro y oscuro, áreas táctiles de al menos 44 px, funcionamiento de 320 a 1,920 px, formularios secuenciales y lenguaje sencillo (respuesta al hallazgo de los usuarios mayores de 40 años). **Recursos:** `capturas/18_tema_oscuro_hoy.png`, `capturas/17_mas_ajustes.png`.

### A3 — Datos y modelo entidad-relación
Contenido: 15 tablas; el historial de mediciones y de planes se conserva; el catálogo no se borra, se da de baja. **Recursos:** `figuras_tesis/fig41_…`, `fig42_…`, `fig43_…`.

### A4 — Casos de uso y secuencia de generación del plan
Contenido: actores deportista y administrador; recorrido de una petición de plan desde la interfaz hasta el motor y la base de datos. **Recursos:** `figuras_tesis/fig49_…`, `fig51_…`.

---

## 7. Preguntas probables del tribunal (con la respuesta respaldada)

| Pregunta | Respuesta con respaldo |
|---|---|
| ¿Por qué una red neuronal si ya existen las fórmulas? | Las fórmulas dan solo la tasa metabólica; la red entrega en una predicción energía, macronutrientes y volumen de entrenamiento según objetivo, experiencia y frecuencia. Además el sistema contrasta cada plan con las fórmulas y puede volver a ellas si el modelo falla. |
| ¿Con qué datos entrenó la red? | Con 32,000 perfiles sintéticos generados a partir de las fórmulas de referencia y validados con 8,000 y con 10,000 perfiles independientes. La encuesta no recogió medidas corporales; la validación con datos reales está prevista. |
| ¿Es seguro? | No diagnostica; limita el déficit a 20 % y el superávit a 15 %; se niega a generar plan ante una condición médica severa; omite ejercicios que cargan una zona lesionada; cada plan lleva aviso de consulta profesional. |
| ¿Cómo se protegen los datos? | Contraseñas cifradas, sesión con vencimiento, bloqueo por intentos fallidos, permisos en el servidor, HTTPS, y el administrador no puede ver datos biométricos individuales. |
| ¿Qué pasa si falla la red o la conexión? | Si falla el modelo, se calcula con las fórmulas de referencia. La sesión de entrenamiento se guarda en el teléfono mientras la persona entrena. |
| ¿Por qué el sistema no responde hoy en producción? | El proyecto gratuito de base de datos se encuentra suspendido; el código y la interfaz están publicados y, según la tesis, reactivarlo desde el panel del proveedor restablece el servicio sin modificar el código (apartados 6.1 y 8.2). |
| ¿Cuánto cuesta mantenerlo? | Q1,150 por semestre (alojamiento y dominio); desembolso real del proyecto Q2,695. |
| ¿Qué falta? | Validar con datos reales, medir usabilidad y constancia con el grupo piloto, completar el levantamiento del catálogo y ejecutar las fases 3 a 6 del plan de implementación. |
