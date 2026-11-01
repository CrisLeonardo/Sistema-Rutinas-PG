# Migraciones del esquema de Senda

**Auditoría final (31-10-2026): base anterior ya arrancada con el código nuevo.** Si una base
creada con `create_all` en septiembre (quince tablas, sin `alembic_version`) recibió el arranque de
esta versión, `create_all` le añadió las tablas nuevas vacías pero no las columnas nuevas, y el
acceso falla con `column "version_sesion" does not exist`. En ese caso no sirven `adoptar` ni
`actualizar`: usar `incorporar_base_anterior.py`, que diagnostica sin cambios por omisión, se detiene
ante cualquier diferencia no prevista o tabla nueva con filas, y con `--confirmar` retira las tablas
nuevas vacías, registra `0001`, actualiza hasta `0005` y verifica 0 diferencias en una transacción.
Ensayado en PostgreSQL 16 y SQLite (`tests/test_incorporar_base_anterior.py`). Respaldar y ensayar
sobre una copia restaurada antes de aplicarlo a producción.

```powershell
uv run python incorporar_base_anterior.py
uv run python incorporar_base_anterior.py --confirmar
```

**Fase 7 individual:** no requiere otra migración. Comunidad está desactivada por defecto; conservar la revisión 0005 y sus datos. No ejecutar un descenso de esquema para ocultar grupos. Véase [fase 7](FASE_7_VALIDACION_INDIVIDUAL.md).

**Revisión actual: `0005_comunidad_privada`.** La revisión 0004 añade duración de
sostenes sin convertir repeticiones históricas; la 0005 crea siete tablas sociales.
Aplicar `actualizar` y `comprobar` antes de iniciar esta versión en una base
existente, con respaldo y ensayo previo. No se migró producción. La reversión de
0004 rechaza eliminar unidades cuando hay duraciones registradas; usar un respaldo
compatible. La reversión de 0005 elimina datos sociales y debe limitarse a un
ensayo desechable o restauración planificada. Véase
[FASE_6_COMUNIDAD_PRIVADA.md](FASE_6_COMUNIDAD_PRIVADA.md).

**Antecedente de fase 4: `0003_alimentacion_practica`.** Sobre la revisión 0002 añade
preferencias privadas y una semana calculada por cuenta, sin modificar menús ni
bitácoras históricos. Aplicar `actualizar` explícitamente antes de arrancar el
código de fase 4 sobre una base existente. La actualización poblada, reversión
en pruebas y persistencia se comprobaron en SQLite y PostgreSQL local; véase
[FASE_4_ALIMENTACION_PRACTICA.md](FASE_4_ALIMENTACION_PRACTICA.md). No se migró
producción. `adoptar` exige ahora también estas dos tablas: no sirve para omitir
la migración de una base antigua.

Senda mantiene React, FastAPI, TensorFlow, PostgreSQL, Docker y la publicación
configurada en Render y Supabase. Alembic añade un historial de cambios de tablas
sobre SQLAlchemy. No sustituye el gestor ni crea otro servicio de producción.

La fase 0 incorpora la revisión `0001_esquema_inicial`, que representa las quince
tablas existentes y sus nueve tipos enumerados. La revisión está congelada: no
importa los modelos futuros de la aplicación para reconstruir un esquema antiguo.
No carga usuarios ni catálogos; esas tareas siguen perteneciendo al arranque.

## Configuración y consultas

Ejecutar desde `backend`, con las dependencias instaladas mediante `uv sync
--locked`. La conexión se obtiene de `URL_BASE_DATOS` o del archivo local `.env`,
igual que en el resto del servidor. No escribir credenciales en `alembic.ini`.

```powershell
uv run python gestionar_esquema.py estado
uv run python gestionar_esquema.py comprobar
```

`estado` muestra la revisión registrada o «sin versionar». `comprobar` compara
tablas, columnas, tipos, valores por defecto, índices, restricciones detectables,
claves primarias y valores de enumeraciones PostgreSQL con los modelos actuales.
Devuelve código 1 cuando encuentra diferencias. No escribe datos ni versiones.
La comparación automática no sustituye la revisión de cambios: Alembic tiene
limitaciones para reconocer renombramientos y ciertos tipos de restricciones.

## Base nueva

Antes del primer arranque del servidor, con una base vacía seleccionada:

```powershell
uv run python gestionar_esquema.py actualizar
uv run python gestionar_esquema.py comprobar
```

El primer comando aplica las revisiones hasta la última disponible. Se niega a
actuar sobre una base con tablas sin versión para impedir una incorporación a
ciegas. Después se puede iniciar el servidor con los comandos habituales.

## Base existente creada con el mecanismo anterior

Primero realizar un respaldo y ensayar su restauración en otra base. Preparar una
ventana de mantenimiento para impedir cambios concurrentes mientras se incorpora
el esquema. Seleccionar explícitamente la conexión que corresponda al entorno.

```powershell
uv run python gestionar_esquema.py estado
uv run python gestionar_esquema.py comprobar
uv run python gestionar_esquema.py adoptar
uv run python gestionar_esquema.py estado
```

`adoptar` registra la revisión actual solo cuando la estructura coincide con
todos los modelos actuales (incluida recuperación de acceso). No
altera ni reemplaza tablas de negocio; crea la tabla técnica `alembic_version`.
Si faltan columnas, índices o restricciones, o cambian los valores de una
enumeración, se detiene. No corregir el resultado con `alembic stamp head` sin
investigar las diferencias. Repetir una adopción válida es idempotente.

Para una base antigua que coincide con fase 0 y no tiene versión, ejecutar la
adopción con el código de fase 0, que registra `0001_esquema_inicial`; después
volver a este código y ejecutar `actualizar` y `comprobar`. No usar la adopción
actual para saltarse `0002_recuperacion_acceso` ni registrar a mano una revisión
sin comprobar el esquema. Una base ya versionada en `0001` solo necesita
`actualizar`. La migración 0002 añade la versión de sesión de los usuarios y la
tabla de tokens de recuperación sin borrar los usuarios existentes.

## Cambios posteriores

a) Respaldar y reproducir el esquema actual en pruebas.

b) Modificar el modelo y generar una propuesta con `uv run alembic revision
--autogenerate -m "descripcion_del_cambio"`.

c) Revisar manualmente la propuesta: conservación de datos, renombramientos,
tipos enumerados compartidos, valores iniciales, restricciones y reversibilidad.

d) Probar la actualización sobre una copia poblada y comprobar contenido,
permisos y recorridos. La regresión debe cubrir el comportamiento que cambia.

e) Incluir la revisión en la imagen Docker y aplicarla como una operación única
del despliegue, antes de atender tráfico que dependa del esquema nuevo.

f) Registrar revisión, pruebas, respaldo, limitaciones y cambios de tesis.

Las revisiones pueden tener una operación de reversión, pero eso no garantiza
recuperar datos borrados por un cambio. Ante una pérdida de datos, el procedimiento
de recuperación parte del respaldo probado y de la versión de código compatible.

## Transición del arranque actual

Esta fase no ejecuta migraciones automáticamente en Render, Supabase ni al atender
peticiones. `arranque.crear_esquema` conserva temporalmente `create_all` para que
las instalaciones existentes sigan iniciando. Ese mecanismo crea tablas que falten,
pero no aplica modificaciones a columnas existentes ni mantiene el historial.

Durante las siguientes ampliaciones, ejecutar la migración explícita antes del
servidor. Después de incorporar los entornos existentes se sustituirá la creación
automática del esquema por una verificación de la revisión al arrancar. No desplegar
un cambio de modelo suponiendo que `create_all` lo aplicará.

La imagen Docker incluye `alembic.ini`, `gestionar_esquema.py` y `migraciones/`;
el punto de entrada conserva su comportamiento previo. No se construyó ni publicó
una nueva imagen durante esta fase.

## Pruebas y recuperación local

Los ejemplos siguientes usan exclusivamente datos ficticios. El contenedor está
separado de los que pertenecen a otras aplicaciones. La contraseña visible es solo
de ese ensayo local y no debe reutilizarse en una instalación real.

```powershell
docker run --detach --name senda_fase0_postgres --publish 127.0.0.1:55432:5432 --env POSTGRES_DB=senda_fase0 --env POSTGRES_USER=senda_pruebas --env POSTGRES_PASSWORD=SoloPruebasLocales2026 --label proyecto=senda-fase0 postgres:16-alpine
```

Si ese contenedor ya existe, usar `docker start senda_fase0_postgres` en lugar de
crearlo otra vez. Confirmar disponibilidad con:

```powershell
docker exec senda_fase0_postgres pg_isready --username senda_pruebas --dbname senda_fase0
```

Desde `backend`:

```powershell
$env:URL_POSTGRESQL_PRUEBAS='postgresql+psycopg://senda_pruebas:SoloPruebasLocales2026@127.0.0.1:55432/senda_fase0'
uv run pytest tests/test_migraciones.py -q
uv run python ../operaciones/ensayar_fase0.py
```

Las pruebas usan esquemas nuevos por caso; el ensayo de recuperación crea dos
bases con nombres únicos, realiza un recorrido funcional, genera un volcado con
`pg_dump`, lo restaura con `pg_restore` y compara filas y huellas SHA-256 de las
quince tablas. Después comprueba las secuencias y repite las consultas de la API.
Los motores se cierran al acabar; las bases ficticias se conservan para inspección.

La evidencia se escribe en `operaciones/evidencias/fase0/`, excluida del control
de versiones. No subir respaldos reales ni capturas con datos personales. Para
detener únicamente el contenedor de este ensayo:

```powershell
docker stop senda_fase0_postgres
```

Referencias técnicas: [tutorial oficial de Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
y [alcances y limitaciones de su comparación automática](https://alembic.sqlalchemy.org/en/latest/autogenerate.html).
