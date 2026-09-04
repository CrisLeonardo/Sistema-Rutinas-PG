# Levantamiento de campo de los catálogos (HU-11)

Esta carpeta es para el resultado de la visita a los mercados de El Progreso,
Jutiapa y al Gimnasio FAMAS. Llene las dos plantillas con lo que encuentre y
después cárguelas con `backend/cargar_catalogo_de_campo.py`. Ese script
reemplaza los valores provisionales de `app/nucleo/alimentos_iniciales.py` y
`app/nucleo/catalogo_inicial.py` por los reales, sin tocar código.

Puede editar los `.csv` con Excel, LibreOffice o Google Sheets — guárdelos de
nuevo en formato CSV (no `.xlsx`) al terminar.

## `alimentos_plantilla.csv`

| Columna | Qué anotar |
|---|---|
| `nombre` | Nombre del alimento tal como se pide en el mercado |
| `categoria` | Una de: `cereal`, `proteina_animal`, `leguminosa`, `lacteo`, `fruta`, `verdura`, `grasa`, `tuberculo` |
| `energia_kcal_100g` | Kilocalorías por cada 100 gramos |
| `proteina_g_100g` | Gramos de proteína por cada 100 gramos |
| `carbohidrato_g_100g` | Gramos de carbohidrato por cada 100 gramos |
| `grasa_g_100g` | Gramos de grasa por cada 100 gramos |
| `costo_aproximado_quetzales` | Precio observado en el mercado (puede dejarse vacío) |
| `medida_casera` | Cómo se sirve sin báscula, ej. `1 tortilla ≈ 30 g` |
| `disponible` | `si` o `no` — si el alimento se consigue en el municipio |

**El aporte nutricional (columnas de energía y macronutrientes) no se mide en
el mercado.** Para esos cuatro valores use una tabla de composición de
alimentos confiable (INCAP — Instituto de Nutrición de Centro América y
Panamá, es la referencia regional) y busque el alimento más parecido al que
vio en el mercado. Lo que sí se levanta en el mercado es el **nombre exacto**,
la **disponibilidad real** y el **costo**. Los 36 alimentos ya cargados
(`app/nucleo/alimentos_iniciales.py`) traen esas cuatro columnas ya resueltas
con ese mismo tipo de tabla: puede partir de esa lista, confirmar cuáles
existen de verdad en el mercado, corregir el costo y el nombre, agregar los
que falten y marcar `no` en los que no se consiguen.

## `ejercicios_plantilla.csv`

| Columna | Qué anotar |
|---|---|
| `nombre` | Nombre del ejercicio |
| `grupo_muscular` | Uno de: `pecho`, `espalda`, `pierna`, `hombro`, `brazo`, `abdomen`, `cuerpo_completo` |
| `nivel_minimo` | Uno de: `principiante`, `intermedio`, `avanzado` |
| `equipamiento` | Lo que el ejercicio necesita, tal como está en el gimnasio (ej. `Barra y discos`, `Mancuernas`, `Polea`, `Máquina`, `Peso corporal`) |
| `descripcion` | Instrucción breve de ejecución (opcional) |
| `es_compuesto` | `si` si mueve más de una articulación principal, `no` si es de aislamiento |
| `disponible` | `si` o `no` — si FAMAS tiene el equipo para ejecutarlo |

Aquí sí todo se levanta en el gimnasio: revise qué máquinas, barras,
mancuernas y poleas hay realmente disponibles, y para cada una anote qué
ejercicios se pueden ejecutar. Los 25 ejercicios ya cargados sirven de punto
de partida — táchelos (columna `disponible` en `no`) si FAMAS no tiene el
equipo correspondiente.

## Cómo cargar el resultado

```bash
cd backend
uv run python cargar_catalogo_de_campo.py \
  --alimentos ../operaciones/campo/alimentos_plantilla.csv \
  --ejercicios ../operaciones/campo/ejercicios_plantilla.csv
```

El script:

- **Crea** los alimentos/ejercicios cuyo nombre no existe todavía en el catálogo.
- **Actualiza** los que ya existen con el mismo nombre (nutrición, costo, disponibilidad, etc.).
- Nunca borra nada: la baja siempre es `disponible=no`, para no romper los planes ya generados que referencian esos alimentos o ejercicios.
- Valida cada fila con las mismas reglas que la pantalla de administración
  (energía entre 0 y 900 kcal, macronutrientes entre 0 y 100 g, costo no
  negativo). Si una fila tiene un error, lo reporta con el número de fila y
  sigue con las demás — no hace falta corregir todo antes de intentar cargar.
- Se puede correr varias veces sin duplicar nada: es idempotente por nombre.

Puede correrlo primero contra el entorno de pruebas
(`docker-compose.pruebas.yml`) para revisar el resultado antes de tocar
producción.
