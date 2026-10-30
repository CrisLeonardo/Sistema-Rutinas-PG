import { Link } from 'react-router-dom'
import { useSesion } from '../contexto/ContextoSesion.jsx'

export default function Bienvenida() {
  const { usuario } = useSesion()
  return <section className="bienvenida-senda pila-5"><p className="rotulo">TU PRIMER PASO</p><h1 className="titulo-grande">Tu cuenta está lista, {usuario?.nombre?.split(' ')[0]}.</h1><p className="cuerpo">Ahora vamos a preparar tu recorrido. Tus datos ayudan al sistema a ajustar el plan y a reconocer situaciones que necesitan orientación profesional.</p><ol className="bienvenida-pasos"><li><strong>Tu perfil</strong><span>Medidas, actividad, objetivo y antecedentes relevantes.</span></li><li><strong>Tu plan</strong><span>Alimentación y rutina, con las advertencias que correspondan.</span></li><li><strong>Tu día</strong><span>Una acción clara para entrenar, comer y registrar tu avance.</span></li></ol><Link to="/avance/medidas/editar?inicio=1" className="boton boton--principal">Completar mi perfil</Link><p className="apoyo">Necesitas tener 18 años cumplidos o más. Completa los datos a tu ritmo.</p><Link to="/panel" className="boton boton--secundario">Continuar más tarde</Link></section>
}
