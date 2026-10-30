# Fase 4: alimentación práctica, restricciones y semana

Incremento local del 30 de octubre de 2026. **Piloto implementado, en revisión**.
No se desplegó ni se migró producción. Se leyeron el plan maestro y los informes
de las fases 0–3 antes de editar. Se conservaron los cambios locales anteriores,
sin reiniciar Git, borrar archivos previos ni crear un commit que los mezcle.

## Entrega y recorrido

- `/comer/preferencias`: patrón omnívoro, vegetariano o vegano; alergias e
  intolerancias por separado; exclusión de alimentos por ID; otra restricción.
  Las opciones se guardan en la cuenta, sin copiar estos datos a localStorage.
- `/comer/recetas`: biblioteca de **18 recetas originales en borrador**, con
  ingredientes reales del catálogo, cantidades, estado de pesada, rendimiento
  de una porción de referencia, medidas caseras aproximadas, pasos y tiempo.
  La biblioteca muestra porciones de referencia, separadas de las asignadas al plan.
- `/comer/semana`: siete días numerados, cinco tiempos cada día, recetas con
  cantidades calculadas, aportes, alternativa por comida y compras agregadas.
  Los días 1–7 no se presentan como fechas ni se vinculan automáticamente al lunes.
- `/comer` conserva el menú anterior y ofrece la entrada a Semana. Si existe una
  semana válida, muestra su día 1 explícitamente. Las consultas antiguas de compras
  suman la semana real y muestran el estado de los ingredientes.

A permanece claro y B oscuro. Se reutilizan tokens, preferencias de tema, hoja
de diálogo y navegación existentes; no se cambió la identidad ni se añadieron
dependencias. Las nuevas pantallas se cargan bajo demanda. Alimentación y
privacidad públicas describen el piloto y los nuevos datos guardados.

## Restricciones efectivas

Las nueve claves de alérgenos del piloto son leche, huevo, pescado, crustáceos,
maní, frutos secos, trigo, soya y sésamo; no representan todas las alergias posibles.
Lactosa y exclusión de gluten tienen claves propias. Avena se excluye al declarar
gluten porque el catálogo no acredita certificación del producto. Pasta se excluye
también por huevo como precaución ante la composición genérica sin marca.

La composición editorial exige nombre exacto y los cuatro valores nutricionales
de la entrada provisional correspondiente. Un nombre parecido o una composición
modificada no hereda estos datos. Los productos ambiguos, incluido aceite vegetal
sin mezcla declarada e Incaparina sin etiqueta concreta, no entran en las recetas;
con restricciones tampoco entran en el generador anterior. No se adivina ausencia
de alérgenos en un alimento desconocido. Las preferencias vegetarianas y veganas
excluyen las fuentes animales correspondientes.

El filtrado ocurre antes de seleccionar ingredientes y antes de calcular
sustituciones. Guardar restricciones invalida la semana anterior. Las lecturas
de menú y compras antiguos rechazan porciones que entren en conflicto con las
restricciones vigentes. Otra restricción detiene la propuesta y deriva a revisión
profesional. Se mantiene el bloqueo de las condiciones médicas existentes.

Esto filtra la composición declarada del alimento genérico; **no certifica marcas,
trazas, contacto cruzado ni la seguridad clínica de una comida**. Revisar el
catálogo de alérgenos y su clasificación con un profesional antes de publicación.
No se guardan diagnósticos nuevos ni se atribuyen a usuarios de prueba.

## Cálculo, sustitución y compras

Los objetivos energéticos y los tres macronutrientes se toman del plan vigente;
no se modificaron las fórmulas, el modelo neuronal ni sus salvaguardas. Un ajuste
acotado por ingrediente busca cubrir esos cuatro objetivos y conserva el reparto
energético 25/10/35/10/20 ya existente. Las cantidades se redondean a gramos y
los aportes se vuelven a calcular sobre esa cantidad final.

El piloto exige diferencias máximas del **6 %** en energía y cada macronutriente
del día, así como en energía de cada tiempo. El 6 % energético ya aparecía en
las pruebas de fidelidad del menú anterior; **extenderlo a macronutrientes es un
criterio técnico nuevo del piloto, pendiente de acuerdo y revisión profesional**.
No se presenta como tolerancia clínica aprobada. Los límites de cantidades y la
factibilidad culinaria también requieren esa revisión.

Se rechaza una semana no factible sin guardar días parciales ni eliminar
restricciones. Hay combinaciones restrictivas y objetivos bajos con proteína alta
que este catálogo no cubre, por ejemplo el ensayo de 1200 kcal, 100 g de proteína,
125 g de carbohidrato y 35 g de grasa. No se amplía silenciosamente el margen ni
se pide quitar una alergia. La variedad depende de las recetas compatibles;
la semana ficticia de revisión reunió 17 recetas distintas, sin prometer esa
cifra para todos los perfiles.

Cambiar comida ajusta otra receta a los aportes de la comida actual, vuelve a
comprobar los objetivos del día y su reparto y actualiza toda la lista de compras.
El servidor no acepta aportes, gramos ni costos enviados por el cliente.
Una revisión monotónica rechaza cambios sobre versiones antiguas; un bloqueo de
la cuenta serializa las mutaciones en PostgreSQL y una actualización condicional
comprueba la revisión al escribir.

La semana conserva ingredientes y cantidades calculadas. Una firma de versión
editorial, restricciones y catálogo obliga a recalcular si cambia disponibilidad,
precio, composición o medida casera. Consultar no modifica la semana.

Las compras suman los ingredientes de los 35 tiempos, sin multiplicar el día 1
por siete. Las cantidades son de parte comestible **en el estado indicado**:
arroz, pollo y legumbres cocidos no equivalen al peso que se compra crudo.
No se inventaron factores de rendimiento de cocción. Los precios conservan la
estimación provisional por 100 g de la base; su fuente se identifica y la fecha
de observación queda nula. No se atribuye una visita al mercado inexistente.
La vista nueva devuelve costo incompleto cuando falta un precio, en vez de cero.
La pantalla antigua conserva su advertencia de subtotal y precios faltantes.

## Persistencia y operación

`0003_alimentacion_practica`, sobre `0002_recuperacion_acceso`, crea:

| Tabla | Contenido | Propiedad |
|---|---|---|
| `preferencias_alimentarias` | Datos estructurados JSON. | Clave de la cuenta autenticada. |
| `semanas_alimentarias` | Plan de origen, revisión, firma y semana JSON. | Una semana vigente por cuenta. |

Se usan claves foráneas y borrado en cascada al eliminar la cuenta. No se alteran
filas ni columnas de menús, perfiles, planes o bitácoras anteriores. Las recetas
editoriales viven en código versionado; el JSON de la semana conserva su versión
y los ingredientes usados, no es un editor de recetas para administradores.

Respaldar y ensayar antes de actualizar una base real. Desde `backend`:

```powershell
uv run python gestionar_esquema.py estado
uv run python gestionar_esquema.py actualizar
uv run python gestionar_esquema.py comprobar
```

No utilizar `adoptar` ni `stamp head` para saltar revisiones de una base antigua.
La migración se comprobó desde 0002 con cuentas pobladas, también al revertir y
reaplicar exclusivamente sobre esquemas de prueba desechables.

Para revisar el piloto en otra base **nueva y ficticia**, usar
`ensayar_fase4.py --servir --puerto 18140` desde backend, con
`URL_POSTGRESQL_PRUEBAS` apuntando al contenedor local de fase 0 según
[MIGRACIONES.md](MIGRACIONES.md). Se niega a usar un destino remoto. El cliente
de ensayo se inicia en una terminal separada:

```powershell
$env:VITE_URL_API='http://127.0.0.1:18140/api/v1'
npm run dev -- --host 127.0.0.1 --port 15174 --strictPort
```

Abrir `http://127.0.0.1:15174/comer/semana`. Cuenta exclusivamente ficticia:
`demostracion.fase4@example.com`, contraseña de ensayo `Demostracion2026`.
El script conserva la base para inspección y registra su nombre sin credenciales
en `evidencias/fase4/entorno-visual.json`. No usar esas credenciales en producción.

## Evidencia ejecutada

Windows, Python 3.12, SQLite temporal y PostgreSQL 16 local. Evidencia excluida
de Git bajo `operaciones/evidencias/fase4/`:

- Suite completa: **759 aprobadas y 3 omitidas**, 158 avisos, 270.59 s,
  `pruebas-completas.xml`. Esta ejecución precede al ajuste final de redondeo
  y metadatos de compras, comprobados por la regresión siguiente. Dos omisiones
  de dialecto anteriores y una nueva
  omisión de concurrencia de filas en SQLite, comprobada en PostgreSQL.
- Regresión posterior al añadir el estado de pesada a las compras antiguas y
  limitar la holgura de redondeo del 6 % a dos centésimas en aportes pequeños:
  **103 aprobadas y una omitida**, 42.25 s, `regresion-final.xml`.
  Cubre alimentación, migración/persistencia, costos/compras y plan nutricional.
- Ejecución focalizada inicial con migraciones: 72 aprobadas y 3 omitidas,
  `pruebas-focalizadas.xml`. No sumar estas ejecuciones a la suite completa.
- Los 21 casos del cliente para fase 3 siguen aprobados. Construcción y
  verificador HTML correctos: diez páginas públicas, armazón privado sin datos
  y carga separada de alimentación. No se acredita publicación con la compilación.
- Navegador integrado sobre la base ficticia: acceso, semana, selección del día 2,
  alternativas del almuerzo, sustitución de pollo por tilapia y cambio visible de
  costo semanal de Q343.73 a Q346.60. Se observaron confirmación y aportes
  actualizados. La semana a 320 px no presentó desbordamiento horizontal.
- Guardado de alergia ficticia a leche, bloqueo de la semana anterior y
  generación de otra semana, con doce recetas distintas en ese caso. Revisión de
  compras con sus estados, formulario claro a 320 px, semana oscura a 1440 px,
  receta oscura a 320 px y búsqueda «mani» que encuentra «maní». Capturas
  `restricciones-claro-320.png`, `compras-claro-320.png`,
  `semana-oscuro-escritorio.png` y `receta-oscuro-320.png`. Sin desbordamiento
  horizontal en las vistas medidas de semana, compras y recetas a 320 px.
  Se corrigió la pérdida de foco causada por deshabilitar el botón durante la
  consulta; Escape cierra el diálogo y devuelve el foco al botón de cambio.
  La matriz de comprobaciones está en `revision-ui.json`.

Las pruebas comprueban exclusiones en ingredientes y alternativas, etiquetas
desconocidas, preferencias entre cuentas, índices fuera de rango, rechazo de datos
arbitrarios, menú antiguo incompatible, catálogo modificado, bloqueo médico,
no factibilidad, sumas de compras, falta de precios, persistencia JSON,
actualización poblada sin pérdida y rechazo de una de dos escrituras concurrentes.
No son validación nutricional ni una medición de uso en teléfono físico.

## Pendientes revisados y condición de cierre

| Pendiente | Estado al terminar este incremento |
|---|---|
| A claro y B oscuro | Decisión conservada; no se abrió otra selección de identidad. |
| Diez fichas simplificadas de fase 3 | Siguen pendientes de revisión técnica; sin responsables o fechas inventados ni reproducción habilitada como validada. |
| Gmail | Sigue sin autorización; no existe `.env.gmail` en este entorno. No se enviaron correos. El propietario debe completar [CORREO_GMAIL.md](CORREO_GMAIL.md). |
| Plancha en repeticiones | Problema confirmado. Sigue abierto: duración explícita en motor, prescripción, registro, progresión e historial, con migración y pruebas. No se convirtieron repeticiones antiguas a segundos ni se eligió una dosis sin revisión. |
| Recetas y datos | Revisar las 18 preparaciones, aportes, estado crudo/cocido, medidas, cantidades, tiempos y tolerancias con un profesional. |
| Campo y compras | Confirmar alimentos locales, precios con fecha/fuente y rendimiento entre compra cruda y cantidad comestible/cocida. |
| Evaluación y publicación | Ampliar la revisión de estados en ambos temas, completar teclado, móvil físico y comprensión con participantes; respaldar, migrar y publicar primero en pruebas. |

No se declara cerrada la fase 4 ni las fases anteriores. No se investigó la
degradación concurrente de fase 0 ni se atribuyen nuevos resultados de adherencia.

La tesis DOCX de 667 pruebas permanece intacta. Incorporar en una copia versionada:
MEJ-08/09 y criterios, diccionario de las dos tablas, versión editorial y estado de
ingredientes, exclusiones, cálculo y límites del ajuste, concurrencia, interfaces,
privacidad y resultados por ejecución. Mantener las cifras históricas por versión.

## Fuentes consultadas

Consulta del 30 de octubre de 2026. La composición y los precios siguen siendo
los del catálogo provisional local, sin verificación nueva de laboratorio o campo.
La composición de alérgenos se infiere del alimento genérico y requiere revisión.

- [FDA: Food Allergies — What You Need to Know](https://www.fda.gov/food/buy-store-serve-safe-food/food-allergies-what-you-need-know): referencia de categorías de alérgenos y lectura de ingredientes; no se presenta la legislación estadounidense como norma guatemalteca.
- [FoodSafety.gov: Safe Minimum Internal Temperatures](https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures): referencia para notas de cocción y recalentamiento. Redacción de recetas original; no se copiaron imágenes.
