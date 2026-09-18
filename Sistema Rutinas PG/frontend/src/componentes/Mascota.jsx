/**
 * Liko, el lobo del sistema.
 *
 * Se dibuja en SVG por la misma razón que los iconos de la barra y las gráficas
 * de los reportes: el requerimiento no funcional 4.5.5 pide que el sistema
 * funcione sin complementos adicionales, y una mascota en mapa de bits obligaría
 * a descargar una imagen por cada estado —ocho— sobre la conexión móvil desde la
 * que entra el 72.2 % de los usuarios. Dibujada, son cuatro kilobytes que ya
 * viajan con la aplicación, se adaptan al tema claro y al oscuro sin una segunda
 * versión, y escalan de los 46 px de una fila a los 200 px de la pantalla de la
 * senda sin perder el filo.
 *
 * La mascota no tiene una sola pose. Cada estado corresponde a una situación
 * real del usuario y lo decide el servidor, en `motor.juego.animo_del_usuario`,
 * porque depende de la bitácora completa: cuándo fue la última sesión, si hoy
 * toca entrenar, si la racha está en riesgo. La interfaz solo dibuja.
 *
 *   saludo      · nada que reportar; está ahí
 *   animando    · el usuario entrenó hoy
 *   entrenando  · hoy toca sesión y todavía no la ha registrado
 *   descanso    · hoy no toca; el descanso es parte del programa
 *   dormido     · más de diez días sin entrenar
 *   alerta      · la semana avanza y la racha está en riesgo
 *   celebrando  · subió de nivel o consiguió una insignia
 *   pensando    · todavía no ha registrado ninguna sesión
 *
 * El atavío —la cinta, la corona de laurel, la capa, el halo— lo fija el nivel y
 * no el estado. Es lo que hace visible el avance sin obligar a leer una cifra:
 * el mismo lobo, mejor vestido.
 *
 * Sobre las coordenadas: el lienzo va de -10 a 150 en vertical para que el halo
 * del último nivel y los añadidos que flotan sobre la cabeza quepan sin recortar
 * el dibujo. El cuerpo ocupa de x=38 a x=82, más estrecho que la cabeza, y los
 * brazos salen POR FUERA de ese ancho: trazados por dentro de la silueta no se
 * ven, y el dibujo queda manco con las patas asomando por los costados.
 *
 * Es decorativa por omisión: lo que informa es el texto que la acompaña. Cuando
 * va sola se le pasa `etiqueta` y entonces sí se anuncia.
 */

/** Pose de los brazos, gesto de la cara y añadidos de cada estado. */
const ESTADOS = {
  saludo: { pose: 'cadera', ojos: 'abiertos', boca: 'sonrisa', cejas: 'normales' },
  animando: {
    pose: 'arriba',
    ojos: 'felices',
    boca: 'abierta',
    cejas: 'normales',
    destellos: true,
    salta: true,
  },
  entrenando: { pose: 'mancuerna', ojos: 'abiertos', boca: 'sonrisa', cejas: 'decididas' },
  descanso: { pose: 'abajo', ojos: 'entornados', boca: 'sonrisa', cejas: 'normales' },
  dormido: { pose: 'abajo', ojos: 'cerrados', boca: 'dormida', cejas: 'normales', duerme: true },
  alerta: { pose: 'aviso', ojos: 'abiertos', boca: 'preocupada', cejas: 'preocupadas', avisa: true },
  celebrando: {
    pose: 'arriba',
    ojos: 'felices',
    boca: 'abierta',
    cejas: 'normales',
    destellos: true,
    confeti: true,
    salta: true,
  },
  pensando: { pose: 'pergamino', ojos: 'abiertos', boca: 'sonrisa', cejas: 'normales' },
}

/** Trazo común de todas las piezas del dibujo: el contorno de caricatura. */
const CONTORNO = {
  stroke: 'var(--mascota-contorno)',
  strokeWidth: 2,
  strokeLinejoin: 'round',
  strokeLinecap: 'round',
}

/**
 * Brazos: un trazo grueso terminado en pata, distinto en cada pose.
 *
 * `brazalete` es el punto del brazo izquierdo donde se prende la cinta de
 * laurel. Viaja con la pose porque el brazo se mueve: en una posición fija
 * quedaría flotando en el aire en cuanto el lobo levanta los brazos.
 */
const BRAZOS = {
  cadera: {
    izquierdo: 'M44 68 C34 72 29 82 33 90',
    derecho: 'M76 68 C86 72 91 82 87 90',
    patas: [
      [33, 91],
      [87, 91],
    ],
    brazalete: [31, 80, 22],
  },
  arriba: {
    izquierdo: 'M44 66 C32 60 24 46 27 34',
    derecho: 'M76 66 C88 60 96 46 93 34',
    patas: [
      [27, 33],
      [93, 33],
    ],
    brazalete: [31, 50, -52],
  },
  mancuerna: {
    izquierdo: 'M44 68 C34 72 30 82 34 89',
    derecho: 'M76 68 C86 70 92 78 90 86',
    patas: [
      [34, 90],
      [90, 87],
    ],
    brazalete: [31, 80, 20],
  },
  abajo: {
    izquierdo: 'M44 68 C36 76 34 88 37 98',
    derecho: 'M76 68 C84 76 86 88 83 98',
    patas: [
      [37, 99],
      [83, 99],
    ],
    brazalete: [34, 84, 10],
  },
  aviso: {
    izquierdo: 'M44 68 C34 72 29 82 33 90',
    // Sube por fuera de la cabeza y no sobre ella: la cabeza se dibuja después
    // y taparía una pata puesta encima de la cara.
    derecho: 'M76 66 C88 62 94 50 90 40',
    patas: [
      [33, 91],
      [89, 39],
    ],
    brazalete: [31, 80, 22],
  },
  pergamino: {
    izquierdo: 'M44 68 C34 72 31 82 34 88',
    derecho: 'M76 66 C86 66 92 62 95 56',
    patas: [
      [34, 89],
      [96, 55],
    ],
    brazalete: [32, 80, 18],
  },
}

export default function Mascota({
  estado = 'saludo',
  gala = 0,
  tamano = 120,
  etiqueta,
  className = '',
}) {
  const gesto = ESTADOS[estado] ?? ESTADOS.saludo
  const brazos = BRAZOS[gesto.pose] ?? BRAZOS.cadera
  const accesibilidad = etiqueta
    ? { role: 'img', 'aria-label': etiqueta }
    : { 'aria-hidden': 'true', focusable: 'false' }

  const clases = ['mascota', `mascota--${estado}`, className].filter(Boolean).join(' ')

  return (
    <svg
      viewBox="0 -10 120 160"
      width={tamano}
      height={(tamano * 160) / 120}
      className={clases}
      {...accesibilidad}
    >
      {/* La sombra queda fuera del grupo que respira: si respirara con él, el
          lobo parecería estar subiendo y bajando del suelo. */}
      <ellipse cx="60" cy="133" rx="27" ry="4.5" fill="var(--mascota-sombra)" />

      {gala >= 3 && <Capa />}

      <g className={`mascota__cuerpo${gesto.salta ? ' mascota__cuerpo--salta' : ''}`}>
        <Cola conMovimiento={estado !== 'dormido'} />
        <Brazos brazos={brazos} />
        <Piernas />
        <Torso />
        <Tunica />
        {brazos.patas.map(([x, y]) => (
          <circle
            key={`${x}-${y}`}
            cx={x}
            cy={y}
            r="6"
            fill="var(--mascota-pelaje-claro)"
            {...CONTORNO}
          />
        ))}
        <Brazalete x={brazos.brazalete[0]} y={brazos.brazalete[1]} giro={brazos.brazalete[2]} />
        <Lira />

        <g className="mascota__cabeza">
          <Orejas />
          <Craneo />
          <Hocico />
          <Cejas variante={gesto.cejas} />
          <Ojos variante={gesto.ojos} />
          <Boca variante={gesto.boca} />
          {gala >= 1 && <Laurel completo={gala >= 2} />}
        </g>

        {gesto.pose === 'mancuerna' && <Mancuerna />}
        {gesto.pose === 'pergamino' && <Pergamino />}
      </g>

      {gala >= 4 && <Halo />}
      {gesto.duerme && <Ronquidos />}
      {gesto.avisa && <Aviso />}
      {gesto.destellos && <Destellos />}
      {gesto.confeti && <Confeti />}
    </svg>
  )
}

/* ── Piezas ─────────────────────────────────────────────────────────────── */

function Cola({ conMovimiento }) {
  return (
    <g className={conMovimiento ? 'mascota__cola' : undefined}>
      <path
        d="M44 97 C33 103 17 102 10 91 C4 81 10 68 20 65 C16 72 16 82 22 87 C28 92 37 93 44 97 Z"
        fill="var(--mascota-pelaje)"
        {...CONTORNO}
      />
      <path
        d="M20 66 C16 73 16 82 22 87 C15 83 14 73 20 66 Z"
        fill="var(--mascota-pelaje-claro)"
        stroke="none"
      />
    </g>
  )
}

/**
 * Los brazos.
 *
 * Cada uno son dos trazos superpuestos —uno oscuro y ancho, otro de pelaje y
 * más angosto encima— porque un trazo de SVG no puede tener relleno y contorno
 * a la vez, y con un solo trazo del color del contorno los brazos se leían como
 * una mancha oscura en lugar de como brazos.
 *
 * Se dibujan ANTES del cuerpo. Dibujados después, el contorno del hombro
 * cruzaba el torso por dentro; delante de la silueta, el brazo nace de detrás
 * del cuerpo, que es de donde nace un brazo.
 */
function Brazos({ brazos }) {
  const trazos = [brazos.izquierdo, brazos.derecho]
  return (
    <g fill="none" strokeLinecap="round" strokeLinejoin="round">
      {trazos.map((trazo) => (
        <path key={`borde-${trazo}`} d={trazo} stroke="var(--mascota-contorno)" strokeWidth="15" />
      ))}
      {trazos.map((trazo) => (
        <path key={`pelo-${trazo}`} d={trazo} stroke="var(--mascota-pelaje)" strokeWidth="11" />
      ))}
    </g>
  )
}

function Piernas() {
  return (
    <g fill="var(--mascota-pelaje)" {...CONTORNO}>
      <rect x="44" y="100" width="16" height="27" rx="8" />
      <rect x="60" y="100" width="16" height="27" rx="8" />
      <path
        d="M44 119 C44 124 47.5 127 52 127 C56.5 127 60 124 60 119 Z"
        fill="var(--mascota-pelaje-claro)"
      />
      <path
        d="M60 119 C60 124 63.5 127 68 127 C72.5 127 76 124 76 119 Z"
        fill="var(--mascota-pelaje-claro)"
      />
    </g>
  )
}

function Torso() {
  return (
    <>
      <path
        d="M46 50 C41 55 38 66 38 78 L38 96 C38 100 41 103 45 103 L75 103 C79 103 82 100 82 96 L82 78 C82 66 79 55 74 50 Z"
        fill="var(--mascota-pelaje)"
        {...CONTORNO}
      />
      {/* El pecho claro asoma por encima de la túnica: sin él, la cabeza gris
          queda pegada al azul y el cuello desaparece. */}
      <path d="M48 52 C52 66 68 66 72 52 Z" fill="var(--mascota-pelaje-claro)" stroke="none" />
    </>
  )
}

/**
 * La túnica: falda acampanada, banda cruzada con ribete dorado, cinturón y
 * ribete del bajo. Se abre hacia abajo porque un rectángulo recto sobre un
 * cuerpo de cuarenta píxeles de ancho parece un delantal y no un quitón.
 */
function Tunica() {
  return (
    <g {...CONTORNO}>
      <path
        d="M45 63 L75 63 C79 73 84 88 84 99 C84 103 81 105 77 105 L43 105 C39 105 36 103 36 99 C36 88 41 73 45 63 Z"
        fill="var(--mascota-toga)"
      />
      <path d="M48 63 L56 63 L74 101 L66 101 Z" fill="var(--mascota-toga-sombra)" />
      <g stroke="var(--mascota-oro)" strokeWidth="1.6" fill="none" strokeLinecap="round">
        <path d="M49 65 L67 99" />
        <path d="M55 65 L73 99" />
      </g>
      <rect x="39" y="83" width="42" height="6" rx="3" fill="var(--mascota-oro)" />
    </g>
  )
}

/**
 * Brazalete dorado del brazo izquierdo. Se dibuja aparte de la túnica y después
 * de los brazos porque su sitio depende de la pose.
 */
function Brazalete({ x, y, giro }) {
  return (
    <rect
      x={x - 7}
      y={y - 3.5}
      width="14"
      height="7"
      rx="3.5"
      transform={`rotate(${giro} ${x} ${y})`}
      fill="var(--mascota-oro)"
      stroke="var(--mascota-oro-sombra)"
      strokeWidth="1"
    />
  )
}

/** La lira prendida al pecho: es lo que la vuelve reconocible de lejos. */
function Lira() {
  return (
    <g
      stroke="var(--mascota-oro)"
      strokeWidth="2"
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M68 80 C65.5 80 64.5 78 65.5 76 L78.5 76 C79.5 78 78.5 80 76 80 Z" />
      <path d="M67 76 C63 70 65 65 68 64" />
      <path d="M77 76 C81 70 79 65 76 64" />
      <path d="M67.5 64.5 L76.5 64.5" />
      <g strokeWidth="1.1">
        <path d="M69.5 65.5 L69.5 75.5" />
        <path d="M72 65.5 L72 75.5" />
        <path d="M74.5 65.5 L74.5 75.5" />
      </g>
    </g>
  )
}

function Orejas() {
  return (
    <g {...CONTORNO}>
      <path d="M40 24 C36 15 33 6 35 3 C40 4 51 11 54 18 Z" fill="var(--mascota-pelaje)" />
      <path d="M80 24 C84 15 87 6 85 3 C80 4 69 11 66 18 Z" fill="var(--mascota-pelaje)" />
      <path
        d="M42 21 C39 14 37 9 38 7 C42 9 48 14 50 19 Z"
        fill="var(--mascota-pelaje-claro)"
        strokeWidth="1.4"
      />
      <path
        d="M78 21 C81 14 83 9 82 7 C78 9 72 14 70 19 Z"
        fill="var(--mascota-pelaje-claro)"
        strokeWidth="1.4"
      />
    </g>
  )
}

function Craneo() {
  return (
    <path
      d="M60 10 C75 10 85 22 85 36 C85 49 75 58 60 58 C45 58 35 49 35 36 C35 22 45 10 60 10 Z"
      fill="var(--mascota-pelaje)"
      {...CONTORNO}
    />
  )
}

function Hocico() {
  return (
    <>
      <path
        d="M60 29 C70 29 77 38 77 47 C77 55 69 59 60 59 C51 59 43 55 43 47 C43 38 50 29 60 29 Z"
        fill="var(--mascota-pelaje-claro)"
        stroke="none"
      />
      <path
        d="M60 38 C64 38 66.5 40 66.5 42.5 C66.5 45.2 63.8 47 60 47 C56.2 47 53.5 45.2 53.5 42.5 C53.5 40 56 38 60 38 Z"
        fill="var(--mascota-contorno)"
        stroke="none"
      />
      <ellipse cx="57.6" cy="40.6" rx="1.3" ry="0.9" fill="var(--mascota-blanco)" opacity="0.55" />
    </>
  )
}

function Cejas({ variante }) {
  const trazos =
    variante === 'preocupadas'
      ? ['M44 28 C47 24 52 23 56 24', 'M76 28 C73 24 68 23 64 24']
      : variante === 'decididas'
        ? ['M44 24 C48 22 53 23 56 26', 'M76 24 C72 22 67 23 64 26']
        : ['M44 25 C47 22 53 22 56 25', 'M76 25 C73 22 67 22 64 25']

  return (
    <g stroke="var(--mascota-contorno)" strokeWidth="2.1" fill="none" strokeLinecap="round">
      {trazos.map((trazo) => (
        <path key={trazo} d={trazo} />
      ))}
    </g>
  )
}

function Ojos({ variante }) {
  if (variante === 'cerrados' || variante === 'entornados') {
    const curva = variante === 'cerrados' ? 3.4 : 2.2
    return (
      <g stroke="var(--mascota-contorno)" strokeWidth="2.2" fill="none" strokeLinecap="round">
        <path d={`M45 34 C48 ${34 + curva} 53 ${34 + curva} 56 34`} />
        <path d={`M64 34 C67 ${34 + curva} 72 ${34 + curva} 75 34`} />
      </g>
    )
  }

  if (variante === 'felices') {
    return (
      <g stroke="var(--mascota-contorno)" strokeWidth="2.4" fill="none" strokeLinecap="round">
        <path d="M45 36 C48 30 53 30 56 36" />
        <path d="M64 36 C67 30 72 30 75 36" />
      </g>
    )
  }

  return (
    <g>
      {[50, 70].map((cx) => (
        <g key={cx}>
          <ellipse
            cx={cx}
            cy="34"
            rx="5.2"
            ry="5.6"
            fill="var(--mascota-blanco)"
            stroke="var(--mascota-contorno)"
            strokeWidth="1.6"
          />
          <circle cx={cx + 0.7} cy="34.4" r="3.4" fill="var(--mascota-ojo)" />
          <circle cx={cx + 0.7} cy="34.4" r="1.7" fill="var(--mascota-contorno)" />
          <circle cx={cx - 1.4} cy="32.2" r="1.2" fill="var(--mascota-blanco)" />
        </g>
      ))}
    </g>
  )
}

function Boca({ variante }) {
  if (variante === 'abierta') {
    return (
      <g {...CONTORNO} strokeWidth="2">
        <path
          d="M52 49 C54 57 66 57 68 49 C64 51 56 51 52 49 Z"
          fill="var(--mascota-contorno)"
        />
        <path d="M56 53 C57 57 63 57 64 53 Z" fill="var(--mascota-lengua)" strokeWidth="1.2" />
      </g>
    )
  }

  const trazo =
    variante === 'preocupada'
      ? 'M54 54 C57 50 63 50 66 54'
      : variante === 'dormida'
        ? 'M55 52 C58 55 62 55 65 52'
        : 'M53 50 C56 55 64 55 67 50'

  return (
    <path
      d={trazo}
      stroke="var(--mascota-contorno)"
      strokeWidth="2.2"
      fill="none"
      strokeLinecap="round"
    />
  )
}

/* ── Atavío por nivel ───────────────────────────────────────────────────── */

/** Una hoja de laurel, colocada por transformación para no repetir la curva. */
function Hoja({ x, y, giro }) {
  return (
    <path
      d="M0 0 C2.5 -3.6 7 -3.6 9 0 C7 3.6 2.5 3.6 0 0 Z"
      transform={`translate(${x} ${y}) rotate(${giro})`}
      fill="var(--mascota-oro)"
      stroke="var(--mascota-oro-sombra)"
      strokeWidth="0.8"
    />
  )
}

function Laurel({ completo }) {
  const hojas = completo
    ? [
        { x: 34, y: 27, giro: -120 },
        { x: 36, y: 20, giro: -100 },
        { x: 41, y: 14, giro: -70 },
        { x: 49, y: 10, giro: -40 },
        { x: 86, y: 27, giro: -60 },
        { x: 84, y: 20, giro: -80 },
        { x: 79, y: 14, giro: -110 },
        { x: 71, y: 10, giro: -140 },
      ]
    : [
        { x: 36, y: 23, giro: -110 },
        { x: 84, y: 23, giro: -70 },
      ]

  return (
    <g>
      <path
        d="M35 25 C43 16 77 16 85 25"
        stroke="var(--mascota-oro)"
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
      />
      {hojas.map((hoja) => (
        <Hoja key={`${hoja.x}-${hoja.y}`} {...hoja} />
      ))}
    </g>
  )
}

/**
 * La capa del séptimo nivel. Va detrás de todo —por eso vive fuera del grupo
 * del cuerpo— y es más ancha que el torso: una capa que no asoma por los
 * costados no se ve.
 */
function Capa() {
  return (
    <path
      className="mascota__capa"
      d="M46 56 C26 74 20 106 26 124 L94 124 C100 106 94 74 74 56 Z"
      fill="var(--mascota-capa)"
      stroke="var(--mascota-capa-borde)"
      strokeWidth="2"
      strokeLinejoin="round"
    />
  )
}

function Halo() {
  return (
    <g className="mascota__halo">
      <ellipse
        cx="60"
        cy="-4"
        rx="21"
        ry="5"
        fill="none"
        stroke="var(--mascota-oro)"
        strokeWidth="2.6"
      />
      <ellipse
        cx="60"
        cy="-4"
        rx="21"
        ry="5"
        fill="none"
        stroke="var(--mascota-blanco)"
        strokeWidth="0.9"
        opacity="0.5"
      />
    </g>
  )
}

/* ── Añadidos de estado ─────────────────────────────────────────────────── */

function Mancuerna() {
  return (
    <g fill="var(--mascota-contorno)" {...CONTORNO} strokeWidth="1.6">
      <rect x="86" y="84.5" width="18" height="4.5" rx="2.2" />
      <rect x="84" y="79" width="5.5" height="16" rx="2.6" />
      <rect x="100" y="79" width="5.5" height="16" rx="2.6" />
    </g>
  )
}

function Pergamino() {
  return (
    <g {...CONTORNO} strokeWidth="1.7">
      <rect x="96" y="48" width="16" height="11" rx="2" fill="var(--mascota-blanco)" />
      <rect x="93" y="47" width="5" height="13" rx="2.5" fill="var(--mascota-oro)" />
      <rect x="110" y="47" width="5" height="13" rx="2.5" fill="var(--mascota-oro)" />
      <g stroke="var(--mascota-contorno)" strokeWidth="1.1" opacity="0.5">
        <path d="M100 51 L108 51" />
        <path d="M100 55 L106 55" />
      </g>
    </g>
  )
}

function Ronquidos() {
  return (
    <g
      className="mascota__ronquidos"
      stroke="var(--brand-accent-ink)"
      strokeWidth="2"
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path className="mascota__ronquido mascota__ronquido--1" d="M90 28 L99 28 L90 38 L99 38" />
      <path
        className="mascota__ronquido mascota__ronquido--2"
        d="M101 12 L108 12 L101 20 L108 20"
        strokeWidth="1.7"
      />
      <path
        className="mascota__ronquido mascota__ronquido--3"
        d="M109 0 L114 0 L109 6 L114 6"
        strokeWidth="1.4"
      />
    </g>
  )
}

function Aviso() {
  return (
    <g className="mascota__aviso">
      <circle
        cx="18"
        cy="20"
        r="11"
        fill="var(--c-warn-solid)"
        stroke="var(--mascota-contorno)"
        strokeWidth="2"
      />
      <path
        d="M18 14 L18 22"
        stroke="var(--mascota-blanco)"
        strokeWidth="2.6"
        strokeLinecap="round"
      />
      <circle cx="18" cy="26" r="1.7" fill="var(--mascota-blanco)" />
    </g>
  )
}

function Destellos() {
  const estrellas = [
    { x: 16, y: 26, r: 5 },
    { x: 104, y: 52, r: 4 },
    { x: 22, y: 58, r: 3.2 },
  ]
  return (
    <g className="mascota__destellos" fill="var(--brand-accent)">
      {estrellas.map(({ x, y, r }, indice) => (
        <path
          key={`${x}-${y}`}
          className={`mascota__destello mascota__destello--${indice + 1}`}
          d={`M${x} ${y - r} L${x + r * 0.32} ${y - r * 0.32} L${x + r} ${y} L${x + r * 0.32} ${
            y + r * 0.32
          } L${x} ${y + r} L${x - r * 0.32} ${y + r * 0.32} L${x - r} ${y} L${x - r * 0.32} ${
            y - r * 0.32
          } Z`}
        />
      ))}
    </g>
  )
}

function Confeti() {
  const piezas = [
    { x: 22, y: -6, color: 'var(--c-warn-solid)' },
    { x: 40, y: -10, color: 'var(--brand-accent)' },
    { x: 62, y: -8, color: 'var(--c-info-solid)' },
    { x: 84, y: -10, color: 'var(--c-warn-solid)' },
    { x: 100, y: -4, color: 'var(--brand-accent)' },
  ]
  return (
    <g className="mascota__confeti">
      {piezas.map((pieza, indice) => (
        <rect
          key={`${pieza.x}-${pieza.y}`}
          className={`mascota__papelillo mascota__papelillo--${indice + 1}`}
          x={pieza.x}
          y={pieza.y}
          width="4"
          height="7"
          rx="1.5"
          fill={pieza.color}
        />
      ))}
    </g>
  )
}
