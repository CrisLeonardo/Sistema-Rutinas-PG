# Registro de cambios de tesis derivados de la fase 0

Fecha: 29 de octubre de 2026. Producto: Senda.

Este registro acompaña al código y a la evidencia de fase 0. Identifica lo que
debe trasladarse a una copia versionada de la entrega 3 de 667 pruebas. El DOCX
de referencia se conserva sin cambios; este archivo no sustituye una tesis
actualizada ni acredita que ya se hayan renovado índices o capturas.

## 1. Cambios que ya tienen implementación y evidencia

| Cambio | Lugar que revisar en tesis | Contenido a incorporar | Evidencia |
|---|---|---|---|
| Nombre comercial Senda elegido por el autor | Visión del producto, prototipos y manuales | Identificar Senda como nombre comercial; conservar el título académico salvo decisión expresa. | Plan maestro y decisión del autor. |
| Alembic para evolución del esquema | III: herramientas; IV 4.5.6; V 5.4 y 5.8; manual técnico | Revisiones versionadas, adopción inicial validada y separación entre cambio de esquema y arranque. | Archivos de migración y comandos de administración. |
| Registro técnico `alembic_version` | V: persistencia y diccionario técnico | Tabla de infraestructura con revisión aplicada, distinta de las quince entidades de negocio. No atribuir una entidad funcional nueva al dominio. | Creación desde cero y adopción. |
| Creación, adopción y rechazo de esquemas incompatibles | VI 6.3: pruebas transversales y despliegue | Registrar los veinte casos nuevos recogidos y el resultado separado: 19 aprobados y uno no aplicable a SQLite. | `pruebas-migraciones.xml`. |
| Respaldo y restauración con PostgreSQL 16 | VI 6.2 y evidencia de operación; manual de instalación | Dos bases ficticias, volcado/restauración, igualdad en quince tablas, revisión y secuencias. | JSON de recuperación y volcado ficticio. |
| Corrección del puerto predeterminado del cliente | V 5.2.3 y manual de instalación, si reproducen el valor anterior | Desarrollo usa `127.0.0.1:8010`; una URL configurada expresamente conserva prioridad. | Código del cliente y construcción PWA. |

Redacción técnica sugerida para adaptar al estilo del capítulo correspondiente:

«La evolución del esquema se administra mediante revisiones versionadas con
Alembic. La revisión inicial representa las quince tablas existentes. Una base
creada antes de incorporar este mecanismo solo se registra cuando una comparación
de estructura confirma su compatibilidad. La aplicación de revisiones constituye
una operación explícita de despliegue; no se ejecuta durante las peticiones de los
usuarios. Durante la transición se conserva la creación de tablas del arranque
anterior, que no sustituye la aplicación de migraciones sobre columnas existentes».

Redacción de evidencia sugerida:

«El 29 de octubre de 2026 se repitió la batería original, con 667 casos aprobados
y ningún fallo. La incorporación de migraciones se comprobó por separado mediante
veinte casos distribuidos entre SQLite y PostgreSQL 16: diecinueve se aprobaron y
uno no correspondió a SQLite, por verificar enumeraciones nativas. El ensayo de
recuperación utilizó datos ficticios y comparó el contenido de las quince tablas
antes y después de restaurar un volcado PostgreSQL. La igualdad de contenido y la
continuidad de las secuencias se verificaron, junto con cuarenta y cinco
comprobaciones de la interfaz de programación».

No reemplazar «667» por una suma de ejecuciones independientes. Para publicar un
nuevo total de batería completa se debe ejecutar y registrar esa batería como tal.

## 2. Afirmaciones existentes que requieren precisión

a) Presupuesto y operación: el autor confirmó gratuidad de todos los servicios
actuales. Diferenciar los Q0.00 de gasto recurrente declarado de las estimaciones
originales. No registrar contratación de un disco o dominio que no esté respaldada.

b) Estado del despliegue: la entrega 3 contiene una comprobación histórica del
dominio; esta fase no volvió a certificar su disponibilidad ni la configuración
productiva. Conservar la fecha de la evidencia histórica.

c) RN-01: la validación admite 18 años cumplidos, mientras «mayores de dieciocho»
puede interpretarse como un límite distinto. Alinear el lenguaje con el alcance
acordado, manteniendo la exclusión de menores.

d) RN-03: distinguir el cálculo base de proteínas de los ajustes posteriores del
plan. El módulo de salvaguardas puede emplear peso de referencia y un límite de
proporción energética; no afirmar que siempre entrega el rango sobre peso total.
Una modificación clínica requiere fundamentación y revisión competente.

e) RN-04: precisar si la cota corresponde a carga por ejercicio o a volumen
semanal. Los términos no son equivalentes; el código existente compara cargas.

f) Rutina: el campo de series objetivo se calcula con una referencia aunque la
generación pueda usar la red. Resolver cómo conservar y presentar el dato real
antes de cambiar la descripción académica de sus resultados.

g) Conectividad: la aplicación instalable conserva recursos de interfaz, no el
plan completo sin conexión. No eliminar el límite de conexión estable basándose
solo en la existencia de un trabajador de servicio.

h) Persistencia del modelo: la plantilla gratuita no habilita el disco descrito
en partes de la guía. Comprobar el mecanismo real antes de afirmar que un modelo
reentrenado sobrevive a reinicios o nuevas publicaciones. La imagen contiene el
artefacto inicial versionado, que es una garantía distinta.

## 3. Evidencia que aún no se puede afirmar

No hay comprobación visual nueva, prueba en teléfono físico, medición móvil de
tercera generación ni verificación del esquema o de la concurrencia en producción.
Un ensayo posterior con cincuenta usuarios contra PostgreSQL local terminó con
fallos y tiempos superiores a los límites informados. Su evidencia está en
`carga-local-50.txt` y en la sección de cierre del informe de fase 0. Debe
investigarse y documentarse antes de afirmar cumplimiento de rendimiento.
El navegador rechazó el acceso al entorno local. El resultado de
0.5464 segundos corresponde a una generación local aislada con el modelo cargado,
y no debe presentarse como un promedio productivo ni como tiempo de primer uso.

Tampoco se acredita revisión de campo de los catálogos, validación clínica de las
prescripciones ni mejora de adherencia por la nueva marca o futuras animaciones.

## 4. Reglas para trasladar y cerrar la actualización

a) Trabajar sobre una copia de `Leonardo Zepeda - Proyecto de Graduacion II -
Entrega 3 (667 pruebas).docx`, conservando el original y una bitácora de cambios.

b) Mantener la estructura Scrum, la terminología en español y los criterios de
aceptación vigentes. Explicar la utilidad de Alembic con una fuente oficial
verificada y compatible con la rúbrica, sin atribuirle resultados que no demuestra.

c) Actualizar diagramas e interfaces solo donde cambia el diseño; distinguir
la tabla técnica de revisión de las entidades del negocio. Renovar manuales y
capturas únicamente después de observar el comportamiento real.

d) Aplicar Times New Roman 12, interlineado 1.5, márgenes de 2.5 cm superior,
inferior y derecho y 3 cm izquierdo, enumeraciones alfabéticas, títulos acompañados
de texto y las extensiones mínimas exigidas. Tablas y figuras llevan número,
título, fuente y explicación pertinente.

e) Actualizar índices, referencias cruzadas y bibliografía verificable. Renderizar
y revisar la copia final; este archivo Markdown no acredita la revisión visual del
DOCX ni la aprobación de la catedrática.
