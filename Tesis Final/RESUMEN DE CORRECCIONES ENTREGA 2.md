# Correcciones a la Entrega 2 de Proyecto de Graduación II

**Archivo revisado por la catedrática:** `Downloads/Leonardo Zepeda - Proyecto de Graduacion II - Entrega 2.docx` (2 comentarios de la Dra. Sheyla Esquivel)
**Archivo corregido:** `Leonardo Zepeda - Proyecto de Graduacion II - Entrega 2 (corregida).docx` y su `.pdf` (194 páginas, 81 tablas, 55 figuras)
**Base:** `Leonardo Zepeda - Proyecto de Graduacion II - Entrega 2.docx`, que queda intacto

---

## 1. Comentarios de la catedrática

| Apartado | Comentario | Qué se hizo |
|---|---|---|
| 5.3.3.1 Interfaces internas | «Agregue diagrama» | Figura 33, diagrama de componentes con las 9 interfaces de la Tabla 56, con párrafo antes y explicación debajo |
| 5.3.3.2 Interfaces externas | «Agregue diagrama» | Figura 34, las 37 rutas agrupadas por nivel de acceso (3 públicas, 23 autenticadas, 11 de administrador) y los dos actores, con párrafo antes y explicación debajo |

## 2. Rúbrica de la Entrega 2

| Aspecto | Estado |
|---|---|
| Capítulos anteriores corregidos | Sí, ver sección 3 |
| Índices actualizados | Sí, recalculados en Word (general, tablas y figuras) |
| Puntualidad y estética | Portada corregida; formato uniforme |
| Ortografía y redacción | Revisadas; ver sección 3 |
| Capítulo V completo | Sí, los 38 apartados del guion Scrum |
| Citas según APA | Orden alfabético dentro de cada cita, cursivas en las referencias, 8 referencias con datos erróneos corregidas o retiradas |
| Envío a la plataforma y a correos | **Le toca a usted** |
| Diagramas con cita | Las 55 figuras llevan «Fuente:» |
| Diagrama de arquitectura del sistema | Figuras 29, 30 y 31 |
| Explicación con cada diagrama | Sí; se agregaron las que faltaban (Figuras 1, 24, 26, 27 y 40) |
| Diagrama de base de datos | Figuras 36, 37 y 38 |
| Diagramas UML | Clases, componentes, casos de uso, actividades, secuencia y **estados** (nuevo) |
| Diseño de la seguridad | 5.6 con tres tablas y **dos diagramas nuevos**: Figura 42 (autenticación y autorización) y Figura 43 (estados de la sesión) |
| Diagrama del negocio antes | Figura 48 |
| Diagrama del negocio después | Figura 49 |

## 3. Otras correcciones de la auditoría

**Portada:** decía «ENTREGA 1» y «JULIO DE 2026». Ahora dice «ENTREGA 2» y «SEPTIEMBRE DE 2026».

**Figuras que contradecían el texto:**
- Las Figuras 26 y 28 decían **MySQL**. El sistema usa PostgreSQL 16. Se rehicieron.
- La Figura 27 (MVC) tenía dos rótulos encimados. La 25 tenía la flecha de retroalimentación sin llegar a la caja. Se rehicieron las dos.
- La Figura 32 decía «guardarraíles» y dibujaba dependencias del motor hacia la base de datos, lo que contradice el texto. Se corrigió.
- La Figura 23 mostraba 3 entradas y 1 salida. La red real tiene 8 entradas y 5 salidas (`motor/conjunto_datos.py`). Se rehizo, y se corrigió el texto del 2.1.2 y la Tabla 56, que decían «seis variables».

**Encabezados sin párrafo explicativo** (la observación que más punteo ha costado): 1.5.2, 1.6.4, 1.9.1, 1.9.2, 4.2.3, Anexos y las 21 gráficas del 1.13.5 y 1.13.6.

**Redacción y datos:**
- «A continuación se» pasa a «A continuación, se» (2 casos; es la coma que la catedrática ya había marcado).
- 4.10.2 decía que el ahorro «supera en más de dieciocho veces» la inversión. Q480,000 / Q26,695 = 17.98, así que la afirmación era falsa. Ahora dice «entre dieciocho y treinta y seis veces».

**Citas y referencias** (todo se verificó en línea):

| Referencia | Problema | Corrección |
|---|---|---|
| LeCun et al. (2021), *Nature Reviews Methods Primers* | El artículo no existe con esos datos | Bengio, LeCun y Hinton (2021), *Communications of the ACM*, 64(7) |
| Topol (2023), *Nature Medicine* 29(1) | Es de 2019, vol. 25 | Topol (2023), *Science*, 381(6663) |
| Suchomel et al. (2022) | El DOI es del artículo de 2016 | Suchomel et al. (2021), *Sports Medicine*, 51(10) |
| Meskó et al. (2023) | Es de 2017 y de otra revista | OMS (2021b), *Estrategia mundial sobre salud digital* |
| Bates et al. (2021), JAMA | No se encontró el artículo | OMS (2021b), o el propio trabajo de campo |
| Jeukendrup (2022), Stear y Burke (2022), Thomas et al. (2021) | Son de 2014, 2013 y 2016 | Se retiraron; esas afirmaciones quedan con Burke y Deakin (2022) |
| Pérez-Escamilla et al. (2022) | No se encontró el artículo | OPS (2021) |
| García y López (2023) | Sin datos verificables | Russell y Norvig (2021) |
| Rojanaphan (2024) | Es un preprint de SSRN, no de *Nutrients* | Referencia corregida |
| Schmidhuber (2022) | Es de arXiv, no de *IEEE TNNLS* | Referencia corregida |
| Node.js citado a Meta, Postman a Ramírez, VS Code a Sommerville, Supabase a Elmasri | Autor equivocado | OpenJS Foundation, Postman, Microsoft y Supabase (2025) |
| Figura 1 | «mapa satelital de acceso público» | Google (2026), con su referencia |

## 4. Ajustes finales (22 de septiembre de 2026)

- El apartado «Título» del Capítulo I ahora usa el título de la portada: «…rutinas de entrenamiento en El Progreso, Jutiapa».
- El gimnasio aparece en todo el documento como «Fama’s Fitness Club», el nombre con que figura en Google Maps (Figura 1). Se cambió en 11 lugares: Figura 1, 1.6.4, 4.1.3, 4.1.4, 4.10.3, 5.8.1, la Tabla 78 y el índice de figuras.
- Las referencias marcadas abajo como dudosas se dejaron como estaban, por decisión del autor.

## 5. Lo que quedaba por decidir o verificar (antes de los ajustes finales)

1. **El título no coincide.** La portada dice «…EN EL PROGRESO, JUTIAPA». El apartado «Título» del Capítulo I dice «…para personas en Jutiapa». Este último es el aprobado en PG1. Confirme cuál es el oficial y úselo igual en los dos lugares.
2. **Referencias con edición o año dudosos:**
   - Fowler, *Patterns of enterprise application architecture*: no existe una 2.ª edición de 2023; el libro es de 2002.
   - Revise también la edición y el año de Hernández-Sampieri (7.ª), Elmasri (8.ª), Kendall (10.ª), Fleck (5.ª), Haff (4.ª, 2022), Helms (2023), Israetel (2022), Arias (8.ª) y Bompa (2022).
   - Revise que abran los enlaces del INE, el MSPAS, la SIT y los repositorios de Ribes Barberis, Rivera Valdivia y Monroy Rodríguez.
   - No se cambiaron porque no pude confirmarlos ni desmentirlos.
3. **Nombre del gimnasio:** en Google Maps aparece como «Fama's Fitness Club». En la tesis figura como «Gimnasio FAMAS».
4. **Envío a la plataforma y a los correos:** le corresponde a usted.
