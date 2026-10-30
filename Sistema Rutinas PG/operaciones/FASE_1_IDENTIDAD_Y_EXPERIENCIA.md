# Fase 1 · Identidad y experiencia de Senda

Fecha: 29 de octubre de 2026, horario de Guatemala.

**Estado: prototipo implementado y en revisión.** Se entregan tres bocetos de
símbolo, dos modos visuales complementarios y recorridos interactivos adaptables. Falta la
evaluación con 5–8 personas, la selección definitiva del símbolo y la revisión
en teléfono físico. No se declara cerrada la fase 1 ni se dan por resueltos los
pendientes técnicos y operativos de la [fase 0](FASE_0_LINEA_BASE.md).

## Cómo revisar la entrega

Desde `frontend`, ejecutar:

```powershell
npm run dev -- --host 127.0.0.1 --port 15173 --strictPort
```

Abrir <http://127.0.0.1:15173/prototipo/fase-1>. No requiere servidor de API ni
cuenta para probar los datos de muestra. El selector superior cambia el tema
claro u oscuro; «Identidad» permite elegir el símbolo; «Vista móvil» limita el lienzo a
390 px. Esta última es una vista previa, no una prueba en teléfono físico.

Los enlaces existentes conservan `direccion=tierra|pulso` para indicar el modo:
`tierra` es claro y `pulso` es oscuro. Sin ese parámetro, la muestra sigue el tema
guardado en el sistema; al abrir un enlace con modo explícito o usar el selector,
la elección se comparte con la aplicación y se recuerda en el dispositivo.
También se conservan los parámetros
`simbolo=camino|paso|cumbre`, `vista=movil`. Se pueden compartir dentro del entorno
que ejecute el cliente. Las preferencias de bienvenida y la finalización del
ejercicio viven en memoria y se borran al recargar. Las series sin finalizar se
reinician al salir de la pantalla, como indica la propia muestra.

| Pantalla | Ruta bajo `/prototipo/fase-1` | Qué se puede revisar |
|---|---|---|
| Portada | `/` | Propuesta de valor, ilustración y entrada al recorrido. |
| Identidad | `/identidad` | Símbolos, comparación visual, tamaños e icono conceptual. |
| Primer uso | `/primer-uso` | Tres pasos, selección con radio, volver y continuar. |
| Inicio | `/hoy` | Acción principal, comida, semana y próximo logro. |
| Sesión | `/sesion` | Ficha, tres series, descanso, omisión, finalización y reinicio. |
| Comida | `/comida` | Presentación editorial ilustrativa de una comida. |
| Avance | `/avance` | Resumen y cambio visible al finalizar el ejercicio. |

## Propuestas de identidad

El nombre **Senda** ya fue elegido por el autor. Los símbolos son dibujos
vectoriales propios definidos en `frontend/src/prototipo/MarcaSenda.jsx`.
Funcionan mediante un solo color y se muestran a 24, 32 y 48 px. No se utilizaron
imágenes de personas ni recursos de terceros para las ilustraciones nuevas.

| Símbolo | Intención | Ventaja propuesta | Riesgo por evaluar |
|---|---|---|---|
| Camino | Una S continua termina en un avance. | Vincula nombre y recorrido. | Reconocimiento de la S a 24 px. |
| Paso | Persona en movimiento. | Asociación directa con actividad. | Asociación excesiva con correr. |
| Cumbre | Horizonte y camino compacto. | Silueta para icono instalado. | Asociación con senderismo. |

Son hipótesis de diseño, no resultados de entrevistas. **La decisión vigente del
autor es conservar A · Tierra y camino como modo claro y B · Pulso y contraste
como modo oscuro.** Son dos modos de una misma identidad para la portada y todo
el sistema; esta decisión reemplaza la selección anterior de una sola dirección.
**Camino** sigue siendo una propuesta de símbolo pendiente de selección. La
evaluación de comprensión sigue pendiente. No se afirma disponibilidad comercial,
de dominio ni registro de marca.

| Elemento | Modo claro / A · Tierra y camino | Modo oscuro / B · Pulso y contraste |
|---|---|---|
| Fondo | Crema `#f6f3eb` | Carbón verde `#151e1b` |
| Texto principal | Bosque `#233d32` | Marfil `#f2f4eb` |
| Acción principal | Verde `#244b3b`, texto marfil | Lima `#c4ed95`, texto oscuro |
| Superficie secundaria | Salvia `#e6ebdf` | Verde oscuro `#26372f` |
| Logros | Ocre `#e8bd65`, texto oscuro | Ocre `#e8bd65`, texto oscuro |
| Hipótesis | Cercanía y convivencia entre alimentación y entrenamiento. | Mayor énfasis deportivo y foco en la acción. |

Tipografía: Geist y respaldo del sistema para interfaz y marca; Georgia para
el énfasis editorial de portada; cifras tabulares para series y cronómetro. Se
reutiliza la carga de fuentes existente. Las ilustraciones son SVG con colinas,
camino y formas orgánicas. No representan corrección de postura ni composición
nutricional. El símbolo tiene área libre propuesta de un cuarto de su ancho y
tamaño mínimo propuesto de 24 px; requieren validación perceptiva.

Movimiento: respuesta de botones de 160 ms; sin animación continua ni
reproducción automática. La preferencia `prefers-reduced-motion` elimina
transiciones y desplazamientos. La duración de transición de contenido de hasta
240 ms queda como regla de diseño para futuras pantallas, no como una animación
ya aplicada a todo el producto.

## Decisiones de experiencia y alcance técnico

a) La portada conecta propuesta, tres pasos y una entrada visible a la muestra.
El registro y acceso reales se identifican de forma explícita y llevan a las
rutas existentes. El recorrido ficticio no recoge correo, medidas ni salud.

b) El inicio presenta una acción principal y muestra alimentación, semana y
próximo logro. «Mi avance» nombra la sección del prototipo para distinguirla de
la marca Senda; no renombra todavía el módulo existente «Mi senda».

c) La sesión demuestra un ejercicio con tres series. El descanso usa una fecha
límite para calcular el tiempo restante y tiene una acción para omitirlo. Los
valores son ficticios. La ficha avisa que la demostración técnica revisada se
desarrollará en la fase 3; no se simula una biblioteca validada.

d) Se usan controles nativos, grupos de radio, etiquetas, estados de selección,
foco en el título al navegar y al cambiar de paso, avisos de confirmación y
alternativas textuales. Las comprobaciones realizadas no equivalen a certificar
conformidad de accesibilidad ni sustituyen una prueba con lector de pantalla.

e) La integración añade una entrada delimitada en `App.jsx`, carga el prototipo
bajo demanda y mantiene su composición dentro de `.fase1`. La fuente de color
común está en `frontend/src/estilos/paleta-senda.css`: los tokens de las pantallas
reales y los estilos de la muestra usan las mismas variables. El selector utiliza
el proveedor de preferencias existente; el interruptor «Tema oscuro» de «Más»
continúa funcionando. Los componentes de muestra no llaman a servicios de
negocio. No se modifican modelos, cálculo, autenticación, reglas de salud ni base
de datos. La renovación de la distribución de las pantallas reales sigue pendiente.

f) Se actualizan el color inicial de la PWA y el color de la barra del navegador
para que coincidan con los nuevos fondos. El favicon e iconos instalados se
conservan. Hay una aplicación conceptual del icono en la página de identidad.
Los PNG definitivos, el manual
de marca final y el cambio de identidad en toda la aplicación se preparan tras
seleccionar el símbolo. No hubo publicación ni cambios en servicios contratados.

## Verificación de esta entrega

a) `npm run build`: construcción correcta, incluyendo generación de service
worker y manifest. El prototipo genera archivos JS y CSS separados mediante
importación diferida. No se añadieron dependencias.

b) Revisión en el navegador integrado: portada, selección en los tres pasos,
reflejo de objetivo y disponibilidad en el inicio, consulta de ficha, marcado de
tres series, omisión de descanso, finalización y avance de 2/3 a 3/3.

c) Cambio de los tres símbolos y de las dos direcciones visuales; comprobación
de la vista previa móvil. Se conservaron capturas locales de escritorio y móvil
en `operaciones/evidencias/fase1/`, excluidas del control de versiones por la
regla de evidencias existente.

d) No se volvió a ejecutar la batería del servidor porque este incremento no
modifica sus archivos ni sus reglas. Las 667 pruebas de fase 0 son un resultado
anterior, no una medición nueva de este prototipo. Tampoco se midieron generación
del primer plan, concurrencia ni conexión móvil real con esta muestra.

e) Las siete rutas se comprobaron a 320 px sin desbordamiento horizontal y con
un título principal por pantalla. Se revisaron además la portada a 768 y 1440 px,
el inicio a 390 px y la dirección B en móvil. El acceso existente se abrió desde
la muestra y recuperó su título y formulario originales. Las combinaciones
principales de texto y botones tienen relaciones de contraste calculadas entre
5.77:1 y 15.34:1; esto no es una auditoría completa de todos los estados.

El registro de dimensiones y revisión de las rutas se conserva en
`operaciones/evidencias/fase1/revision-adaptable.json`. Las capturas y medidas de
ancho son evidencia de navegador; no prueban compatibilidad con un teléfono físico.

Tras la decisión de conservar ambos modos se comprobó además la continuidad
entre el selector de la muestra y el acceso real: claro con fondo `#f6f3eb` y
botón `#244b3b`; oscuro con fondo `#151e1b` y botón `#c4ed95`. En ambos casos se
verificó persistencia tras recargar y coincidencia de `theme-color`. La evidencia
está en `evidencias/fase1/revision-temas-compartidos.json` y en las capturas
`acceso-modo-claro.jpg` y `acceso-modo-oscuro.jpg`. Esto comprueba colores y
preferencia compartida; no acredita una revisión visual de cada pantalla privada.

## Evaluación pendiente y condición de cierre

Utilizar el [guion de evaluación](FASE_1_GUION_EVALUACION.md) con 5–8 personas
adultas del público inicial, combinando principiantes y usuarios con experiencia.
Registrar comprensión, finalización sin ayuda, obstáculos, preferencia y recuerdo.
No hay participantes ni resultados de campo registrados en esta entrega.

La fase puede cerrarse después de evaluar ambos modos, documentar la
selección del símbolo, atender problemas que impidan las tareas, revisar en
teléfono físico y acordar los activos finales de marca. La identidad se aplica
a portada, acceso, registro, panel, entrenamiento, alimentación, progreso y
administración, conservando el mismo símbolo y jerarquía en ambos modos.
El sitio público
integrado, la recuperación de acceso y el perfil real corresponden a la fase 2.
Los hallazgos de rendimiento y despliegue de fase 0 siguen abiertos.

Para la tesis: describir este incremento como **prototipo de identidad y
experiencia**, separado de las interfaces productivas y de sus resultados
históricos. No reemplazar capturas del producto por esta muestra como si ya
estuviera desplegada; no atribuir mejoras de adherencia o eficacia sin evidencia.
