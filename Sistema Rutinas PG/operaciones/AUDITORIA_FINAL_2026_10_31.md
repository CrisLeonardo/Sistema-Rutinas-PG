# Auditoría final del sistema — 31 de octubre de 2026

Rama: `auditoria-final-sistema`, creada desde `main` en `a87f1fe` (igual a `origin/main`).
No se hizo push, publicación ni migración de producción. No se usaron credenciales reales.

## Cómo se comprobó

- Suite del servidor antes de cambiar nada: con SQLite, 795 aprobadas y 21 omitidas; con PostgreSQL
  16 local desechable (`URL_POSTGRESQL_PRUEBAS`), **812 aprobadas y 4 omitidas, 0 fallos**, igual que
  la cifra declarada en la tesis.
- Cliente: 69 pruebas (36 entrenamiento, 11 interacción, 14 conexión, 8 experiencia), construcción y
  verificador correctos.
- Esquema: base nueva con `gestionar_esquema.py actualizar` → `0005_comunidad_privada`, `comprobar`
  → 0 diferencias, tal como indica el Manual de Instalación.
- Recorrido completo en el navegador contra una API local (SQLite aislada, cuentas ficticias y un
  servidor SMTP de prueba para la recuperación), siguiendo el Manual de Usuario de la tesis: registro,
  acceso, perfil en cuatro pasos, plan, menú, sustitutos, semana, restricciones, cambio de comida,
  recetas, compras, rutina, sesión, bitácora, marcas, 25 guías, avance, Mi senda, evolución,
  medidas, informes, ajustes, cambio y recuperación de contraseña, administración, sitio público.
- API: lesión y condición médica, bloqueo de intentos, revocación de token, permisos, los 8
  informes del administrador en pantalla, CSV, Excel y PDF.
- Producción: solo lecturas públicas (`/`, `/api/v1/estado`, `opciones-publicas`, recursos).

## Hallazgos

| Id | Gravedad | Hallazgo | Estado |
|---|---|---|---|
| S-1 | Alta | Producción ejecuta el código de `a87f1fe`, que lee `usuarios.version_sesion` (revisión 0002) y las columnas de duración (0004). Los informes de fases 0–7 dicen que la base de producción nunca se migró, y el arranque solo usa `create_all`, que crea tablas pero no agrega columnas. Si la base es la de septiembre, el acceso y el registro fallarían. | **Pendiente de verificar por el autor** |
| S-2 | Media | Zona horaria. Las marcas se guardan en UTC y se publicaban sin zona: el navegador mostraba seis horas de más («Plan generado el 1 de noviembre a las 12:26 a. m.» el 31 de octubre a las 18:26). En Render (UTC) una sesión registrada después de las 18:00 quedaba con la fecha del día siguiente y se otorgaba «Antes del sol» a quien entrenaba de noche (se reprodujo en local). El PDF mezclaba «Generado el 31/10/2026 18:35» con «01/11/2026». | Corregido |
| S-3 | Media | Con una semana preparada, «Qué comer hoy» y el panel mostraban siempre el Día 1, fuera cual fuera el día. | Corregido |
| S-4 | Media | Los errores de validación estándar llegaban en inglés y sin nombrar el dato: «Input should be less than or equal to 100». Además se podía marcar como hecha una serie con 1212 repeticiones (el volumen subía a 48,480 kg) y el error aparecía solo al guardar. Una dirección `/entrenar/<texto>` mostraba «Input should be a valid integer…». | Corregido |
| S-5 | Baja | El catálogo aceptaba alimentos imposibles: 90 g de proteína + 90 g de carbohidrato por 100 g con 26 kcal. El esquema ya tenía la tolerancia y la fórmula de Atwater, sin usarlas. | Corregido |
| S-6 | Baja | Plurales: «1 sesiones registradas», «1 sesiones en total · 1 semanas registradas». | Corregido |
| S-7 | Baja | Producción sirve `manifest.webmanifest` como `binary/octet-stream` y no hay `sitemap.xml` (responde la portada). Las rutas `/prototipo/fase-1` y `/prototipo/fase-3` son públicas aunque no están enlazadas. | Abierto |
| S-8 | Info | El sitio público y la recuperación tutean («Recupera tu acceso»); la aplicación trata de usted («Entre para ver qué le toca hoy»). | Abierto, decisión de estilo |
| S-9 | Info | Tras declarar una alergia, la semana anterior se invalida y el Menú pide preparar otra; no se muestra un menú con el alérgeno. Correcto, aunque obliga a un paso más. | Sin cambio |

Limitaciones conocidas que siguen abiertas, ya documentadas en fase 7 y en la tesis revisada:
primera generación desde proceso nuevo de 6.29–7.46 s (la prueba pide el plan mientras TensorFlow
aún carga; los siguientes tardan 0.04 s), estabilidad bajo 50 usuarios no acreditada.

## Correcciones de esta rama

- `app/nucleo/tiempo.py` (nuevo): hora de Guatemala (UTC−6 fijo, sin horario de verano desde 2006),
  `hoy_local()`, `a_hora_local()` y el tipo `MarcaUTC`, que publica con «+00:00» las marcas guardadas
  en UTC. Se aplicó a plan, menú, compras, rutina, perfil, cuenta, insignias e hitos; el registro de
  avance conserva su fecha local.
- Servicios y validadores usan `hoy_local()` en lugar de `date.today()`; «Antes del sol» usa la hora
  local; los informes convierten fechas UTC y fechan «Generado el» en hora local.
- La semana guarda `preparada_el`; el Menú y el panel usan `dia_de_hoy()`; la pantalla Semana abre en
  el día de hoy y lo rotula «· hoy».
- `frontend/src/servicios/validacion.mjs` (nuevo): mensajes en español según el tipo de error de
  Pydantic, con el nombre del dato y la serie. La sesión revisa repeticiones, segundos y peso antes de
  marcar una serie, con los mismos límites del servidor.
- `formatos.js`: `aFecha()` lee «AAAA-MM-DD» como día local.
- Catálogo: macronutrientes que sumen más de 100 g o energía que no concuerde con Atwater (tolerancia
  de 25 kcal o 20 %) se rechazan con un mensaje en español; los 36 alimentos iniciales siguen válidos.
- `backend/incorporar_base_anterior.py` (nuevo, incluido en la imagen Docker): incorpora a Alembic una
  base creada con `create_all` que ya recibió el código nuevo (hallazgo S-1).
- Pruebas nuevas: `backend/tests/test_hora_local.py` (7), `backend/tests/test_incorporar_base_anterior.py`
  (3 en SQLite y 3 en PostgreSQL) y `frontend/operaciones/auditoria.test.mjs` (5,
  `npm run test:auditoria`). Las pruebas que calculaban «hoy» usan `hoy_local()`.

## Resultado después de las correcciones

- Servidor con PostgreSQL 16: **825 aprobadas, 4 omitidas y 0 fallos** (252.07 s): las 812 previas,
  7 de hora local y 6 del guion de incorporación. Las 4 omitidas son casos de SQLite que no aplican.
- Cliente: 74 aprobadas (36 + 11 + 14 + 8 + 5); construcción y verificador correctos.
- En el navegador: «Plan generado el 31 de octubre de 2026 a las 6:35 p. m.», «Miembro desde el 31
  de octubre», medidas del «31 oct», semana con «Día 1 · hoy», serie con 1212 repeticiones rechazada
  con «Serie 1 de Remo con barra: escriba entre 0 y 100 repeticiones.» y ruta inválida con
  «Sesión: debe ser un número entero.».

## Qué falta para la entrega

1. **S-1:** entrar a `https://senda-gt.onrender.com` con una cuenta propia y generar un plan. Se
   ensayó el caso probable en PostgreSQL 16: base de septiembre más el arranque de `a87f1fe` deja 25
   tablas, 4 columnas faltantes y el acceso falla con `column "version_sesion" does not exist`. Si
   producción falla así, respaldar Supabase, restaurar el respaldo en otra base, ejecutar ahí
   `incorporar_base_anterior.py` (diagnóstico) y `--confirmar`, comprobar, y solo después repetir en
   producción. El guion conserva las cuentas y se detiene si encuentra algo distinto a ese caso.
2. Decidir si se publica esta rama (`main` se despliega solo en Render) y, si se publica, repetir la
   comprobación de producción.
3. Decisiones del autor del 31-10-2026, ya aplicadas en esta rama: Gmail, teléfono físico y
   participantes quedan fuera del alcance (el enlace «Olvidé mi contraseña» solo aparece si hay un
   correo configurado). La revisión profesional —un nutricionista para las 18 recetas y la
   composición del catálogo; un entrenador del Gimnasio FAMAS para las 25 guías y la plancha de
   20–30 s— y los precios de los mercados de El Progreso, ambos de octubre de 2026, se registran en
   `backend/app/nucleo/revision.py` y en las pantallas, sin nombres de revisores. Sin recuperación
   por correo, una persona que olvide su contraseña no tiene vía automática para recuperarla.

## Cierre y publicación (31-10-2026, autorizado por el autor: «haz todo»)

- **Contraseña temporal del administrador** (`POST /api/v1/usuarios/{id}/contrasena-temporal`,
  botón en Administración → Cuentas). Sustituye a la recuperación por correo descartada: genera 12
  caracteres que cumplen las reglas del registro, se muestra una vez, cierra las sesiones de esa
  cuenta y no se aplica a la cuenta propia. Pruebas: `tests/test_contrasena_temporal.py`.
- **Incorporación automática y protegida al arrancar** (`app/nucleo/incorporacion.py`, llamada desde
  `arranque.incorporar_base_anterior`). Solo actúa si la base no tiene versión y le faltan las
  columnas nuevas; se detiene ante cualquier otra diferencia o si alguna tabla nueva tiene filas.
  Ensayada en PostgreSQL 16 y SQLite, incluido el arranque completo.
- **`/api/v1/estado` publica `esquema`** («al_dia», «incompleto» o «sin_comprobar»), para verificar
  un despliegue sin credenciales. No revela tablas ni columnas.
- Suite del servidor con PostgreSQL 16: **829 aprobadas, 4 omitidas, 0 fallos**. Cliente: 74.
