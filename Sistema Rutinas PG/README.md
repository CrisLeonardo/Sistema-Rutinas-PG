# Sistema de rutinas de entrenamiento y planes nutricionales

Sistema web que genera de forma automática regímenes nutricionales y rutinas de
entrenamiento personalizadas a partir de las variables biométricas del usuario,
ajustados a los alimentos y al equipamiento disponibles en el municipio de
El Progreso, Jutiapa.

Corresponde al Proyecto de Graduación de Leonardo Zepeda, Universidad Mariano
Gálvez de Guatemala. El análisis del sistema se documenta en el Capítulo IV de
la tesis; este repositorio contiene su implementación.

## Estado del desarrollo

El detalle tarea por tarea está en **[PLAN.md](PLAN.md)**, que lleva el control de lo
construido y lo pendiente. El desarrollo sigue las cinco iteraciones de la pila de
producto (Tabla 11 del Capítulo IV).

| Iteración | Épica | Historias | Puntos | Estado |
|---|---|---|---|---|
| 1 | E1. Acceso seguro | HU-01, HU-02, HU-03 | 8 | Terminada |
| 2 | E2. Perfil biométrico | HU-04, HU-05 | 8 | Terminada |
| 3 | E3. Generación de planes | HU-06, HU-07 | 21 | Terminada |
| 4 | E3 y E4. Catálogo local | HU-08, HU-11 | 13 | Terminada |
| 5 | E4. Seguimiento | HU-09, HU-10 | 13 | Terminada |

## Pila tecnológica

Corresponde a la definida en el apartado 3.6 de la tesis.

| Capa | Tecnología |
|---|---|
| Presentación | React, HTML5, CSS3 y Bootstrap 5 |
| Lógica y servicios | FastAPI sobre Python, interfaz REST con formato JSON |
| Inteligencia artificial | Python, TensorFlow 2.21 y Keras 3.15 |
| Persistencia | PostgreSQL 16, administrado por Supabase en producción |

## Requisitos previos

- Docker, para levantar la base de datos PostgreSQL.
- [uv](https://docs.astral.sh/uv/), que administra el entorno de Python.
- Node.js 20 o superior.

El backend se fija a **Python 3.12**: TensorFlow, que se incorpora en la
iteración 3, aún no publica versiones compatibles con Python 3.14. `uv` descarga
e instala esa versión automáticamente.

## Puesta en marcha

### 1. Base de datos

Desde la raíz del proyecto:

```bash
docker compose up -d
```

PostgreSQL queda disponible en el puerto **5433** del equipo, para no interferir
con otra instalación de PostgreSQL que pudiera existir en el puerto habitual. Es
la misma versión mayor que ejecuta Supabase en producción, de modo que un defecto
propio del gestor aparezca aquí y no allá.

### 2. Servicios (backend)

```bash
cd backend
cp .env.example .env          # en Windows: copy .env.example .env
uv sync
uv run uvicorn app.main:aplicacion --host 127.0.0.1 --port 8010 --reload
```

Antes de usarlo, genere su propia clave de firma y colóquela en `CLAVE_SECRETA`
dentro de `.env`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Al iniciar por primera vez, el sistema crea el esquema de la base de datos y una
cuenta de administrador con las credenciales indicadas en `.env`. **Cambie esa
contraseña antes de cualquier despliegue.**

La documentación interactiva de los servicios queda en
<http://127.0.0.1:8010/documentacion>.

### 3. Interfaz de cliente (frontend)

```bash
cd frontend
cp .env.example .env          # en Windows: copy .env.example .env
npm install
npm run dev
```

La aplicación queda en <http://localhost:5173>.

### Nota sobre el puerto 8010

Los servicios se publican en el puerto 8010 y no en el 8000 porque el reenvío de
puertos de Docker y WSL ocupa el 8000 sobre IPv6. Como en Windows el nombre
`localhost` se resuelve primero a IPv6, el navegador alcanzaría ese otro servicio
en lugar del backend. Por la misma razón, el archivo `.env` del frontend apunta a
`127.0.0.1` y no a `localhost`.

## Pruebas

Las pruebas funcionales verifican uno a uno los criterios de aceptación de la
Tabla 10 del Capítulo IV. Se ejecutan sobre una base de datos temporal, por lo
que no requieren que PostgreSQL esté levantado.

```bash
cd backend
uv run pytest -v
```

Las pruebas que entrenan la red neuronal tardan cerca de medio minuto. Para
excluirlas durante el desarrollo:

```bash
cd backend
uv run pytest -m "not lenta"
```

## Modelo neuronal

El motor de cálculo vive en `backend/app/motor/` y no depende de la base de datos
ni de la interfaz: puede entrenarse y evaluarse por separado.

| Módulo | Contenido |
|---|---|
| `formulas.py` | Mifflin-St Jeor, Harris-Benedict, factores de actividad, reglas *b*, *c* y *d*, constantes de Atwater, volumen de entrenamiento |
| `conjunto_datos.py` | Generación de perfiles sintéticos, normalización y división en entrenamiento y validación |
| `red_neuronal.py` | Arquitectura, entrenamiento, métricas y predicción |
| `rutina.py` | Reparto del volumen semanal entre las sesiones disponibles (HU-07) |

Para entrenar el modelo:

```bash
cd backend
uv run python entrenar_modelo.py
```

El script genera el conjunto de datos, entrena la red, mide su margen de error
frente a las dos fórmulas de referencia y guarda en `backend/modelo/` el modelo,
su normalizador y sus métricas. El modelo entrenado no se versiona porque se
regenera con este script, lo que permite reentrenarlo sin modificar el código del
servicio que lo consume (requerimiento no funcional 4.5.6).

La red recibe ocho variables —peso, estatura, edad, sexo, factor de actividad,
ajuste del objetivo, nivel de experiencia y frecuencia semanal— y entrega cinco:
el requerimiento energético, los tres macronutrientes y el volumen semanal de
series por grupo muscular, que es lo que el apartado 2.5.1 de la tesis le encarga.

Resultado del último entrenamiento, con 40 000 perfiles sintéticos y tres capas
ocultas de 128, 128 y 64 neuronas con activación ReLU:

| Métrica | Valor |
|---|---|
| Error absoluto medio | 2.6 kcal |
| Margen de error medio | 0.11 % |
| Margen de error máximo | 2.69 % |
| Perfiles de validación bajo el 5 % | 100 % |
| Error del volumen de entrenamiento | 0.02 series |

El criterio de aceptación de la investigación —un margen de error inferior al
5 % frente a las fórmulas de Mifflin-St Jeor y Harris-Benedict— se cumple.

El servicio precarga el modelo al arrancar. Sin esa precarga, el primer usuario
en pedir su plan pagaría el costo de importar TensorFlow y leer el modelo del
disco —cerca de seis segundos— y el sistema incumpliría el criterio de HU-06, que
exige generar el plan en menos de tres segundos. Con el modelo ya en memoria, la
generación completa tarda medio segundo.

Si el modelo no se ha entrenado, el sistema arranca igual y calcula los planes con
las fórmulas de referencia: cada plan registra en `origen_calculo` con cuál de las
dos vías se produjo.

## Estructura del proyecto

```
Sistema Rutinas PG/
├── docker-compose.yml           Base de datos PostgreSQL (desarrollo)
├── docker-compose.pruebas.yml   Los tres componentes en contenedores (pruebas)
├── render.yaml                  Entorno productivo declarado (Render y Supabase)
├── DESPLIEGUE.md                Procedimiento de despliegue paso a paso
├── operaciones/                 Respaldo y restauración de la base de datos
├── backend/
│   ├── app/
│   │   ├── main.py              Punto de entrada de la aplicación
│   │   ├── nucleo/              Configuración, base de datos, seguridad y arranque
│   │   ├── modelos/             Entidades del modelo entidad-relación (3.4.3)
│   │   ├── esquemas/            Contratos de entrada y salida de la interfaz
│   │   ├── motor/               Fórmulas de referencia y red neuronal (E3)
│   │   ├── servicios/           Reglas de negocio
│   │   └── api/                 Controladores de la interfaz REST
│   ├── modelo/                  Modelo entrenado (se versiona: lo necesita el despliegue)
│   ├── entrenar_modelo.py       Script de entrenamiento de la red
│   ├── entrada.sh               Arranque del contenedor: siembra el modelo y fija el puerto
│   └── tests/                   Pruebas de los criterios de aceptación
└── frontend/
    └── src/
        ├── paginas/             Pantallas de la aplicación
        ├── componentes/         Elementos reutilizables de la interfaz
        ├── contexto/            Manejo de la sesión del usuario
        ├── datos/               Valores controlados y sus explicaciones
        └── servicios/           Cliente de la interfaz de programación
```

La separación entre `modelos`, `api` y las pantallas de `frontend` materializa el
patrón modelo-vista-controlador adoptado en el apartado 3.1.2.

## Interfaz de programación de aplicaciones

| Método | Ruta | Acceso | Historia |
|---|---|---|---|
| POST | `/api/v1/autenticacion/registro` | Público | HU-01 |
| POST | `/api/v1/autenticacion/acceso` | Público | HU-02 |
| POST | `/api/v1/autenticacion/renovacion` | Autenticado | HU-02 |
| POST | `/api/v1/autenticacion/cambio-de-contrasena` | Autenticado | Seguridad |
| GET | `/api/v1/autenticacion/sesion` | Autenticado | HU-02 |
| GET | `/api/v1/usuarios` | Administrador | HU-03 |
| PUT | `/api/v1/usuarios/{id}/rol` | Administrador | HU-03 |
| PUT | `/api/v1/usuarios/{id}/estado` | Administrador | HU-03 |
| POST | `/api/v1/perfil-biometrico` | Autenticado | HU-04 |
| GET | `/api/v1/perfil-biometrico` | Autenticado | HU-04 |
| GET | `/api/v1/perfil-biometrico/historial` | Autenticado | HU-05 |
| POST | `/api/v1/plan-nutricional` | Autenticado | HU-06 |
| GET | `/api/v1/plan-nutricional` | Autenticado | HU-06 |
| GET | `/api/v1/plan-nutricional/historial` | Autenticado | HU-06 |
| GET | `/api/v1/rutina` | Autenticado | HU-07 |
| GET | `/api/v1/entrenamiento/sesiones/{id}` | Autenticado | Adicional |
| POST | `/api/v1/entrenamiento/sesiones` | Autenticado | Adicional |
| GET | `/api/v1/entrenamiento/sesiones` | Autenticado | Adicional |
| GET | `/api/v1/entrenamiento/ejercicios/{id}` | Autenticado | Adicional |
| GET | `/api/v1/entrenamiento/resumen` | Autenticado | Adicional |
| POST | `/api/v1/progreso` | Autenticado | HU-09 |
| GET | `/api/v1/progreso` | Autenticado | HU-09 |
| GET | `/api/v1/progreso/reporte` | Autenticado | HU-10 |
| GET | `/api/v1/plan-nutricional/menu` | Autenticado | HU-08 |
| GET | `/api/v1/plan-nutricional/lista-de-compras` | Autenticado | Adicional |
| GET | `/api/v1/catalogos/alimentos` | Autenticado | HU-11 |
| POST | `/api/v1/catalogos/alimentos` | Administrador | HU-11 |
| PUT | `/api/v1/catalogos/alimentos/{id}` | Administrador | HU-11 |
| PUT | `/api/v1/catalogos/alimentos/{id}/disponibilidad` | Administrador | HU-11 |
| GET | `/api/v1/catalogos/ejercicios` | Autenticado | HU-11 |
| POST | `/api/v1/catalogos/ejercicios` | Administrador | HU-11 |
| PUT | `/api/v1/catalogos/ejercicios/{id}` | Administrador | HU-11 |
| PUT | `/api/v1/catalogos/ejercicios/{id}/disponibilidad` | Administrador | HU-11 |
| GET | `/api/v1/administracion/estado` | Administrador | Operación |
| POST | `/api/v1/administracion/modelo/recargar` | Administrador | 4.5.6 |
| GET | `/api/v1/estado` | Público | Monitoreo |

Las rutas del perfil biométrico y del plan operan siempre sobre la cuenta que inició sesión.
No existe ninguna ruta que permita consultar el perfil de otra persona, ni
siquiera para el administrador, en cumplimiento de la regla del negocio *f* del
apartado 4.3.4.

## Seguridad

Conforme al requerimiento no funcional 4.5.1:

- Las contraseñas se almacenan con `bcrypt`, que aplica sal aleatoria; nunca se
  guardan ni se devuelven en texto plano.
- El acceso a cada recurso se valida en el servidor a partir del rol almacenado
  en la base de datos, no del rol declarado en el token.
- El mensaje de credenciales incorrectas es el mismo para un correo inexistente
  y para una contraseña equivocada, de modo que no revela cuál dato falló.
- La sesión caduca tras treinta minutos de inactividad y se renueva mientras el
  usuario interactúe con la aplicación.

- Los datos biométricos solo son visibles para su titular: las consultas se
  filtran por el identificador que viaja en el token verificado y no por un
  parámetro de la petición.

- Los intentos fallidos de acceso se cuentan por cuenta y por dirección de origen
  a la vez, y se bloquean tras agotarse. Contar solo por cuenta permitiría dejar
  fuera al titular de un correo conocido; contar solo por origen dejaría pasar un
  ataque repartido entre direcciones. El límite protege además la disponibilidad:
  `bcrypt` consume cerca de un décimo de segundo de procesador por intento, y la
  instancia contratada tiene medio núcleo.

- Cada respuesta lleva encabezados de seguridad propios. Los del sitio estático,
  declarados en `render.yaml` y en `nginx.conf`, no alcanzan a las respuestas del
  backend. Se añaden `nosniff`, `X-Frame-Options: DENY`, una política de contenido
  restrictiva y `Cache-Control: no-store`, para que un plan —que es un dato de
  salud— no quede en la memoria intermedia de ningún proxy. HSTS solo en producción.

- La documentación interactiva y el esquema OpenAPI se sirven **solo fuera de
  producción**: publicarlos entrega a cualquiera el mapa completo de la interfaz,
  incluidas las rutas reservadas al administrador.

- El usuario puede cambiar su propia contraseña. Se le exige la vigente aunque la
  sesión ya esté abierta: un teléfono desatendido no debe bastar para quedarse con
  la cuenta.

Los archivos `.env` contienen credenciales y están excluidos del control de
versiones; solo se versionan las plantillas `.env.example`.

## Guardarrailes clínicos del plan

El motor produce el requerimiento energético que las fórmulas de referencia
determinan. Antes de prescribirlo, `app/motor/seguridad.py` comprueba que lo
calculado quepa dentro de lo que es seguro comer, y lo corrige cuando no.

| Situación | Qué hace el sistema |
|---|---|
| Energía por debajo del mínimo alimentario | La eleva a 1 200 kcal en mujeres y 1 500 en hombres, y lo explica |
| Índice de masa corporal bajo con objetivo de perder grasa | No aplica déficit: prescribe mantenimiento y advierte |
| Índice de masa corporal normal | Gradúa el déficit —10 % o 15 %— en lugar de aplicar siempre el 20 % |
| Obesidad | Calcula la proteína sobre un peso de referencia, no sobre el peso total |
| Cualquier caso | La proteína nunca supera el 35 % de la energía del día |

La corrección se aplica **después** del cálculo y no dentro de las fórmulas, a
propósito. Las ecuaciones de Mifflin-St Jeor y Harris-Benedict son el patrón
contra el que se mide la precisión de la red neuronal, y alterarlas cambiaría la
referencia misma de esa medición. El margen de error de la historia HU-06 se
sigue midiendo sobre el valor que el modelo produce, antes de acotarlo: el ajuste
es una regla del negocio, no un error del modelo, y confundirlos haría que un plan
correcto se reportara como fuera del margen admitido.

El plan devuelve las correcciones aplicadas en `correcciones_de_seguridad` y los
avisos de salud en `advertencias_de_salud`, y ambos se muestran al usuario: el
plan no se corrige en silencio.

Estas reglas **no sustituyen la valoración profesional** ni emiten diagnóstico,
conforme a la regla del negocio *e* del apartado 4.3.4. Acotan una prescripción,
que es cosa distinta.

## Costo del plan y lista de compras

El catálogo registra el costo de cada alimento **en quetzales por cada 100
gramos**, igual que su aporte nutricional. Con ese dato el sistema hace tres
cosas: estima lo que cuesta el menú por día y por mes, prefiere el alimento
económico cuando existe uno de aporte equivalente, y arma la lista de compras de
la semana.

El estudio de campo del Capítulo I documenta que la barrera declarada con más
frecuencia es económica. Un plan cuyo costo el usuario descubre recién frente al
puesto del mercado no resuelve esa barrera: la traslada.

La lista de compras suma el menú por siete días, lo agrupa por categoría —que es
como se recorren los puestos— y expresa las cantidades en libras, que es la
unidad con que se despacha en los mercados del municipio.

**Si la base de datos ya tenía el catálogo cargado antes de esta versión, hay que
reexpresar los costos una sola vez:**

```bash
cd backend
uv run python actualizar_costos_del_catalogo.py            # muestra qué haría
uv run python actualizar_costos_del_catalogo.py --aplicar  # lo aplica
```

Antes, la columna no declaraba su unidad: la instrucción del levantamiento pedía
«el precio observado en el mercado», y el catálogo quedó con la tortilla por
pieza, el pollo por libra y el aceite por envase. Sumar esos valores no producía
ninguna cifra con sentido, y por eso el dato se capturaba sin que nada lo usara.
El script solo corrige la fila que conserva el valor sembrado: un precio que el
administrador ya haya corregido en el mercado se respeta y se reporta aparte.

Los precios siguen siendo estimaciones hasta el levantamiento de campo, igual que
el resto del catálogo.

## Validaciones del perfil biométrico

Del criterio de aceptación de HU-04 y de las reglas del negocio del apartado
4.3.4. Todas se aplican en el servidor, no solo en la interfaz (apartado 4.8.3).

| Dato | Regla |
|---|---|
| Peso | Obligatorio, entre 30 y 250 kilogramos |
| Estatura | Obligatoria, entre 120 y 220 centímetros |
| Edad | Obligatoria, desde 18 años cumplidos (regla del negocio *a*) |
| Sexo | Obligatorio: masculino o femenino |
| Nivel de actividad | Obligatorio: sedentario, ligero, moderado, alto o muy alto |
| Objetivo | Obligatorio: pérdida de grasa, mantenimiento o ganancia muscular |
| Días de entrenamiento | Entre 1 y 7 por semana |

Actualizar las medidas nunca sobrescribe la medición anterior: cada envío agrega
un registro con su propia fecha, y el historial resultante es el que la historia
HU-05 expone y el que alimentará el reajuste del plan en la Iteración 5.

## Rutina de entrenamiento

La rutina se genera junto con el plan nutricional, en la misma transacción: un
plan sin rutina describiría solo la mitad del incremento. El reparto vive en
`app/motor/rutina.py` y respeta el criterio de aceptación de HU-07 —ningún grupo
muscular recibe estímulo en dos días consecutivos—, comprobado para las siete
frecuencias posibles y considerando que el microciclo se repite: el último día de
la semana tampoco puede chocar con el primero de la siguiente.

El catálogo de ejercicios se carga al arrancar con 25 ejercicios ejecutables con
equipamiento básico. **Es una lista provisional:** la historia HU-11 exige levantar
el equipamiento efectivamente disponible en el Gimnasio FAMAS mediante visita
directa. La carga es idempotente y no deshace lo que el administrador modifique.

## Bitácora de entrenamiento y progresión de carga

La rutina era de solo lectura: el sistema prescribía series, repeticiones y
repeticiones en reserva, y no tenía forma de saber si se ejecutaron ni con cuánto
peso. Al final de la semana el usuario reportaba cuántas sesiones cumplió —un
número suelto— y con eso el sistema decidía si reajustaba el plan.

Esa falta de datos tenía una consecuencia concreta: la regla del negocio *d* del
apartado 4.3.4, que acota el incremento de carga al 10 % entre microciclos,
estaba implementada en `formulas.progresion_admitida` y **no se invocaba desde
ningún servicio**. El principio de sobrecarga progresiva del apartado 2.5.2
aparecía únicamente como un párrafo que le pedía al usuario subir la carga por su
cuenta. En la práctica, la rutina de la semana doce era idéntica a la de la
primera.

La bitácora registra la ejecución real —serie por serie, con su peso— y con ella
el sistema calcula la carga de la sesión siguiente.

### El método: progresión doble

Es el que la literatura de referencia prescribe para el principiante y el
intermedio, y consta de tres pasos:

1. Se entrena dentro de un rango de repeticiones, no en un número fijo.
2. Mientras no se alcance el extremo alto del rango **en todas las series**, se
   repite la misma carga y se busca sumar repeticiones.
3. Cuando se alcanza, se sube la carga y las repeticiones vuelven al extremo bajo.

El paso 3 es el que la regla *d* acota. De esa cota sale una consecuencia que
importa: con cargas ligeras, el incremento más pequeño que el gimnasio permite
—un disco de 1.25 kg por lado— ya supera el 10 %. Con 20 kg en la barra, subir
2.5 kg es un 12.5 %. El sistema **no se salta la regla**: responde que se siga
progresando en repeticiones hasta que el salto quepa dentro del límite.

| Situación | Qué decide el sistema |
|---|---|
| Sin historial | No inventa una carga: pide elegir un peso y guardarlo |
| No completó el rango | Repetir la misma carga y sumar repeticiones |
| Completó el rango en todas las series | Subir al siguiente escalón armable, dentro del 10 % |
| El escalón mínimo excedería el 10 % | Seguir en repeticiones y explicar por qué |
| Ejercicio de peso corporal | Progresar en repeticiones; no hay carga que anotar |
| Tres sesiones estancado con esfuerzo alto | Descargar un 10 %: es fatiga acumulada, no falta de estímulo |

La bitácora se enlaza al **ejercicio del catálogo** y no a la sesión prescrita.
Al regenerarse el plan, las sesiones prescritas se sustituyen por otras nuevas;
el historial de cargas debe sobrevivir a ese cambio, porque es justamente lo que
da continuidad al entrenamiento.

### La pantalla del gimnasio

`/entrenar/:sesionId` se usa con el teléfono en la mano entre serie y serie, y de
eso salen sus tres decisiones de diseño:

- **Todo viene precargado.** La carga sugerida y las repeticiones objetivo ya
  están escritas: confirmar una serie es un toque, no cuatro campos.
- **Lo marcado se guarda en el dispositivo** conforme se avanza. Un teléfono que
  se bloquea a mitad de la sesión no debe costar el entrenamiento entero.
- **El descanso se cronometra solo.** Es parte de la dosis prescrita —dos minutos
  en los compuestos— y hasta ahora la pantalla lo declaraba en texto y confiaba
  en que alguien lo midiera.

El resumen de la bitácora entrega además la racha de semanas, el volumen semanal
y las marcas personales de cada ejercicio, con la repetición máxima estimada por
la fórmula de Epley. Es una estimación para comparar series de repeticiones
distintas en una sola cifra: **el sistema nunca le pide a nadie levantar su
máximo.**

## Seguimiento y reajuste

El usuario registra cada semana su peso, su perímetro de cintura, las sesiones que
completó y qué tanto siguió el plan. Con ese avance el sistema decide si reajusta:

| Situación | Qué hace |
|---|---|
| Adherencia menor al 70 % | No reajusta: el estancamiento no se explica por el cálculo |
| Cambio de peso menor a 0.5 kg | No reajusta: cabe en la fluctuación normal |
| Cambio apreciable con buena adherencia | Registra la medición, regenera plan y rutina |

El reajuste no aplica una corrección calórica inventada: convierte el peso reportado
en una medición biométrica nueva y regenera el plan por la misma cadena que produjo
el original, de modo que las reglas del negocio se cumplen por construcción. La
respuesta explica siempre qué hizo y por qué.

Los reportes de evolución se dibujan con SVG propio, sin bibliotecas de terceros,
para no requerir complementos (requerimiento 4.5.5) y garantizar la legibilidad en
pantallas de 320 píxeles.


## Despliegue en producción

El sistema se publica sobre **Render** —la aplicación, en contenedor— y **Supabase**
—PostgreSQL administrado—. El procedimiento completo, paso a paso, está en
**[DESPLIEGUE.md](DESPLIEGUE.md)**; aquí solo va el resumen.

El apartado 3.8 exige separar los entornos, empaquetar en contenedores, configurar
respaldos y cambiar todas las credenciales. Los tres entornos son:

| Entorno | Dónde se declara | Para qué |
|---|---|---|
| Desarrollo | `docker-compose.yml` y los servicios ejecutados a mano | Programar |
| Pruebas | `docker-compose.pruebas.yml` | Validar un incremento antes de publicarlo, que es la condición (g) de la definición de terminado |
| Producción | `render.yaml` | El sistema en uso |

Producción queda declarada entera en un archivo versionado, de modo que el despliegue
sea reproducible y no dependa de recordar qué se configuró a mano en un panel.

### El entorno de pruebas

Levanta los tres componentes en contenedores, igual que producción, contra una base
de datos propia y desechable:

```bash
cp .env.pruebas.example .env.pruebas
```

Reemplace todos los valores y levante la composición:

```bash
docker compose -f docker-compose.pruebas.yml --env-file .env.pruebas up -d --build
```

Queda en <http://localhost:8080>.

El sistema **se niega a arrancar en producción** si detecta que alguna credencial
conserva su valor de ejemplo. Un despliegue con la contraseña escrita en el
repositorio no es un descuido recuperable: cualquiera que lea el código entra como
administrador.

### Respaldos

```bash
./operaciones/respaldar_base_datos.sh
```

Sin variables, respalda el entorno de pruebas. Para producción, la cadena de conexión
entra por el entorno, de modo que la credencial no queda escrita en ningún archivo:

```bash
URL_RESPALDO="<cadena de Supabase>" ./operaciones/respaldar_base_datos.sh
```

Para restaurar:

```bash
./operaciones/restaurar_base_datos.sh respaldos/<archivo>.sql.gz
```

El primero está pensado para el planificador de tareas (`0 2 * * *`) y retira los
volcados que superan el periodo de retención. **El plan gratuito de Supabase no
conserva copias automáticas,** de modo que este respaldo no es una precaución
adicional sino la única que existe sobre los datos de producción. El segundo script
existe porque un respaldo que nunca se ha restaurado no es un respaldo, es un
archivo: conviene probarlo.

### Reentrenar sin detener el servicio

El requerimiento 4.5.6 pide que el modelo pueda reentrenarse sin interrumpir el
servicio. El modelo vive en un disco persistente, fuera de la imagen del contenedor:

```bash
cd backend
uv run python entrenar_modelo.py
```

Envíe el modelo nuevo al repositorio, espere a que Render publique, y póngalo en
operación sin detener el servicio:

```bash
curl -X POST https://sudominio.gt/api/v1/administracion/modelo/recargar -H "Authorization: Bearer <token de administrador>"
```

### Pruebas de carga

```bash
cd backend
uv run python prueba_de_carga.py --usuarios 50 --url http://127.0.0.1:8010
```

La prueba tiene dos fases: prepara las cuentas sin medir —crear cincuenta cuentas
simultáneas satura la función de cifrado de contraseñas y daría un número que no
describe ningún escenario real— y después somete al sistema a las operaciones de uso
con todos los usuarios a la vez.

**La medición solo es concluyente contra el gestor de producción.** SQLite serializa
las escrituras de todos los procesos sobre un mismo archivo; PostgreSQL las admite en
paralelo. Ejecutada contra PostgreSQL con cincuenta usuarios concurrentes y un solo
proceso de trabajo, las seis operaciones cumplen sus límites sin ningún fallo. Queda
repetirla contra el sistema ya publicado, que corre en una instancia más modesta y con
la base de datos al otro lado de la red.
