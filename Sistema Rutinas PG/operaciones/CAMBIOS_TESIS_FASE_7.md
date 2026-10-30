# Integración académica de la fase 7

30-10-2026. **Ficha de cambios y texto propuesto; el DOCX no fue editado.**
Usar una copia versionada de `Tesis Final/Leonardo Zepeda - Proyecto de Graduacion
II - Entrega 3 (667 pruebas).docx`. Mantener la referencia original y sus cifras
históricas. El avance técnico actual no acredita todavía una entrega académica
final ni una evaluación de campo terminada.

| Parte de la tesis | Cambio que incorporar con la evidencia correspondiente |
|---|---|
| Alcance y requisitos | La entrega actual conserva motivación individual; MEJ-11 y los grupos quedan como ampliación pospuesta por decisión del autor. No renumerar las historias aprobadas ni cambiar la hipótesis por agregar funciones. |
| Diseño y modelo de datos | Documentar duración de plancha, migraciones 0004/0005 como historial y desactivación social. Las tablas conservadas no representan funciones sociales habilitadas. |
| Arquitectura y rendimiento | Misma red y pesos; inferencia de una fila con `training=False`. Admisión asíncrona de cinco solicitudes por proceso sobre el pool existente. Citar fuentes técnicas del informe de fase 7 y describir límites por proceso. |
| Interfaces y manual | Capturas de Mi senda individual; no mostrar invitaciones o grupos como parte de la entrega vigente. Actualizar ayuda, privacidad, recuperación y estados de borrador de ejercicios/recetas. |
| Pruebas | Incorporar cada ejecución con fecha, código, entorno, casos y omisiones. No sumar 667, 759, 792 y los resultados actuales como una sola ejecución. |
| Rendimiento | Incluir ensayos favorables y fallidos. Los 50 usuarios son cuentas simuladas. Exponer primer plan de 7.46 s y estabilidad no acreditada, sin mover los límites para declarar cumplimiento. |
| Evaluación humana y conclusiones | Se mantiene pendiente. No convertir cuentas simuladas, geometría de SVG o perfiles sintéticos en participantes, revisión profesional, adherencia o beneficios clínicos. |
| Anexos y entrega | Añadir manifiesto, pruebas, métricas sin tokens, guion individual y dictámenes cuando existan. Actualizar tablas/figuras/índices en la copia final, renderizar y revisar antes de entregar. |

Texto propuesto para el avance de implementación:

> La entrega evaluada mantiene el seguimiento individual mediante puntos,
> niveles e insignias. La participación con amigos y los grupos privados se
> pospusieron y no están disponibles en la interfaz ni en la API normal. Se
> comprobaron funciones e integridad en un entorno local con PostgreSQL y datos
> ficticios. La optimización de inferencia conservó las respuestas en los casos
> comparados, y se redujo la competencia por recursos con una admisión asíncrona.
> Los ensayos de concurrencia mostraron mejoras, junto con variaciones que
> impiden declarar un cumplimiento estable. La primera generación tras crear
> un proceso superó el tiempo objetivo. Permanecen pendientes la evaluación con
> participantes, el teléfono físico, los dictámenes de contenido y la operación
> del correo real. Estos resultados técnicos no demuestran efectos clínicos ni
> cambios causales en la adherencia.

No usar `validar_hipotesis.py` como evidencia de personas del municipio: genera
perfiles sintéticos y compara métodos definidos por el propio instrumento.
Antes de incorporar sus estadísticas, revisar diseño, supuestos, tratamiento
de empates y justificación de los comparadores. No se ejecutó ni se declaró
validada la hipótesis poblacional en este incremento.
