# Auditoría final de la tesis — 31 de octubre de 2026

Documento auditado: `Leonardo Zepeda - Proyecto de Graduacion II - Entrega 3 (verificada PostgreSQL).docx`
(carpeta Descargas, guardado por el autor el 30-10-2026 a las 16:53, revisión 8). Es el DOCX más
reciente; se comparó párrafo por párrafo con la referencia de 667 pruebas
(`Tesis Final/... Entrega 3 (667 pruebas).docx`, 23-10-2026), que no se modificó.

Esta auditoría no modifica ningún DOCX. Cada punto indica el apartado, lo que dice hoy y lo que
corresponde según el sistema ejecutado el 31-10-2026. Las ubicaciones se dan por apartado porque la
paginación cambia al actualizar campos.

## A. Decisiones que solo puede tomar el autor (con su asesora)

**A-1. Cuál archivo se entrega.** La versión más reciente está en Descargas, no en `Tesis Final`.
Copiarla a `Tesis Final` con un nombre versionado antes de seguir editando.

**A-2. El tono de la versión «verificada PostgreSQL» cambia el resultado de la tesis.** Frente a la de
667 pruebas, reemplaza o elimina 172 párrafos y filas de tabla y agrega o reescribe 187. Entre otros cambios:

- Capítulo VII y Anexo 3: «la hipótesis se acepta» pasó a «La evidencia sostiene una comparación
  técnica … no la aceptación de la hipótesis para la población». La tabla de comprobación marca
  «Pendiente», «En perfiles sintéticos» y «Limitado al experimento» donde antes decía «Se cumple».
- 4.10.3 Factibilidad operativa: la anuencia del gimnasio pasó de «Favorable» a «Pendiente de
  confirmación». Si el gimnasio sí dio su anuencia (la versión anterior lo afirmaba), la nueva
  redacción es inexacta y perjudica la factibilidad. Si no la dio, la anterior era la inexacta.
- Muchos párrafos describen la tesis como bitácora interna: «versión local» (19 veces), «no se volvió
  a comprobar para esta versión», «Evidencia de la entrega anterior», «no se deben sumar estas
  cifras», «el responsable debe iniciar la interfaz y los servicios». Es lenguaje de auditoría, no de
  informe final: un lector concluye que el sistema no está verificado.

Recomendación: conservar la honestidad sobre los límites (perfiles sintéticos, sin participantes,
primera generación lenta en arranque en frío), pero concentrarla en un apartado de limitaciones y
redactar resultados y conclusiones en registro académico. Decidir con la asesora si la hipótesis se
declara aceptada con limitaciones o no comprobada; las dos versiones actuales se contradicen.

## B. Afirmaciones que ya no coinciden con el sistema

**B-1. Publicación y dominio (5.2, 6.1, Anexo 4 §2 y su introducción, Anexo 6 §5, Anexo 3 objetivo b).**
La tesis dice que los incrementos de octubre «no se han publicado» y que la dirección es
`https://rutinas-interfaz.onrender.com`, «no comprobada». Hoy `https://senda-gt.onrender.com`
responde 200, su API `/api/v1/estado` responde «disponible» y sirve el código del commit `a87f1fe`
(textos «Conectando con Senda», recuperación, recetas). La dirección antigua también responde.
Corresponde: indicar `senda-gt.onrender.com` como dirección vigente, la fecha de publicación y los
datos de su certificado. **Antes de afirmarlo, comprobar que el inicio de sesión funciona en
producción** (ver informe del sistema, hallazgo S-1): la base de producción no tiene registradas las
migraciones 0002–0005.

**B-2. Recuperación por correo en producción.** Correcto decir que el envío real está pendiente:
producción responde `recuperacion_habilitada: false` y la pantalla lo explica. En local, con un
servidor SMTP de prueba, el recorrido completo funcionó (correo, enlace de un uso, 15 minutos,
rechazo al reutilizarlo, revocación de la sesión anterior).

**B-3. Cifras de pruebas (6.3 y Anexo 5 §7).** Dice «21 pruebas de entrenamiento y 11 de interacción»
y «Las 32 pruebas de cliente». Al 31-10 el cliente tiene 69 pruebas (36 + 11 + 14 + 8) y, con las
correcciones de esta auditoría, 74. La suite del servidor se reprodujo hoy: 812 aprobadas y 4
omitidas con PostgreSQL 16 (231.97 s), igual que la cifra de la tesis; con las correcciones queda en
825 aprobadas y 4 omitidas. Mantener 667 como ejecución histórica y no sumar.

**B-4. Manual de usuario, textos de pantalla.**

| Apartado | Dice | La aplicación muestra |
|---|---|---|
| Anexo 4 §2 c | toque «Entrar» | botón «Entrar a mi día» |
| Tabla 114 | «Demasiados intentos fallidos. Espere unos minutos antes de volver a intentarlo.» | «Demasiados intentos fallidos. Espere 15 minutos antes de volver a intentarlo.» |
| Tabla 114 | «El servidor tardó demasiado en responder.» | «La consulta tardó demasiado. Vuelva a intentarlo en un momento.» (consultas) o «No recibimos la confirmación a tiempo…» (envíos) |
| Tabla 114 | «No se pudo comunicar con el servidor.» | igual, más «Verifique su conexión e intente de nuevo.» |

**B-5. Manual §6, semana de comidas (después de la corrección S-3).** Añadir: el día en que se prepara
la semana es el Día 1, el botón del día actual dice «· hoy» y el Menú muestra la comida de ese día.
Antes de la corrección el Menú mostraba siempre el Día 1.

**B-6. Interfaces y datos (5.3.3.2, 5.4.3).** La tabla de rutas documenta 40 rutas en 11 enrutadores
como «histórica». La versión publicada expone 50 rutas activas en 12 enrutadores más la de estado
(la API social está apagada) y 25 tablas de negocio más `alembic_version`. Para una entrega final
conviene actualizar la tabla y el diccionario en lugar de remitir a «la documentación local».

**B-7. RN-01 y RE-01.** RN-01 dice «desde los 18 años cumplidos»; RE-01 y el mensaje de la pantalla
dicen «mayores de dieciocho años». El sistema acepta 18 años (comprobado). Unificar la redacción.

## C. Formato y aparato crítico

**C-1. Índice de figuras desactualizado.** Hay 86 figuras en el cuerpo y 85 en el índice; 12 entradas
no coinciden (42, 43, 44, 45, 46, 57, 63, 65, 83, 84, 85 y falta la 86). Ejemplo: el índice dice
«Figura 44. Prototipos de las pantallas principales…» y el cuerpo «Figura 44. Pantalla Hoy de la
versión local de Senda». Solución: clic derecho sobre el índice de figuras → Actualizar campo →
Actualizar toda la tabla; luego lo mismo con el índice general y el de tablas.

**C-2. Referencias sin cita.** Tres referencias quedaron sin cita en el texto porque la reescritura de
6.3.3.1 las retiró: Administración de Alimentos y Medicamentos de los Estados Unidos (2024), Field
(2024) y Servicio Nacional de Salud del Reino Unido (2023). APA exige que toda referencia se cite:
restituir las citas (plan genérico de 2,000 kcal, valores orientativos por sexo y prueba de
Wilcoxon) o retirar las referencias.

**C-3. Comprobado sin observaciones.** Márgenes 2.5/2.5/3/2.5 cm; Normal en Times New Roman 12 con
interlineado 1.5; 120 tablas y 86 figuras numeradas sin saltos ni duplicados y todas con «Fuente»;
305 encabezados coinciden con el índice general; ningún encabezado seguido de otro; 65 referencias,
62 de 2021 o posteriores (las antiguas: plan municipal 2018 y guía de Scrum 2020, la vigente); las
81 citas del texto tienen referencia; sin «¡Error! No se encuentra el origen de la referencia».

## D. Lo que la tesis afirma y sí funciona (comprobado en el sistema el 31-10-2026)

Registro con validación (correo, 8 caracteres con letra y número), acceso y cierre de sesión,
bloqueo tras 8 intentos fallidos durante 15 minutos, revocación del token al cambiar la contraseña,
perfil en cuatro pasos con rechazo de menores (17 rechazado, 18 aceptado) y rangos de peso y
estatura, plan con red neuronal (0.11 % frente a las fórmulas, aviso profesional), menú con
sustitutos equivalentes, semana con recetas, restricciones (alergia al maní y alimento evitado
excluidos en los siete días), cambio de comida recalculado, recetas, lista de compras con marcas
persistentes, rutina por días sin grupos consecutivos, sesión en curso sin barra de navegación,
cronómetro de descanso, puntos e insignias al guardar, bitácora, marcas, 25 guías de ejercicio,
avance semanal con reajuste explicado, Mi senda, evolución, historial de medidas, cuatro informes
personales y ocho del administrador en pantalla, Excel, CSV y PDF, tema claro y oscuro, lesión de
rodilla que retira sentadilla, prensa y zancadas, condición médica que bloquea plan, menú, semana y
rutina, administración de catálogos y cuentas con sus protecciones, diez páginas públicas, video de
30 s, iconos y manifiesto de instalación, y redirección de `/avance/amigos`.
