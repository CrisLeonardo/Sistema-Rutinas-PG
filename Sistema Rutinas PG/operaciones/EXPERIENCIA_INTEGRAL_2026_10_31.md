# Experiencia integral de Senda

31 de octubre de 2026, Guatemala. Implementación y comprobación local.
Continúa el incremento de `CONEXION_Y_EXPERIENCIA_2026_10_31.md`; sus resultados
anteriores se conservan como ejecuciones separadas. La fase 7 permanece abierta.

**Petición posterior del autor:** el 31-10-2026 autoriza enviar la mejora a `main`.
Los párrafos de implementación local describen la revisión anterior al envío.
Esta autorización no ejecuta migraciones de producción ni demuestra por sí sola
que Render haya desplegado el commit. Verificar ambas cosas por separado.

## Cambios terminados

- Las **25 entradas del catálogo inicial** tienen ficha visual: 24 recorridos
  dinámicos y plancha como sostén estático. Se agregaron las quince fichas que
  faltaban, equipo, apoyos, preparación, tres fases, errores y referencias.
  Las figuras y los textos son propios. Todas siguen pendientes de revisión
  técnica; no se modificaron prescripciones, selección, dosis ni progresión.
- Reproducción, pausa, velocidad, selección de fases y recorrido manual.
  Repetir continuamente es optativo. Al ocultarse la pestaña o salir de vista
  se detiene la reproducción. Curl alterno muestra un brazo después del otro;
  las manos de los ejercicios suspendidos permanecen en la barra.
- Ayuda «Cómo usar» con tres acciones concretas en cada pantalla privada,
  incluido entrenamiento y administración. Navegación de sección consistente,
  regreso visible y foco en el título al cambiar de pantalla. En móvil los
  destinos se distribuyen en filas para que ninguno quede oculto a un lado.
- Respuestas de pulsación, foco, selección, carga, entrada de pantallas,
  tarjetas, anillos, barras, detalles y guardado. Senda permite reducir el
  movimiento desde Más y también respeta la preferencia del sistema operativo.
  En ese caso las guías dinámicas presentan tres posiciones estáticas.
- El panel ofrece la siguiente acción, aprender ejercicios, organizar comidas
  y Mi senda. Plancha muestra segundos y referencia provisional, corrigiendo
  el antiguo resumen de cero repeticiones. Los campos de entrenamiento aclaran
  que kg significa carga adicional y permiten registrar cero.
- Plan y medidas distinguen error de consulta de primera utilización. Los
  informes permiten recuperar su catálogo y descartan respuestas anteriores
  al cambiar rápidamente de informe. Preferencias conserva lo consultado y los
  cambios escritos si falla el catálogo de alimentos; se reintenta ese catálogo.
- Historial conserva el resumen si falla la lista de sesiones y permite
  reintentar una gráfica. Administración carga sus catálogos independientemente.
  Las marcas de compras se guardan por cuenta. Registrar avance no sobrescribe
  un peso que ya se está escribiendo ni presume un porcentaje de cumplimiento.
- Se conserva la conexión anticipada, el tratamiento de resultados parciales,
  el reintento explícito y la sesión ante errores temporales del incremento previo.

## Verificación realizada

Evidencias locales excluidas de Git:
`operaciones/evidencias/experiencia-integral-2026-10-31/`.

- **69 pruebas del cliente aprobadas, cero fallos**, en una invocación final:
  14 conexión, 36 entrenamiento, 11 interacción y 8 experiencia. Resultado en
  `cliente-cierre.xml` y `cliente-cierre.log`. No se suman a las 46 del incremento
  anterior. Los casos comprueban cobertura contra el catálogo real del servidor,
  coordenadas, apoyos, alternancia, ayuda, navegación y preferencia de movimiento.
- Construcción de producción y verificador correctos: diez páginas públicas y
  seis armazones privados sin datos. `construccion.log` y `verificacion.log`.
  No se añadió una dependencia ni se actualizó el bloqueo del proyecto.
- **36 pruebas existentes de informes del servidor aprobadas**, en ejecución
  separada (`informes.xml`): formatos, aislamiento de cuentas y permisos.
  Se conserva una advertencia de obsolescencia Starlette/httpx.
- Navegación por diecinueve pantallas privadas en tamaño normal y diecisiete
  principales a 320 px en claro; sin errores visibles ni desbordamiento del
  documento en esas observaciones. Las tres pantallas de administración se
  comprobaron a 1366 y 320 px en oscuro; mediciones en `administracion-*.json`.
- Las veinticinco fichas se abrieron y se seleccionó una fase en claro y oscuro
  a 320 px. En la comprobación final oscura hubo 25 figuras, tres fases por
  ficha y 24 reproductores, sin alertas ni desbordamiento del documento.
  Mediciones de ese recorrido: `guias-320-oscuro.json`.
- Se comprobaron movimiento reducido, fotogramas, ayuda, cierre con Escape y
  devolución del foco. Se restauró tema oscuro, movimiento normal y el tamaño
  predeterminado del navegador al terminar.
- Sesión ficticia: guía dentro del entrenamiento, marcar una serie, descanso,
  terminar, guardar y recibir Primer paso. Se verificaron 20 segundos de sostén,
  cero repeticiones y cero carga adicional; sin participantes reales.
- Los cuatro informes personales respondieron 200 en PDF, CSV y Excel:
  doce exportaciones en `exportaciones.json`. La descarga de PDF también se
  comprobó desde la pantalla y mostró su confirmación.

## Fallos encontrados y recuperación

Los ensayos se hicieron con SQLite ficticia y API local en 18160; no se usaron
datos ni credenciales de producción. Un envoltorio temporal devolvió GET 503
en plan, perfil, catálogo de informes y catálogo de alimentos. Plan y perfil
mostraron reintento sin formularios engañosos de creación. Informes mostró el
reintento y recuperó su catálogo al volver a entrar. Preferencias retuvo sus campos; al recuperar alimentos
conservó la selección vegana escrita sin guardar. El primer envoltorio omitía
CORS en el error simulado; se corrigió el instrumento antes de comprobar esos
estados. Las banderas quedaron vacías y el envoltorio fue retirado del proceso;
la revisión termina con la API ordinaria, sin inyección de fallos.

Un primer ensayo de PDF y Excel devolvió 500: faltaban `fpdf2` y `openpyxl` en
el entorno virtual local. Se instalaron las versiones ya declaradas y bloqueadas
por el repositorio (2.8.9 y 3.1.5). Las exportaciones posteriores y las 36 pruebas
pasaron. Este hallazgo local no prueba el estado de esas librerías en Render.
No se cambió el servicio de exportación para ocultar ese fallo.

La primera revisión geométrica encontró un codo de abdominales fuera del lienzo;
se corrigió. La lámina de comparación inicial repetía identificadores SVG al
combinar renderizados independientes; se rehízo como un solo árbol React.
Se ajustaron proyección de aperturas, pies y apoyos de las figuras. La lámina
temporal se retiró de `public` antes de construir; no forma parte del producto.

Las referencias están enlazadas en cada ficha. La comprobación de fuentes del
31-10 incluyó [ACE](https://www.acefitness.org/resources/everyone/exercise-library/126/single-arm-row/),
[Mayo Clinic](https://www.mayoclinic.org/healthy-lifestyle/fitness/multimedia/abdominal-crunch/vid-20084664),
[PureGym](https://www.puregym.com/exercises/arms-and-shoulders/shoulder-press/arnold-press/),
[Catalyst Athletics](https://www.catalystathletics.com/exercise/135/Ab-Rollout/) y
[ActivTrax](https://instructions.activtrax.com/exercises/show_exercise_instruction/1211).
Tres referencias nuevas que bloquearon la consulta automatizada con 403 se
sustituyeron por fuentes accesibles. Pájaros distingue la referencia de control
en variante sentada del esquema adaptado de pie. Consultar bibliografía y probar
geometría no equivale a un dictamen profesional de estos esquemas.

## Monitor y límites vigentes

El autor confirmó en este chat que ya cambió el monitor solicitado a GET del
estado de la API cada cinco minutos. Es confirmación del autor; no se consultó
el historial de ese servicio externo. El diagnóstico de dominio y reenvío del
incremento anterior permanece en su informe y no se presenta como otro ensayo.

No hay publicación, push ni migración de producción, conforme a `AGENTS.md`.
No se tocaron tesis, reglas individuales, comunidad desactivada ni migraciones.
Las pruebas locales y tamaños emulados no acreditan teléfono físico, experiencia
con personas, accesibilidad manual completa, rendimiento de Render o estabilidad
bajo 50 usuarios. Se conservan todos los ensayos anteriores, incluidos los fallidos.
El primer plan histórico de proceso nuevo de 6.29 s sigue fuera de la meta de 3 s;
no se modifica la meta de 2 s para consultas. Siguen pendientes revisores, Gmail
real, participantes, teléfono, publicación y actualización de tesis en copia.
