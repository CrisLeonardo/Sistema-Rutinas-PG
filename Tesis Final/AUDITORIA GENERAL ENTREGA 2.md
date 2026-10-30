# Auditoría general de la Entrega 2 (25 de septiembre de 2026)

**Archivo revisado:** `Leonardo Zepeda - Proyecto de Graduacion II - Entrega 2 (corregida).docx` (queda intacto)
**Archivo resultante:** `Leonardo Zepeda - Proyecto de Graduacion II - Entrega 2 (final).docx` y su `.pdf` (199 páginas, 83 tablas, 55 figuras)

Se leyó el documento completo (portada, índices, Introducción, Capítulos I a V, referencias y anexos), se recalcularon las cifras de la encuesta, se cruzaron las 56 citas con las 56 referencias y se cotejó el Capítulo V contra el código actual del repositorio.

## 1. Rúbrica

| Aspecto | Estado |
|---|---|
| Capítulos anteriores corregidos | Sí; se corrigieron 3 datos mal citados en el Cap. I y 6 encabezados sin párrafo explicativo |
| Índices actualizados | Sí; general, de tablas (83) y de figuras (55) recalculados en Word |
| Puntualidad y estética | Columnas del diccionario de datos ensanchadas: ya no se parten «Nulo», «Clave», «Secuencia», «principiante» ni «numeric(5,2)» |
| Ortografía y redacción | Sin dobles espacios, comillas rectas ni palabras repetidas; el texto nuevo no agrega marcas del corrector salvo el apellido Morrow |
| Capítulo V completo | Sí, y ahora coincide con el código actual (ver sección 3) |
| Citas según APA | 56 citas ↔ 56 referencias, en orden alfabético y con cursivas; se corrigió la autoría de Krause |
| Envío a la plataforma y a correos | **Le toca a usted** |
| Diagramas con cita | Las 55 figuras llevan «Fuente:» |
| Explicación con cada diagrama | Sí; se agregó la explicación de las 6 figuras del Anexo 2 |
| Arquitectura, base de datos, UML, seguridad, negocio antes y después | Presentes (Figuras 29–31, 36–38, 35 y 44–46, 42–43, 48 y 49) |

## 2. Errores corregidos en capítulos anteriores

| Lugar | Decía | Ahora |
|---|---|---|
| 1.13.5.10 | «Únicamente el 16.6 % la recibe de forma regular» | 9.5 % de forma regular (Tabla 13); 16.6 % en una o dos ocasiones |
| 1.13.5.14 | «solo el 5.3 % se mostró reacio» | 6.5 % (5.3 % + 1.2 %) |
| 1.13.5.18 | funciones adicionales «con prioridad media» | «con prioridad baja», como dice 4.6.2 |
| 1.13.4 | el modelo «antecede a la construcción de los módulos» | coherente con la Tabla 3 (la plataforma empieza en el mes 3; el modelo se entrena en los meses 4 y 5) |
| 1.3.2, 1.5.2, 1.6.4, 1.9.1, 1.9.2, 4.2.3 | el encabezado pasaba directo a la lista o a la tabla | párrafo explicativo antes |
| 5.8.2 | «cuatro fuentes» | «cinco fuentes» (la Tabla 81 tiene cinco) |
| Referencias | «publicaciones de los últimos cinco años» | se exceptúa la Guía de Scrum (2020), que es la versión vigente |
| Referencia Krause | Mahan y Raymond (2021) | Raymond y Morrow (2021): son las editoras de la 15.ª edición (verificado en Elsevier) |
| Figura 53 | «Sección II… preguntas 7 y 8» | «Secciones II y III… preguntas 7 a 9» (la captura incluye la pregunta 9) |
| 5.7.1 | 12 casos de uso en la Figura 44 frente a 11 en la Tabla 41, sin explicación | párrafo que explica cómo el diseño agrupó y separó los casos |

## 3. Capítulo V frente al código

El commit `f81d6ea` (posterior a la tesis) quitó la mascota y agregó el historial de lesiones y las condiciones médicas. El capítulo afirma que todo coincide con el sistema en operación, así que se actualizó:

- **Tablas nuevas:** 5.4.3.3 *Lesiones del perfil* (Tabla 61) y 5.4.3.4 *Condiciones del perfil* (Tabla 62); los subapartados siguientes pasan a 5.4.3.5–5.4.3.15. El esquema ahora tiene **15 tablas** (antes 13).
- **Figura 38** redibujada con `lesiones_perfil` y `condiciones_perfil`; **Figura 32** con el módulo `lesiones`, 14 componentes y 15 entidades; **Figura 40** sin mascota (anillo de nivel e insignias «6 de 18»).
- Tabla 55 (+ `motor.lesiones`, sin mascota), Tabla 58, 5.3.4, 5.4.2, 5.4.3, 5.5.2 y la síntesis final (19 módulos, 15 entidades).
- Tabla 77: excepción por condición médica (restricción RE-02) y rutina que omite los ejercicios que cargan una zona lesionada.

## 4. Rúbrica de la Entrega 1 (26 de septiembre de 2026)

Documento resultante: 205 páginas, 84 tablas, 60 figuras. Los 30 comentarios de la catedrática en la Entrega 1 siguen atendidos.

| Renglón con punteo perdido | Qué se hizo |
|---|---|
| Capítulo 1 completo/corregido (0/2) | Las viñetas «−» de 1.6.3 y 1.6.4 pasan a incisos a), b)…, como exige la guía del curso |
| Estética (0.5/1) | Encabezados de 24 tablas ensanchados («Código», «Probabilidad», «Impacto» ya no se parten); las 84 «Fuente» de tabla alineadas igual; los dos párrafos de más de 170 palabras, divididos; la Figura 31 recortada |
| Aspectos completos del capítulo (1.5/2) | Los apartados del Cap. IV siguen la guía Scrum; ahora cada proceso del análisis tiene su diagrama |
| Tablas y figuras con citas (0.5/1) | Todas llevan «Fuente:» |
| Factibilidades (1/2) | Se mantienen las tablas de requisitos, presupuesto y factibilidad operativa |
| Riesgos evaluados correctamente (1/2) | Nueva Tabla 47 con el nivel de cada riesgo (probabilidad × impacto) y Figura 33, la matriz de probabilidad e impacto; la mitigación va después de la evaluación |
| No posee diagramas (0.5/1) | Cinco diagramas nuevos en el Cap. IV: contexto (Fig. 29), dependencias de la pila (Fig. 30), flujo del proceso (Fig. 31), casos de uso (Fig. 32) y matriz de riesgos (Fig. 33) |

Además, el idioma por defecto del documento era inglés, así que Word subrayaba palabras en español; ahora es español (es-419) y las marcas del corrector bajan de 1 074 a 447 (nombres propios, apellidos y términos técnicos).

Las figuras del Capítulo V se renumeran solas: +5 respecto de la sección 3 (por ejemplo, la entidad-relación de la segunda parte es ahora la Figura 43).

## 5. Referencias verificadas una por una (26 de septiembre de 2026)

Se comprobó cada referencia en la editorial, el repositorio o Crossref. Como la rúbrica de Proyecto de Graduación I ya penalizó las fuentes de más de cinco años, las obras cuya edición real es antigua se sustituyeron por fuentes reales y recientes que respaldan lo mismo. El resultado son 49 referencias, todas citadas, y 49 citas, todas con su referencia, en orden alfabético.

| Referencia anterior | Problema | Ahora |
|---|---|---|
| Ribes Barberis (2024), primer antecedente | No existe en RiuNet; el enlace no corresponde | Bueno Fuentes (2024), trabajo de fin de grado real de la UPV sobre una aplicación de gestión de entrenamientos de gimnasio; se reescribió el antecedente según su resumen |
| Rivera Valdivia (2022), «tesis de la Universidad de Costa Rica» | Es un artículo de revista de la Universidad Nacional del Altiplano (Perú) y es una revisión documental | Referencia de artículo con su DOI; antecedente reescrito según el artículo |
| Monroy Rodríguez (2024), «UNAM» | La tesis es del CINVESTAV del IPN | Institución y enlace corregidos; el antecedente se ajustó al resumen real de la tesis |
| Rojanaphan (2024) y Tsolakidis et al. (2024) | El texto atribuía resultados que los resúmenes no dicen | Descripciones ajustadas a los resúmenes (Tsolakidis: 67 estudios, 43 de sistemas de recomendación y 17 de recolección de datos) |
| Instituto Nacional de Estadística (2024), «Estudio sociodemográfico… de Jutiapa» | Ese documento no existe | INE (2025), *Perfil estadístico: Jutiapa* (ingreso laboral de Q2,175.10, participación laboral de 53.8 %, 80.7 % de hogares con internet o celular) |
| Datos del municipio en 1.6.3 | No coincidían con ninguna fuente: 68 km², 146 km, 22,400 habitantes y una «PEA del 38 %» que en realidad es la población en edad escolar | Datos del Plan de Desarrollo Municipal de El Progreso (Concejo Municipal, 2018): 60 km², 128 km, 11 km, 19,252 habitantes (proyección del INE para 2017) |
| MSPAS (2022), SIT (2023) y OPS (2021) | Informe y boletín no localizables; el panorama de 2021 lo publican cinco organismos, no solo la OPS | FAO et al. (2021), el panorama real, y el INE (2025); las afirmaciones sobre cargas y lesiones pasan a Burke et al. (2021) y Suchomel et al. (2021) |
| Fowler (2023), 2.ª ed. | Solo existe la edición de 2002 | Richards y Ford (2025), *Fundamentals of software architecture*, 2.ª ed. |
| Elmasri y Navathe (2023), 8.ª ed.; Silberschatz et al. (2021), 7.ª ed. en español | No hay 8.ª ed. (la 7.ª es de 2016); la 7.ª de Silberschatz es de 2020 y no está traducida | Coronel y Morris (2023), *Database systems*, 14.ª ed. |
| Arias (2022), 8.ª ed.; Hernández-Sampieri et al. (2023), 7.ª ed. | No hay 8.ª ed. de Arias (la 7.ª es de 2016); la de Hernández-Sampieri no corresponde | Hernández-Sampieri y Mendoza Torres (2023), *Las rutas cuantitativa, cualitativa y mixta*, 2.ª ed. |
| Haff y Triplett (2022), Fleck y Kraemer (2022), Helms et al. (2023), Israetel et al. (2022) | Ediciones reales de 2016, 2014, 2019 y 2020 | Sus citas pasan a Suchomel et al. (2021), Zatsiorsky et al. (2021), Schoenfeld (2021) y Bompa y Buzzichelli (2022) |
| Kendall y Kendall (2022), 10.ª ed. | La 10.ª es de 2019 | 11.ª ed. (2024) |
| Burke y Deakin (2022) | Es de 2021 y tiene una tercera editora | Burke, Deakin y Minehan (Eds.) (2021) → «Burke et al., 2021» |
| Williams y Rawson (2023), 13.ª ed. en español | La 13.ª es de Rawson, Branch y Stephenson (2024) y no está traducida | Rawson et al. (2024) |
| Tanenbaum y Wetherall (2021) | La 6.ª ed. agrega a Feamster | Tanenbaum et al. (2021) |
| Bompa y Buzzichelli (2022), Ediciones Tutor | Esa edición en español es de Paidotribo, 2016 | *Periodization of strength training for sports*, 4.ª ed., Human Kinetics, 2022 |
| Russell y Norvig, Schoenfeld y Sommerville «en español» | No hay traducción de esas ediciones | Título original con traducción entre corchetes; año sin cambio |

Géron (2023) se deja igual: la 3.ª edición salió en octubre de 2022 con derechos de 2023. La nota de las referencias ahora exceptúa, además de la guía de Scrum, el plan municipal, que es el instrumento oficial vigente hasta 2032.

## 6. Pendiente de usted

- Revisar que los antecedentes reescritos (1.1) y los datos del municipio (1.6.3) le parezcan bien redactados.
- Abrir el `.docx` en Word, aceptar si pregunta por actualizar campos, y enviarlo a la plataforma y a los correos.
