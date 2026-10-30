# Fase 3: biblioteca y piloto visual

Implementación local del 30 de octubre de 2026. Pendiente de revisión del autor,
validación técnica, equipo de campo y evaluación de comprensión. No se publicó
en producción. El autor se ofreció a revisar las fichas y pidió fundamentarlas
en fuentes para reducir correcciones evitables.

## Entrega

- `/entrenar/biblioteca`: catálogo real de la API, con búsqueda sin distinción de
  tildes, filtros por grupo y equipo, y filtro de fichas visuales. Oculta las bajas
  del listado. Cada detalle usa el ID que devuelve el servidor, sin IDs supuestos.
- `/entrenar/biblioteca/:ejercicioId`: descripción del catálogo y, si existe una
  coincidencia editorial exacta, ficha de preparación, fases, puntos de atención,
  errores, variantes, fuentes y estado de revisión.
- En la sesión, «Ver técnica paso a paso» abre una hoja y conserva la cuadrícula
  de series sin navegar ni enviar cambios a la API. Escape cierra y devuelve el
  foco al botón; Tab permanece dentro de la hoja.
- `/prototipo/fase-3`: revisión de los diez borradores, controles de reproducción,
  pausa, reinicio, velocidad y fases; comparación de posiciones mediante
  `?vista=lamina`. Las observaciones se guardan localmente y se pueden descargar
  como JSON. No se envían a terceros ni validan o publican las fichas.

La vinculación exige nombre, grupo y equipo coincidentes; admite las claves del
catálogo y sus etiquetas exactas en la API de sesión. Un nombre parcial,
un ejercicio personalizado o un equipo distinto recibe la descripción del
catálogo, sin heredar una ilustración que podría ser incorrecta. No se ampliaron
tablas ni se requiere otra migración de base de datos para este incremento.

## Representación y revisión

El autor señaló que la primera figura resultaba confusa. Se rehízo como esquema
de cabeza circular, segmentos simples, articulaciones y apoyos visibles. La vista
lateral representa un solo lado salvo cuando ambos apoyos son necesarios; la
vista frontal distingue las extremidades. Se retiraron ropa, cabello, rellenos y
decoración que dificultaban leer la postura.

Se corrigieron las rodillas flexionadas en la posición de pie, el contacto de las
manos con el suelo en las lagartijas, la estabilidad de los pies en sentadilla y
zancadas, la separación del suelo de la rodilla trasera y el recorrido exterior
de los codos en las elevaciones laterales. Estas comprobaciones geométricas no
sustituyen una revisión de técnica humana.

La plancha se muestra como posición sostenida, sin fabricar repeticiones ni
prescribir segundos a partir de la ilustración. La preparación y la salida se
explican en texto. En los movimientos dinámicos, un ciclo visual dura seis
segundos a 1×; es una velocidad de demostración, no una cadencia prescrita.

La sesión existente también prescribe la plancha en repeticiones y carece de un
campo de duración. La ficha abierta desde esa prescripción señala la diferencia;
no transforma 8–12 repeticiones en 8–12 segundos. Corregir la unidad del motor,
persistencia e historial requiere un cambio específico y sigue pendiente. La
ficha visual no acredita que esa prescripción anterior sea adecuada.

Todas las fichas permanecen en estado `pendiente`, sin responsable ni fecha de
validación inventados. El sistema normal muestra posiciones estáticas; el piloto
permite revisar el movimiento. Para habilitar una animación revisada, registrar
el estado, responsable y fecha en la versión editorial, tras recibir la revisión
real. Las notas del navegador no cambian ese registro.

## Selección y referencias

La selección cubre los seis grupos del catálogo inicial; no se atribuye a una
estadística de uso ni a equipo confirmado en FAMAS. Redacción en español y SVG
originales; no se copiaron fotos ni videos de las fuentes. Consulta: 30-10-2026.

| Ficha | Referencia técnica |
|---|---|
| Press de banca con barra | [NASM, Barbell Bench Press](https://www.nasm.org/resource-center/exercise-library/barbell-bench-press) |
| Lagartijas | [NASM, Push-Up](https://www.nasm.org/resource-center/exercise-library/push-up) |
| Remo con barra | [ACE, Bent-over Row](https://www.acefitness.org/resources/everyone/exercise-library/12/bent-over-row/) |
| Jalón al pecho | [ACE, Seated Lat Pulldown](https://www.acefitness.org/resources/everyone/exercise-library/158/seated-lat-pulldown/) |
| Sentadilla con barra | [NASM, Squats and Deadlifts, pp. 6–8](https://trainer.nasm.org/hubfs/NASM_Free%20Guide_Squats%20and%20Deadlifts.pdf?hsLang=en) |
| Zancadas con mancuernas | [ACE, progresión de zancadas](https://www.acefitness.org/resources/everyone/blog/5032/try-this-fat-burning-leg-workout/) |
| Elevación de talones | [Mayo Clinic, Calf raise](https://www.mayoclinic.org/healthy-lifestyle/fitness/multimedia/calf-raise/vid-20084681) |
| Elevaciones laterales | [ACE, Lateral Raise](https://www.acefitness.org/resources/everyone/exercise-library/26/lateral-raise/) |
| Curl con barra | [NASM, Barbell Bicep Curl](https://www.nasm.org/resource-center/exercise-library/barbell-bicep-curl) |
| Plancha frontal | [NASM, Plank](https://www.nasm.org/resource-center/exercise-library/plank) |

Las fuentes no son un permiso para reutilizar sus gráficos ni certifican estos
SVG. Algunas clasificaciones difieren del catálogo provisional: ACE clasifica
el remo con barra como avanzado, mientras el catálogo actual lo admite desde
principiante. La ficha comunica la exigencia técnica; este incremento no altera
las reglas del motor sin una revisión específica de ese cambio.

Variantes y alternativas son referencias para conversar con quien guía al
usuario. No se aplica una sustitución ni se recomiendan según lesiones desde la
biblioteca. La selección, volumen, cargas y exclusiones de la rutina se conservan
en el motor actual; una sustitución persistente y su recálculo quedan fuera de
este piloto. La ilustración no captura cámara ni evalúa el cuerpo del usuario.

## Verificación

`npm run test:entrenamiento`: veintiún casos automatizados sobre vinculación,
filtros, bajas, integridad de prescripción, publicación editorial, ciclo y
velocidad, geometría de los diez ejercicios, apoyos y recorrido de codos.
No acreditan corrección biomecánica ni comprensión humana.

`npm run build` y `npm run verificar:construccion` comprueban la compilación y la
conservación de las diez páginas públicas y los armazones privados. Los recursos
de biblioteca y demostración se cargan aparte; abrir el panel no inicia ciclos.
La animación empieza por acción del usuario y se pausa al ocultarse el documento
o salir su recurso de la vista. Movimiento reducido ofrece posiciones estáticas
y mantiene las instrucciones.

Comprobaciones en navegador: catálogo de 25 ejercicios con 10 fichas vinculadas;
búsqueda «jalon» encuentra «Jalón»; cuenta requerida para la biblioteca; ficha
estática en cuentas normales; reproducción, pausa y velocidad 0.5× en el piloto;
movimiento reducido con tres imágenes y reproducción desactivada a 320 píxeles,
sin desbordamiento horizontal; conservación del valor ficticio escrito en una
serie al abrir y cerrar su ficha. Shift+Tab y Tab recorren el diálogo, Escape
cierra y restituye el foco. Se corrigió el intento de enfocar enlaces dentro de
desplegables cerrados, que Chrome aún puede reportar con rectángulos de diseño.
Se bloqueó temporalmente la descarga del módulo de ficha en una pestaña de
ensayo: el diálogo conservó la descripción del catálogo y el resto de la sesión.
Después se retiró el bloqueo y se recargó la pestaña. Los fallos de ilustración
tienen un respaldo separado para mantener las indicaciones escritas.

Las pruebas de backend de la fase 2 (709 aprobadas, 2 omitidas) son evidencia de
esa ejecución anterior: no se suman a las pruebas de este incremento. No se
cambió el backend en fase 3. Las capturas locales se conservan en
`operaciones/evidencias/fase3/`, excluidas de Git.

## Cierre pendiente y tesis

Revisar cada ficha comparando fuente, postura, apoyos, agarre, articulaciones,
equipo, vista y fases. Registrar los ajustes y la revisión real antes de activar
la reproducción en las cuentas normales. Confirmar el equipamiento de campo y
evaluar las tareas en un teléfono físico y con participantes; la emulación no
acredita ese resultado. El piloto no cumple todavía la condición de diez fichas
técnicamente revisadas.

La tesis no fue modificada. Trasladar este incremento al alcance de la biblioteca,
diseño de interfaces y recursos, estados editoriales, carga bajo demanda,
accesibilidad, casos ejecutados y manual de usuario. Mantener explícita la
diferencia entre prueba de software, revisión de técnica y evaluación humana.
Los pendientes de las fases 0–2 siguen vigentes.
