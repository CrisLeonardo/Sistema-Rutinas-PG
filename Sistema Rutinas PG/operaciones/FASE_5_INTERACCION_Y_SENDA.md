# Fase 5: respuestas de interacción y Mi senda

Incremento local del 30 de octubre de 2026. Implementado y comprobado con datos
ficticios; pendiente de evaluación con participantes, teléfono físico y despliegue
en pruebas. Se conservaron los cambios locales de las fases anteriores. No se
editaron el backend, las fórmulas ni la tesis, no se crearon migraciones y no se
publicó una versión nueva.

## Qué cambia en los recorridos

| Acción del plan maestro | Comportamiento local entregado |
|---|---|
| Completar una serie | La fila confirma su estado y el aviso identifica ejercicio y serie. Distingue la anotación en el dispositivo del guardado posterior en el servidor. Desmarcar también se anuncia. |
| Iniciar descanso | El reloj usa una fecha límite, se actualiza al volver a la pestaña y ofrece Saltar/Listo. El final se comunica en texto, sin anunciar cada segundo. |
| Guardar sesión | Mantiene series, esfuerzo y notas ante un fallo. La pantalla de resultado recibe foco, muestra el resumen y las recompensas que devolvió el servidor, y permite volver a la rutina o consultar Mi senda. |
| Alcanzar insignias | Las nuevas claves de la respuesta se resuelven contra el catálogo propio. Se muestran nombre y explicación con una entrada breve; si falla la consulta, el registro permanece guardado y se ofrece Mi senda. |
| Cambiar comida | Conserva día y comida. Muestra comparación de porciones, energía, macronutrientes, costo de la comida y costo semanal; el fallo de envío conserva comida y alternativas. |
| Consultar evolución | Las gráficas entran suavemente y ofrecen una tabla nativa con todas las observaciones y unidades. No se inventan valores para series vacías. |
| Enviar formularios | Perfil y progreso exponen el estado de envío y bloquean sus campos mientras esperan. Los errores conservan los datos. Los resultados de sesión y progreso reciben foco sin esperar una animación. |

Los puntos, niveles, insignias y límites siguen siendo calculados por el servidor.
Un resultado con cero puntos no se confunde con un registro fallido. No se
añadieron premios por restricciones alimentarias, pérdida de peso, cargas extra
o sesiones adicionales. Este incremento no cambia las reglas de juego históricas
ni certifica que todas ellas hayan sido revisadas desde una perspectiva clínica.

Mi senda conserva anillo, cifras, camino y reglas. Añade una siguiente acción
vinculada a la rutina, la mejor racha registrada y filtros Todas/Conseguidas/Por
conseguir. Tras una pausa, el mensaje explica que el recorrido y las insignias
se conservan; no borra logros ni obliga a recuperar una racha.

## Descanso, movimiento y accesibilidad

El cronómetro deja de restar uno por cada ejecución de `setTimeout`: calcula
`ceil((venceEn - ahora) / 1000)`, acotado a cero. Las revisiones periódicas y el
evento de visibilidad corrigen los intervalos retrasados. El aviso de finalización
ocurre una vez por descanso y el trabajo periódico se detiene al terminar.
No se añadió un servicio en segundo plano ni se garantiza avisar con el navegador
cerrado o el teléfono bloqueado.

La vibración está **apagada por defecto**. Solo la preferencia explícita
`encendida` la habilita; se conserva una elección previa expresa. Se intenta
únicamente si el documento está visible y el navegador la admite. Un rechazo de
la API no elimina la confirmación textual. No se añadió sonido ni se solicitan
permisos de cámara, micrófono o notificaciones.

Las nuevas entradas duran 180–220 ms. Se acortaron las transiciones anteriores
de 900 ms del nivel. No hay confeti, contadores artificiales, reproducción
continua ni una espera de animación antes de guardar. `prefers-reduced-motion:
reduce` suprime animaciones, transiciones y desplazamiento suave, también en los
componentes anteriores. Los resultados hacen foco y se sitúan al inicio de forma
inmediata. Los avisos de confirmación permanecen disponibles para leerlos.

Se corrigió el foco al guardar una comida: se restaura después del desmontaje del
diálogo y de habilitar el botón, evitando la carrera entre una respuesta de red y
la limpieza de foco del diálogo. La comparación permanece durante la visita y
puede cerrarse; no se persiste otro historial de alimentación ni se ofrece
deshacer un cambio ya guardado. Recargar conserva la semana del servidor, no el
recibo de comparación en memoria.

Estas comprobaciones no constituyen certificación WCAG ni sustituyen pruebas
con lector de pantalla y usuarios del público objetivo.

## Tarjetas de insignias

Una insignia conseguida permite abrir una vista previa, descargar un SVG original
y copiar un mensaje. La tarjeta incluye únicamente el nombre de la insignia y
texto fijo de Senda. No copia nombre de cuenta, correo, puntos, fecha, medidas,
cargas, calorías, notas ni historial. La lista de campos se limita expresamente
en el generador; el nombre se escapa como texto XML y el SVG no carga recursos
externos. No se permite generar tarjetas desde insignias bloqueadas.

No se envía ni publica nada desde el sistema. Descargar prepara un archivo local;
copiar escribe el mensaje solo tras pulsar el botón. La persona elige después
dónde compartirlo. La tarjeta no sustituye el símbolo definitivo de la marca,
que sigue pendiente de selección.

## Archivos principales

- `frontend/src/interaccion/respuestas.mjs`: reloj, preferencia háptica,
  confirmaciones, copia de comparaciones y tarjeta SVG.
- `frontend/src/componentes/RespuestaAccion.jsx`, `ResultadoAccion.jsx`,
  `RecompensaAccion.jsx`, `TarjetaLogro.jsx`, `CambioComidaGuardado.jsx` y
  `DatosGrafica.jsx`: respuestas, resultados, vista previa y valores accesibles.
- `BitacoraSesion.jsx`, `RegistroProgreso.jsx`, `PerfilBiometrico.jsx`,
  `Senda.jsx` y `AlimentacionPractica.jsx`: integración en los recorridos reales.
- `CronometroDescanso.jsx`, ambas gráficas, preferencias y estilos de interacción.

No se añadieron dependencias. La construcción conserva las diez páginas públicas,
los armazones privados sin datos y la separación de recursos de la fase 3.

## Evidencia de verificación

Comprobaciones del 30 de octubre en Windows, Node y navegador integrado. API de
pruebas en `127.0.0.1:18140`, cliente en `127.0.0.1:15174`, base ficticia creada
por el ensayo de fase 4. No se usaron cuentas personales ni datos productivos.

- `npm run test:interaccion`: **11 casos aprobados**, cero fallos. Incluyen tiempo
  real con un salto de reloj equivalente a una pestaña suspendida, consentimiento
  háptico, separación local/servidor, comparación sin referencias mutables,
  costos incompletos, escape y privacidad del SVG y renderizado de tablas de
  las dos gráficas con React sobre módulos compilados por Vite.
- `npm run test:entrenamiento`: **21 casos aprobados**, cero fallos. Mantiene la
  vinculación y las condiciones editoriales de los diez borradores de fase 3.
  No acredita validación biomecánica.
- `npm run build` y `npm run verificar:construccion`: correctos. Se conservan
  diez páginas públicas con contenido y los armazones privados sin datos.
- `git diff --check`: sin errores de espacio. El manifiesto anterior al trabajo
  se conserva en `evidencias/fase5/estado-inicial.json`.

No se volvió a ejecutar la suite del backend, puesto que no se editaron sus
archivos ni reglas. Las cifras de 759 pruebas de fase 4 y 103 de su regresión
siguen siendo evidencia anterior, y no se suman a los casos de interfaz nuevos.

Recorridos observados en el navegador:

1. Se anotó una serie ficticia de ocho repeticiones con 20 kg: confirmación
   explícita, progreso 1/14 y descanso 2:00. Se omitió el descanso desde el control.
2. Se bloqueó temporalmente **solo** la petición local de guardar la sesión. El
   error se mostró dentro de la hoja y conservó las notas y la serie. Tras retirar
   el bloqueo, la sesión quedó guardada, el título recibió foco y el servidor
   devolvió 305 puntos y las insignias Primer paso y Marca propia. Son datos de
   ensayo autodeclarados; no describen entrenamiento real.
3. Se revisó y descargó `senda-insignia.svg`. Se analizó como XML válido y se
   comprobó que no incluía los datos de la cuenta ni cifras del entrenamiento.
   Shift+Tab y Tab permanecieron dentro del diálogo; Escape lo cerró y devolvió
   el foco al botón de tarjeta.
4. Mi senda mostró dos insignias conseguidas al filtrar, conservó 18 en el
   catálogo y permitió consultar la próxima sesión. Se revisaron A claro y
   B oscuro a 320 px, sin desbordamiento horizontal.
5. Un registro ficticio de 78 kg, 80 % y una sesión produjo resultado con foco,
   mantuvo el plan y devolvió 130 puntos desde el servidor. La evolución mostró
   78 kg en una tabla nativa. En movimiento reducido la gráfica no tuvo animación
   y el anillo informó transición de 0 s.
6. Un bloqueo temporal de la petición local de cambiar comida conservó el diálogo
   y la comida anterior. Al retirarlo, el almuerzo cambió de pollo a tilapia y se
   mostraron Q16.49→Q19.76 por comida y Q323.20→Q326.47 por semana, junto con los
   aportes y las porciones reales. Un segundo cambio comprobó el foco restaurado
   tras la respuesta de red. La comparación se revisó a 320 px sin desbordamiento.

Los bloqueos de red y la emulación de movimiento se retiraron al terminar; el
tamaño de navegador se restituye. Las capturas se guardan bajo
`operaciones/evidencias/fase5/`, excluidas de Git. No se midieron en este
incremento red 3G, arranque en frío, concurrencia ni rendimiento en teléfono físico.

## Pendientes y tesis

La fase 5 permanece pendiente de evaluación humana y publicación en pruebas.
Revisar comprensión de los mensajes, teclado y lector de pantalla en los
recorridos completos; probar temporizador y vibración en un teléfono real, y
medir los tiempos y el rendimiento pendientes de fase 0. Comprobar recuperación
ante interrupción del proceso servidor; esta fase no añade una cola, sincronización
sin conexión ni idempotencia persistente a la API de entrenamiento.

Siguen abiertos Gmail, revisión técnica de los diez ejercicios, revisión
profesional de recetas y tolerancias, precios y rendimientos de campo, duración
explícita de la plancha, selección final del símbolo y los pendientes anteriores.
No se habilitó la reproducción de fichas sin revisar ni se convirtió ninguna
repetición histórica de plancha en segundos. La fase 6 social no se implementó.

Trasladar MEJ-10 a la copia versionada del DOCX de referencia: diseño de estados,
movimiento reducido, tablas accesibles, cronómetro, manejo de errores, privacidad
de tarjetas, capturas y resultados de esta ejecución. No atribuir mejoras de
adherencia ni cambios físicos a la incorporación de estos elementos.
