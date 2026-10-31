# Despliegue en producción

**Estado local de fase 7 (30-10-2026):** mantener `COMUNIDAD_HABILITADA=false` y `SOLICITUDES_ACTIVAS_BD=5`. No se desplegó este incremento ni se migró producción. Consultar [validación individual](operaciones/FASE_7_VALIDACION_INDIVIDUAL.md): carga de 50 usuarios sin estabilidad acreditada y primera generación de 7.46 s. Conservar esquema 0005 aunque la comunidad esté apagada.

Guía del apartado 3.8 de la tesis, del principio al final. El sistema se publica
sobre **Render** —la aplicación— y **Supabase** —la base de datos—. El autor
confirmó el 29 de octubre de 2026 que todos los servicios actuales son gratuitos.
La fase 0 no modificó el despliegue publicado.

> **Antes de empezar.** Todo lo que sigue se hace una sola vez. Después, cada
> cambio que se envíe al repositorio se publica solo.

## Índice

1. [Servicios actuales y presupuesto](#1-servicios-actuales-y-presupuesto)
2. [Publicar el repositorio](#2-publicar-el-repositorio)
3. [Crear la base de datos en Supabase](#3-crear-la-base-de-datos-en-supabase)
4. [Crear los servicios en Render](#4-crear-los-servicios-en-render)
5. [Verificar el despliegue](#5-verificar-el-despliegue)
6. [Dominio propio y certificado](#6-dominio-propio-y-certificado)
7. [Respaldos](#7-respaldos)
8. [Reentrenar el modelo sin detener el servicio](#8-reentrenar-el-modelo-sin-detener-el-servicio)
9. [Lo que puede salir mal](#9-lo-que-puede-salir-mal)
10. [El entorno de pruebas](#10-el-entorno-de-pruebas)

---

## 1. Servicios actuales y presupuesto

| Componente | Servicio | Plan | Costo mensual |
|---|---|---|---|
| Servicios y motor neuronal | Render, servicio web con contenedor | gratuito, según el autor y `render.yaml` | US$ 0.00 |
| Disco persistente del modelo | No habilitado en `render.yaml` | sin contratación declarada | US$ 0.00 |
| Interfaz de cliente | Render, sitio estático | gratuito | US$ 0.00 |
| Base de datos | Supabase, PostgreSQL administrado | gratuito | US$ 0.00 |
| Dominio propio | Sin contratación declarada; se usa la dirección del proveedor | sin costo declarado | US$ 0.00 |

El gasto recurrente declarado es **US$ 0.00 / Q0.00**, según la confirmación del
autor; no es una auditoría de facturación. Las cifras anteriores de alojamiento,
disco y dominio eran estimaciones de otra configuración y no representan pagos
actuales. El presupuesto de la tesis debe diferenciar estimación y ejecución real.

**Rendimiento por verificar en el servicio publicado.** Se deben medir por separado
el arranque en frío y la generación con el modelo disponible. La gratuidad no
acredita ni impide por sí sola cumplir el criterio de HU-06. La fase 0 verificó el
recorrido local; no certificó los tiempos ni las cuotas actuales del proveedor.

**Medición histórica de recursos.** Se midió: el
servicio ocupa 271 MB con un proceso de trabajo, de los cuales 190 son la
biblioteca TensorFlow. El cómputo de un plan —predicción neuronal, rutina y
menú— tarda 44 milisegundos. Un segundo proceso de trabajo no cabría en la
memoria de la instancia, y por eso `PROCESOS_DE_TRABAJO` queda en uno.

---

## 2. Publicar el repositorio

Render y Supabase se conectan al repositorio, de modo que este paso va primero.
Es, además, un pendiente del apartado 3.5.2.

```bash
gh repo create sistema-rutinas-pg --private --source=. --remote=origin --push
```

Si prefiere hacerlo desde el sitio, cree el repositorio vacío y luego:

```bash
git remote add origin https://github.com/<su-usuario>/sistema-rutinas-pg.git
```

**Verifique antes de enviar** que no viaja ninguna credencial. El archivo
`.gitignore` excluye `backend/.env`, `.env.pruebas` y los respaldos, que son los
tres lugares donde hay datos que no deben salir del equipo:

```bash
git status --short
```

---

## 3. Crear la base de datos en Supabase

1. Entre a <https://supabase.com> y cree un proyecto.
2. **Región: East US (Ohio), `us-east-2`.** Debe coincidir con la región de
   Render que declara `render.yaml`. Cada consulta del sistema cruza esa
   distancia, y elegir regiones distintas agrega decenas de milisegundos a cada
   una sin ganar nada a cambio.
3. Anote la contraseña de la base de datos que le pide al crear el proyecto.
   Supabase no vuelve a mostrarla.
4. Vaya a **Project Settings → Database → Connection string** y copie la del
   **Session pooler**. Tiene esta forma:

   ```
   postgresql://postgres.<referencia>:<contraseña>@aws-1-us-east-2.pooler.supabase.com:5432/postgres
   ```

> **No use la conexión directa** (`db.<referencia>.supabase.co`). Solo responde
> por IPv6, y Render sale a la red por IPv4: el servicio arrancaría y no
> alcanzaría la base de datos, con un error de red que no dice nada sobre su
> causa. El repartidor de sesión atiende por IPv4 en todos los planes.

**No hay que crear ninguna tabla a mano.** El sistema crea su esquema al
arrancar, con las mismas entidades del modelo entidad-relación del apartado
3.4.3, y carga los catálogos iniciales y la cuenta de administrador.

---

## 4. Crear los servicios en Render

1. Entre a <https://render.com>, elija **New → Blueprint** y seleccione el
   repositorio. Render lee `render.yaml` y propone los dos servicios:
   `rutinas-servicios` y `rutinas-interfaz`.
2. Render pedirá los valores que el archivo marca como `sync: false`, porque son
   los que no pueden estar escritos en el repositorio:

   | Variable | Qué poner |
   |---|---|
   | `URL_BASE_DATOS` | La cadena del repartidor de sesión de Supabase, con la contraseña ya sustituida |
   | `ADMIN_CORREO` | Un correo real del Gimnasio FAMAS |
   | `ADMIN_CONTRASENA` | Una contraseña propia, que no esté en ningún archivo de ejemplo |

   `CLAVE_SECRETA` no se pide: Render la genera aleatoria y no la deja escrita en
   ningún archivo.

3. Confirme y espere. La primera construcción tarda varios minutos, casi todos
   en descargar TensorFlow.

> **El sistema se niega a arrancar si alguna credencial conserva su valor de
> ejemplo.** No es un obstáculo, es el último punto del apartado 3.8 convertido
> en una comprobación automática: un despliegue con la contraseña escrita en el
> repositorio deja la cuenta de administrador al alcance de cualquiera que lea
> el código.

4. Cuando los dos servicios estén publicados, confirme que las direcciones que
   Render les asignó coinciden con las que `render.yaml` da por supuestas. Si
   Render tuvo que agregar un sufijo a algún nombre porque ya estaba tomado, hay
   dos valores que corregir:

   | Dónde | Qué debe apuntar a |
   |---|---|
   | `destination` de la regla `/api/*` del sitio estático | La dirección de `rutinas-servicios` |
   | `ORIGENES_PERMITIDOS` de `rutinas-servicios` | La dirección de `rutinas-interfaz` |

   El primero es indispensable: sin él la interfaz no alcanza los servicios. El
   segundo solo actúa si algún día se separan los dominios, porque mientras el
   reenvío funcione el navegador ve un solo dominio y no hay petición de origen
   cruzado.

---

## 5. Verificar el despliegue

Sustituya `<direccion>` por la del sitio estático.

```bash
curl https://<direccion>/api/v1/estado
```

Debe responder `{"estado":"disponible",...}`. Que responda **a través de la
dirección de la interfaz**, y no de la de los servicios, es lo que comprueba que
el reenvío funciona y que ambos comparten dominio.

Después entre con el navegador y recorra el flujo completo: registro, perfil
biométrico, generación del plan y consulta de la rutina. En la pantalla de
administración, la ruta `/api/v1/administracion/estado` informa si el sistema
está usando la red neuronal o las fórmulas de referencia:

```json
{ "modelo": { "origen_de_los_planes": "red_neuronal" } }
```

Si dice `formula`, el modelo no llegó al disco. Busque en la bitácora de Render
la línea «Sembrando el modelo entrenado que trae la imagen».

Por último, la prueba de carga del requerimiento 4.5.2, ahora sí contra el gestor
de producción:

```bash
cd backend
uv run python prueba_de_carga.py --url https://<direccion>
```

---

## 6. Dominio propio y certificado

1. Registre el dominio con el proveedor que prefiera.
2. En Render, en `rutinas-interfaz` → **Settings → Custom Domains**, agregue el
   dominio. Render indica qué registro `CNAME` crear.
3. Créelo con su registrador y espere la propagación.
4. El certificado lo emite y lo renueva Render sin intervención. Con eso queda
   cubierto el cifrado del tránsito del requerimiento 4.5.1, que hasta ahora
   figuraba como pendiente de contratar.
5. Agregue el dominio a `ORIGENES_PERMITIDOS` del servicio `rutinas-servicios`.

---

## 7. Respaldos

**El plan gratuito de Supabase no conserva copias automáticas.** El respaldo de
`operaciones/` no es entonces una precaución adicional: es la única que existe
sobre los datos de producción.

```bash
URL_RESPALDO="postgresql://postgres.<referencia>:<contraseña>@aws-1-us-east-2.pooler.supabase.com:5432/postgres" ./operaciones/respaldar_base_datos.sh
```

Programe la ejecución diaria en el planificador de tareas del equipo donde viva
el repositorio. Los volcados quedan comprimidos en `respaldos/`, y el script
retira los que superan los treinta días. **No se versionan:** contienen los datos
biométricos de los usuarios, que la regla del negocio RN-06 reserva a su titular.

Un respaldo que nunca se restauró es un archivo, no un respaldo. Compruébelo
contra el entorno de pruebas:

```bash
./operaciones/restaurar_base_datos.sh respaldos/postgres_2026-09-03_0200.sql.gz
```

---

## 8. Reentrenar el modelo sin detener el servicio

Es el requerimiento no funcional 4.5.6. El modelo vive en un disco persistente,
separado de la imagen del contenedor, y el servicio puede releerlo en caliente.

```bash
cd backend
uv run python entrenar_modelo.py
```

Envíe el modelo nuevo al repositorio y espere a que Render publique. Después, con
la sesión de administrador:

```bash
curl -X POST https://<direccion>/api/v1/administracion/modelo/recargar -H "Authorization: Bearer <token>"
```

El servicio cambia de modelo sin dejar de atender peticiones, y vacía la memoria
de predicciones para que ninguna respuesta del modelo anterior sobreviva al
cambio.

---

## 9. Lo que puede salir mal

**Supabase suspende los proyectos gratuitos tras siete días de poca actividad.**
Es el riesgo operativo más serio de esta configuración, porque se materializa
justo cuando más importa: un sistema que nadie usa entre la entrega y la
presentación final llega dormido al día de la presentación, y reactivarlo desde
el panel toma varios minutos. Dos maneras de evitarlo:

- Entrar al sistema al menos una vez por semana.
- Subir Supabase a plan de pago la semana de la presentación, y volver a bajarlo
  después.

**El disco impide publicar sin corte.** Render detiene la versión anterior antes
de levantar la nueva, de modo que cada publicación deja el sistema unos segundos
sin responder. Es el precio de que el modelo reentrenado sobreviva a la
actualización del contenedor, y es un corte de segundos, no de minutos. No
publique durante la presentación.

**Un solo proceso de trabajo, una sola instancia.** El disco impide replicar el
servicio. Si la prueba de carga incumpliera el requerimiento 4.5.2, la salida no
es agregar procesos de trabajo —no caben en la memoria— sino subir el plan de la
instancia.

**La contraseña de Supabase lleva caracteres que la dirección no admite.** Si
contiene `@`, `/`, `:` o `#`, hay que escribirlos en su forma codificada dentro
de la cadena de conexión. Lo más simple es generar una contraseña sin ellos.

---

## 10. El entorno de pruebas

El apartado 3.8 distingue tres entornos, y el de pruebas es donde se valida un
incremento antes de publicarlo —la condición (g) de la definición de terminado
del apartado 4.8.2—. Levanta los tres componentes en contenedores, igual que
producción, contra una base de datos propia y desechable:

```bash
cp .env.pruebas.example .env.pruebas
```

Reemplace todos los valores del archivo copiado y levante la composición:

```bash
docker compose -f docker-compose.pruebas.yml --env-file .env.pruebas up -d --build
```

Queda en <http://localhost:8080>. Reproduce de producción lo que puede fallar al
desplegar —dos procesos de trabajo, la interfaz servida como archivos estáticos,
la ruta relativa de los servicios— sin tocar los datos reales de los usuarios.

Para detenerlo, conservando los datos:

```bash
docker compose -f docker-compose.pruebas.yml --env-file .env.pruebas down
```

## Preparación de la fase 2

Antes de publicar el sitio y las cuentas renovadas, respaldar y aplicar
`0002_recuperacion_acceso` siguiendo [MIGRACIONES.md](operaciones/MIGRACIONES.md).
El arranque no incorpora columnas a tablas existentes. Autorizar el remitente
mediante [CORREO_GMAIL.md](operaciones/CORREO_GMAIL.md), configurar el origen HTTPS
del frontend y ensayar la entrega real. La configuración de `render.yaml` por sí
sola no autoriza Google ni demuestra que el correo funcione. Consultar el
[informe de fase 2](operaciones/FASE_2_SITIO_Y_CUENTAS.md) antes del despliegue.

## Reexpresión de los costos del catálogo

**Paso obligatorio la primera vez que se publica esta versión sobre una base de
datos que ya tenía el catálogo cargado.**

El costo de los alimentos pasó a expresarse en quetzales por cada 100 gramos,
igual que su aporte nutricional. Antes la columna no declaraba unidad y el
catálogo quedó con valores por pieza, por libra y por envase mezclados. La carga
de arranque no corrige esto: solo inserta los alimentos que faltan y nunca
modifica los existentes, para no deshacer lo que el administrador haya corregido.

```bash
cd backend
URL_BASE_DATOS="<cadena de Supabase>" uv run python actualizar_costos_del_catalogo.py
URL_BASE_DATOS="<cadena de Supabase>" uv run python actualizar_costos_del_catalogo.py --aplicar
```

La primera invocación solo muestra qué haría. La segunda guarda. El script
respeta cualquier precio que ya se haya corregido a mano y lo reporta aparte para
revisarlo.

Sin este paso, la lista de compras y el costo del menú muestran cifras sin
sentido.

# Conexión y monitor del servicio (31-10-2026)

El autor confirmó que la URL pública actual es `https://senda-gt.onrender.com`
(antes `rutinas-interfaz`). La portada estática y la API son servicios separados.
Para comprobar el servidor,
configure el monitor con **GET** a
`https://rutinas-servicios.onrender.com/api/v1/estado`, cada cinco minutos.
La respuesta esperada es HTTP 200, `Content-Type: application/json` y
`"estado":"disponible"`. Una visita a la portada no verifica la API; una petición
HEAD puede devolver 405, ya que el controlador de salud declara GET.

Compruebe en el historial del monitor que las peticiones se ejecutan y que no
reciben una página HTML de arranque. El reenvío de la interfaz puede comprobarse
por separado en `https://senda-gt.onrender.com/api/v1/estado`.
Ambas rutas de salud respondieron JSON en la comprobación del 31-10-2026.
Usar cualquiera de esas dos rutas en el monitor; no basta con vigilar `/`.
No se cambió el monitor externo desde esta revisión.
La salud confirma que el proceso responde; no comprueba la base de datos ni la
generación neuronal. Si el acceso tarda con salud disponible, revisar los logs
del servicio, la conexión con Supabase y los tiempos de autenticación antes de
atribuirlo a suspensión. No compartir contraseñas ni tokens en esos registros.

Render documenta suspensión tras 15 minutos sin tráfico y alrededor de un minuto
para reactivar el servicio gratuito; también puede reiniciarlo en cualquier
momento. Un monitor no elimina esas limitaciones ni acredita rendimiento:
[documentación oficial](https://render.com/docs/free).

Desde la carpeta del sistema, diagnóstico público sin credenciales:

```powershell
backend/.venv/Scripts/python.exe operaciones/diagnosticar_conexion.py --salida operaciones/evidencias/conexion-ensayo-01.json
```

Usar un nombre nuevo para cada ensayo. Se comparan API directa y reenvío; un 401
al catálogo sin token es esperado, y no equivale a una consulta autenticada.
El cliente comienza una comprobación de salud al abrir la aplicación y la comparte
con el acceso: espera hasta 75 s por disponibilidad antes de enviar las credenciales
una sola vez. Las consultas y escrituras conservan su corte de red de 30 s,
incluida la lectura del cuerpo. Estos cortes no reemplazan los requisitos de
3 s para plan y 2 s para consultas. No hay pings periódicos desde el navegador.

Los cambios de cliente se construyen con `npm run build` desde `frontend`.
`VITE_URL_API=/api/v1` sigue siendo el valor de Render; si falta, la construcción
productiva también usa `/api/v1`, y desarrollo usa `127.0.0.1:8010`.
Esta revisión es local: no se publicaron cambios ni se migró producción.

