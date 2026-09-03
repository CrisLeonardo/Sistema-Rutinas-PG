# Cambios en la tesis por el cambio de pila de despliegue

**Archivo generado:** `Leonardo Zepeda - Proyecto de Graduacion II - Entrega 1 (pila de despliegue actualizada).docx`
**Archivo de partida (intacto):** `Leonardo Zepeda - Proyecto de Graduacion II - Entrega 1 (corregido).docx`
**Fecha:** 3 de septiembre de 2026

El sistema se despliega sobre **Render** —la aplicación— y **Supabase** —la base
de datos—. Este documento registra qué hubo que cambiar en la tesis por esa
decisión, y, tan importante como eso, qué **no** hubo que cambiar.

---

## 1. Lo que no cambió: el alojamiento

La tesis **nunca nombra un proveedor de alojamiento**. Lo describe siempre en
términos genéricos, y Render satisface la descripción al pie de la letra:

| Apartado | Texto original | ¿Render lo cumple? |
|---|---|---|
| 3.8 Despliegue | «sobre un servidor en la nube con dominio propio y certificado de seguridad» | Sí. Dominio propio y certificado emitido y renovado por la plataforma |
| 4.5.6 Restricciones técnicas | «el sistema debe operar sobre un servidor en la nube de bajo costo» | Sí. US$ 7.25 mensuales |
| 4.10.1 Factibilidad técnica | «un servicio de alojamiento en la nube de costo reducido, cuya capacidad cubre holgadamente los cincuenta usuarios concurrentes» | Sí. Verificado con la prueba de carga |
| Tabla 13, presupuesto | «Alojamiento en la nube… Q900.00» por seis meses | Sí. El costo real son Q342.00 |

**No se modificó ninguno de esos apartados por razón del proveedor.** El único
cambio en 3.8 fue añadir una oración que nombra la plataforma, para que el
documento describa con precisión el sistema entregado.

## 2. Lo que sí cambió: el gestor de base de datos

Supabase provee **PostgreSQL**, y la tesis nombraba **MySQL** en nueve lugares.
Todos fueron corregidos.

| # | Ubicación | Antes | Después |
|---|---|---|---|
| 1 | Índice general, pág. 73 | 3.4.1 Gestor MySQL | 3.4.1 Gestor PostgreSQL |
| 2 | Índice general, pág. 74 | 3.4.2 Herramienta MySQL Workbench | 3.4.2 Plataforma Supabase |
| 3 | Párrafo de entrada del Capítulo III | «el gestor MySQL para la persistencia» | «el gestor PostgreSQL para la persistencia» |
| 4 | Título 3.4.1 | Gestor MySQL | Gestor PostgreSQL |
| 5 | 3.4.1, párrafo de definición | Definición de MySQL | Definición de PostgreSQL, con las mismas citas |
| 6 | 3.4.1, párrafo de justificación | Justificación de MySQL | Justificación de PostgreSQL, más la razón de despliegue |
| 7 | 3.4.1, párrafo de características | Índices, claves foráneas, permisos | Lo mismo, más los tipos de datos propios |
| 8 | Título 3.4.2 | Herramienta MySQL Workbench | Plataforma Supabase |
| 9 | Tabla 7, fila Persistencia | MySQL y MySQL Workbench | PostgreSQL y la plataforma Supabase |

**Detalle del apartado 3.4.2.** Era el que describía MySQL Workbench: la
herramienta visual con que se diseña y administra el esquema. Supabase cumple
ese mismo papel con su consola web, de modo que el apartado conserva su función
dentro del capítulo —la herramienta de administración de la base de datos— y sus
tres párrafos, ahora referidos a la plataforma que efectivamente se usa. Se
añade además que la conexión con la base de datos va cifrada, que es una
exigencia del requerimiento 4.5.1 y una consecuencia real de que la base ya no
viva en el mismo servidor que la aplicación.

**Detalle del apartado 3.4.1, párrafo de justificación.** Se conservó íntegra la
argumentación original —rendimiento, soporte, integridad transaccional del
historial biométrico— y se le sumó la razón que motivó el cambio: los
proveedores de alojamiento administrado ofrecen PostgreSQL en su nivel gratuito,
de modo que la persistencia no consume presupuesto. Esto conecta el apartado
3.4.1 con la restricción de costo del 4.5.6.

## 3. Referencias añadidas

Tres, insertadas en su lugar alfabético y con la sangría francesa del resto de
la lista. El total pasa de 54 a 57.

- Grupo Global de Desarrollo de PostgreSQL. (2025). *Documentación oficial de PostgreSQL 16*. https://www.postgresql.org/docs/16/
- Render Services Inc. (2025). *Documentación oficial de Render*. https://render.com/docs
- Supabase Inc. (2025). *Documentación oficial de Supabase*. https://supabase.com/docs

El estilo sigue el de las referencias de documentación oficial que ya había en
la lista —Fundación Mozilla (2025), Software Freedom Conservancy (2024), Meta
Open Source (2025), Ramírez (2023)—, de modo que no introduce un tipo de fuente
nuevo en la bibliografía.

## 4. Lo que hay que hacer al abrir el documento en Word

**Actualizar el índice general.** Las dos entradas del apartado 3.4 se
corrigieron también en el texto que el índice tiene almacenado, de modo que se
ven bien al abrir el archivo. Aun así, conviene regenerarlo para que los números
de página queden exactos después del cambio de extensión:

1. Haga clic dentro del índice general.
2. Pulse **F9**.
3. Elija **Actualizar toda la tabla**.

El capítulo creció unas pocas líneas, de modo que la paginación de los apartados
posteriores puede correrse. Los índices de tablas y de figuras no se tocaron.

## 5. Pendiente que queda en sus manos: la Tabla 13

El presupuesto **no se modificó**, y conviene decir por qué. La Tabla 13 fue
revisada por la Dra. Sheyla Esquivel, que pidió expresamente agregarle el rubro
de mano de obra; tocarla de nuevo tiene un costo que no es solo el de la fila
que se cambia.

Estos son los números reales, por si decide ajustarla:

| Rubro | Presupuestado | Costo real | Diferencia |
|---|---|---|---|
| Alojamiento en la nube, seis meses | Q900.00 | Q342.00 | −Q558.00 |
| Dominio y certificado, anual | Q250.00 | ≈ Q95.00 (el certificado lo emite Render sin costo) | −Q155.00 |

Si los ajusta, arrastran también la fila de **Imprevistos** —que es el 10 % de
los costos desembolsables—, el **total** de la tabla, y el párrafo del apartado
4.10.2 que cita las cifras de Q2,695.00, Q26,695.00 y «Q1,150.00 semestrales».

**Argumento para dejarla como está:** un presupuesto es una estimación previa, y
la tabla dice «Costo estimado». Ejecutar por debajo de lo presupuestado no
contradice el documento; refuerza la afirmación de factibilidad económica del
apartado 4.10.2. Es su decisión.
