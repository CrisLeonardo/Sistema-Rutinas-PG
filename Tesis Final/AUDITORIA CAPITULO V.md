# Capítulo V – Diseño del Sistema · construcción y auditoría

**Archivo entregable:** `Leonardo Zepeda - Proyecto de Graduacion II - Entrega 2.docx`
**Vista previa:** `Leonardo Zepeda - Proyecto de Graduacion II - Entrega 2.pdf`
**Base:** `Leonardo Zepeda - Proyecto de Graduacion II - Entrega 1 (corregida).docx` (intacto, no se modificó)
**Guion seguido:** `PG2 Diseño del Sistema.pdf`, esquema de la **metodología Scrum** (diapositiva 7), que es la metodología declarada en el apartado 1.12.3 y usada en el Capítulo IV.

---

## 1. Lo que pedía el PDF y lo que quedó escrito

Los **38 apartados** del guion están presentes, en el mismo orden y en el mismo nivel de encabezado. Ninguno falta.

| Guion del PDF | Apartado escrito | Contenido |
|---|---|---|
| 5.1 Arquitectura del sistema | 5.1 Arquitectura del Sistema | Párrafo de entrada |
| 5.1.1 Vista General de la arquitectura | 5.1.1 Vista general de la arquitectura | Figura 29 (tres capas) |
| 5.1.2 Componentes principales y sus interacciones | ídem | Tabla 52 + Figura 30 |
| 5.2 Diseño de arquitectura técnica | 5.2 Diseño de la Arquitectura Técnica | Párrafo de entrada |
| 5.2.1 Diagrama de arquitectura | ídem | Figura 31 (despliegue real en Render y Supabase) |
| 5.2.2 Patrones de diseño utilizados | ídem | Tabla 53 (7 patrones) |
| 5.2.3 Consideraciones de integración | ídem | Tabla 54 (7 consideraciones) |
| 5.3 Diseño de componentes y módulos | 5.3 Diseño de Componentes y Módulos | Párrafo de entrada |
| 5.3.1 Identificación de componentes | ídem | Figura 32 (paquetes) |
| 5.3.2 Descripción de módulos | ídem | Tabla 55 (18 módulos con trazabilidad a HU) |
| 5.3.3 Diseño de interfaces de componentes | ídem | Párrafo de entrada |
| 5.3.3.1 Interfaces internas | ídem | Tabla 56 (9 interfaces) |
| 5.3.3.2 Interfaces externas | ídem | Tabla 57 (37 rutas de la API) |
| 5.3.4 Diagrama de clases | ídem | Figura 33 |
| 5.4 Diseño de Base de datos | 5.4 Diseño de la Base de Datos | Párrafo de entrada |
| 5.4.1 Modelo de datos conceptual | ídem | Figura 34 + Tabla 58 |
| 5.4.2 Diagrama de la base de datos | ídem | Figuras 35 y 36 (entidad-relación en dos partes) |
| 5.4.3 Diccionario de datos | ídem | **13 tablas, una por entidad** (Tablas 59 a 71) |
| 5.5 Diseño de la interfaz de usuarios (UI) | 5.5 Diseño de la Interfaz de Usuarios | Párrafo de entrada |
| 5.5.1 Principios de diseño de UI/UX | 5.5.1 Principios de diseño de la interfaz y de la experiencia de usuario | Tabla 72 |
| 5.5.2 Prototipos de interfaz | ídem | Figuras 37 y 38 (7 pantallas) |
| 5.5.3 Diseño de navegación | ídem | Figura 39 (mapa completo) |
| 5.5.4 Directrices de accesibilidad y usabilidad | ídem | Tabla 73 (WCAG 2.2 nivel AA) |
| 5.6 Diseño de la seguridad | 5.6 Diseño de la Seguridad | Párrafo de entrada |
| 5.6.1 Autenticación y autorización | ídem | Tabla 74 (matriz de permisos) |
| 5.6.2 Gestión de Sesiones | 5.6.2 Gestión de sesiones | Tabla 75 (9 parámetros) |
| 5.6.3 Cifrado de datos | ídem | Tabla 76 (10 mecanismos) |
| 5.7 Diagramas UML | ídem | Párrafo de entrada |
| 5.7.1 Diagramas de casos de uso | ídem | Figura 40 + Tabla 77 (caso de uso ampliado) |
| 5.7.2 Diagrama de actividades | ídem | Figura 41 (con calles) |
| 5.7.3 Diagrama de secuencia | ídem | Figura 42 |
| 5.8 Revisión y mejora continua del diseño | 5.8 Revisión y Mejora Continua del Diseño | Párrafo de entrada |
| 5.8.1 Revisión de Diseño en Reuniones de Sprint | 5.8.1 Revisión del diseño en las reuniones de la iteración o sprint | Figura 43 + Tabla 78 |
| 5.8.2 Retroalimentación del diseño | ídem | Tabla 79 (5 fuentes) |
| 5.8.3 Adaptación y mejora continua | ídem | Tabla 80 (9 decisiones rectificadas) |
| 5.9 Procesos de negocio | 5.9 Procesos de Negocio | Concepto, como pide la diapositiva 8 |
| 5.9.1 Proceso actual | ídem | Figura 44 + explicación debajo |
| 5.9.2 Proceso sistematizado | ídem | Figura 45 + explicación debajo + Tabla 81 comparativa |

Los 13 subapartados numerados del diccionario de datos (5.4.3.1 a 5.4.3.13) siguen el mismo formato que la diapositiva 12 del PDF muestra como ejemplo: encabezado por entidad, párrafo que la describe y tabla con **Campo, Tipo, Nulo, Clave, Valor por defecto, Extra y Descripción**.

---

## 2. Cifras del entregable

| | Antes (Entrega 1 corregida) | Ahora (Entrega 2) |
|---|---|---|
| Capítulos | 4 | **5** |
| Páginas del documento | — | **188** |
| Páginas del Capítulo V | — | **50** (123 a 172; el mínimo exigido es 15) |
| Palabras | ~34 500 | **49 425** |
| Tablas | 51 | **81** (30 nuevas) |
| Figuras | 34 | **51** (17 nuevas) |

---

## 3. Los errores de las entregas anteriores, revisados uno por uno

| Observación que costó punteo antes | Cómo se atendió en el Capítulo V | Verificado |
|---|---|---|
| «Agregue una explicación» en cada apartado | Los **52 encabezados** del capítulo llevan párrafo explicativo antes de cualquier subapartado, tabla o figura | 0 encabezados sin explicación |
| Pies de tabla y figura que quedaban solos al final de una página | Todos los rótulos llevan `keepNext` | **0 rótulos huérfanos** |
| «Nota. Elaboración propia» en lugar de «Fuente:» | Las 47 tablas y figuras nuevas nacen con **«Fuente: …»** | 0 rótulos sin fuente |
| Tablas largas sin repetir el encabezado | Fila de encabezado marcada como repetible y filas sin partir | Verificado en las tablas de 37 y de 18 filas |
| Índices desactualizados | Índice general, Índice de Tablas e Índice de Figuras **recalculados en Word** | 231 / 81 / 51 entradas |
| Numeración de tablas y figuras | Campos `SEQ` automáticos, no números escritos a mano | Tablas 52–81 y Figuras 29–45, correlativas |
| «No posee diagramas» | **17 figuras** en el capítulo, que es donde el PDF del curso dice que van | — |

---

## 4. Correcciones de coherencia en capítulos anteriores

El Capítulo V describe el sistema tal como está construido hoy. Eso obligó a corregir tres puntos del Capítulo III que ya no correspondían al código, porque un documento que se contradice a sí mismo pierde punteo:

| Lugar | Antes | Ahora |
|---|---|---|
| 3.3.4 | «Marco de presentación Bootstrap» | **«Sistema de Tokens de Diseño»**, con las dos razones de la decisión: control del contraste y peso de la descarga |
| Tabla 6, fila 4 | Bootstrap | Tokens de diseño |
| Tabla 7, fila «Presentación» | «…y Bootstrap» | «…y tokens de diseño» |

Motivo: el rediseño de la interfaz retiró Bootstrap del proyecto. No queda ninguna mención en el documento (tampoco de MySQL ni de Workbench, retirados en la entrega anterior).

También se actualizó la **Introducción**, que anunciaba «cuatro capítulos»: ahora anuncia cinco y describe el contenido del Capítulo V.

Y se agregaron **dos referencias** que el capítulo cita, en orden alfabético y con formato APA 7:

- Consorcio World Wide Web. (2023). *Web content accessibility guidelines (WCAG) 2.2*.
- Nielsen, J. (2024). *10 usability heuristics for user interface design*.

---

## 5. Todo el contenido está verificado contra el código

No hay nada inventado. Cada dato del capítulo se tomó del repositorio:

- Las **37 rutas** de la Tabla 57 se extrajeron de `backend/app/api/v1/`, con su verbo, su ruta y su nivel de acceso real.
- Las **13 entidades** del diccionario se extrajeron de `backend/app/modelos/`, con sus tipos, nulabilidad, valores por defecto, claves e índices reales.
- Los **18 módulos** de la Tabla 55 corresponden a los paquetes que existen en el repositorio.
- Los parámetros de sesión (30 minutos, revisión cada 30 s, aviso 2 minutos antes) salen de `nucleo/configuracion.py` y `frontend/src/contexto/ContextoSesion.jsx`.
- El límite de intentos (8 en 5 minutos, bloqueo de 15) sale de `nucleo/limitador.py`.
- Los encabezados de seguridad salen de `backend/app/main.py`, `render.yaml` y `frontend/nginx.conf`.
- Las **9 rectificaciones de diseño** de la Tabla 80 corresponden a cambios que están en el historial de Git del proyecto.

---

## 6. Revisión de ortografía y redacción

Se releyó el capítulo completo —prosa y celdas de tabla— y se pasaron comprobaciones automáticas de puntuación y el corrector de Word.

**Comprobaciones mecánicas: todas en cero.** Espacios dobles, espacio antes de coma o punto, coma sin espacio después, comillas rectas, palabras repetidas, paréntesis, comillas latinas y rayas sin cerrar.

**Homófonos y tildes verificados uno por uno en su contexto:** *sino* / *si no*, *aun* / *aún*, *continua* / *continúa*, *porque* / *por qué*, *solo*, *mas* / *más*. Todos correctos.

**27 correcciones de redacción aplicadas**, agrupadas por motivo:

| Motivo | Antes | Ahora |
|---|---|---|
| Calco del inglés | «sin romper a los clientes ya instalados» | «sin inutilizar las aplicaciones ya instaladas» |
| Calco del inglés | «verificar en tiempo de análisis» | «comprobar, antes de ejecutar el programa» |
| Anglicismo innecesario | «los guardarraíles clínicos» (5 veces y 2 figuras) | «las salvaguardas clínicas» |
| Término confuso | «el repartidor de sesión» (3 veces y 1 figura) | «el distribuidor de conexiones» |
| Término confuso | «bloquean la llave durante quince minutos» | «bloquean ese origen durante quince minutos» |
| Coma ante *sino* adversativo | «no se elige por preferencia sino por…» (5 casos) | «no se elige por preferencia, sino por…» |
| Concordancia | «todo alimento y todo ejercicio propuesto existe» | «todos los alimentos y todos los ejercicios propuestos existen» |
| Mayúscula indebida | «La Tabla siguiente presenta» | «La tabla siguiente presenta» |
| Régimen preposicional | «se omiten de este diagrama» | «se omiten en este diagrama» |
| Régimen preposicional | «se ejecutan antes que el controlador» | «se ejecutan antes del controlador» |
| Coma mal colocada | «los tres niveles, sobre el gestor PostgreSQL 16 justificado» | «los tres niveles sobre el gestor PostgreSQL 16, justificado» |
| Antecedente ambiguo | «Quien no puede pagarla busca» | «Quien no puede costear esa asesoría busca» |
| Redundancia | «sustituye en su lugar» | «pone en su lugar» |
| Redundancia | «datos que el negocio sí necesita» | «datos que sí necesita» |
| Registro coloquial | «quede a un toque» | «quede a un solo toque de distancia» |
| Registro coloquial | «entidades que se tocan» | «entidades que se modifican» |
| Elipsis confusa | «devuelve al acceso» | «devuelve a la pantalla de acceso» |
| Orden confuso | «la consulta el proveedor antes de publicar» | «el proveedor la consulta antes de publicar» |
| Concordancia | «alimentos o ejercicios bastantes» | «suficientes alimentos o ejercicios» |
| Coherencia con el Cap. IV | «jamás la contraseña en claro» | «jamás la contraseña en texto plano» |
| Voz poco natural | «Es administrada exclusivamente por el rol» (2 veces) | «Su administración está reservada al rol» |
| Término poco asentado | «el mapeador objeto-relacional» (2 veces) | «la herramienta de mapeo objeto-relacional» |
| Expresión oscura | «ciclo de dependencia en el sentido del código» | «ciclo de dependencias en el plano del código» |

**Corrector de Word.** Las marcas en el Capítulo V bajaron de **92 a 10**. Las 92 iniciales eran nombres de campo, de módulo y de tipo de dato (`contrasena_cifrada`, `motor.red_neuronal`, `varchar`, `smallint`…), que el corrector señalaba por no llevar tilde aunque son código. Esos textos se marcaron como «no revisar ortografía», de modo que el documento ya no se abre con el diccionario de datos lleno de subrayados rojos.

Las **10 marcas restantes son correctas y deben quedarse**: los apellidos de la bibliografía (Elmasri, Fowler, Jeor, Mifflin-St, Navathe, Schwaber, Silberschatz, World) y dos nombres de producto (bcrypt, React). Aparecen igual en los capítulos anteriores.

---

## 7. Qué debe hacer usted antes de entregar

1. **Abrir el .docx en Word.** Los índices ya vienen calculados, pero si Word pregunta si desea actualizar los campos, acepte.
2. **Revisar la numeración de páginas del pie**, que no se tocó.
3. Si el asesor pide el capítulo suelto, imprima el rango de **páginas 123 a 172**.
