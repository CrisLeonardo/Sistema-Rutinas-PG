/**
 * Anillo de avance con la mascota dentro.
 *
 * Es la pieza protagonista de la senda: el lobo dentro de un arco que se cierra
 * conforme el usuario se acerca al nivel siguiente. Se dibuja con un solo
 * círculo y `stroke-dasharray`, que es la forma de hacer un anillo de progreso
 * sin una segunda biblioteca, igual que las gráficas de los reportes.
 *
 * El anillo es decorativo: la misma cifra va escrita al lado, y anunciarla dos
 * veces obligaría al lector de pantalla a leerla dos veces.
 */

import Mascota from './Mascota.jsx'

export default function AnilloNivel({
  porcentaje = 0,
  estado = 'saludo',
  gala = 0,
  tamano = 132,
  grosor = 7,
}) {
  const radio = (tamano - grosor) / 2
  const vuelta = 2 * Math.PI * radio
  // Se acota entre cero y cien: un porcentaje fuera de rango dejaría el arco
  // dando la vuelta sobre sí mismo.
  const avance = Math.min(Math.max(porcentaje, 0), 100)

  return (
    <div className="anillo" style={{ width: tamano, height: tamano }}>
      <svg
        className="anillo__svg"
        width={tamano}
        height={tamano}
        viewBox={`0 0 ${tamano} ${tamano}`}
        aria-hidden="true"
        focusable="false"
      >
        <circle
          className="anillo__pista"
          cx={tamano / 2}
          cy={tamano / 2}
          r={radio}
          strokeWidth={grosor}
        />
        <circle
          className="anillo__recorrido"
          cx={tamano / 2}
          cy={tamano / 2}
          r={radio}
          strokeWidth={grosor}
          strokeDasharray={vuelta}
          strokeDashoffset={vuelta * (1 - avance / 100)}
        />
      </svg>
      <span className="anillo__contenido">
        <Mascota estado={estado} gala={gala} tamano={tamano * 0.78} />
      </span>
    </div>
  )
}
