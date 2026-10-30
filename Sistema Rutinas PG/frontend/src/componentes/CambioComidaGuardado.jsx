import { quetzales } from '../utilidades/formatos.js'

const precio = valor => valor == null ? 'Precio incompleto' : quetzales(valor)

export default function CambioComidaGuardado({ cambio, alCerrar }) {
  return <section className="tarjeta cambio-comida pila-3" aria-label="Comparación de la comida cambiada">
    <h2 className="titulo-tarjeta">Cambio guardado · día {cambio.dia}</h2>
    <p className="apoyo">{cambio.tiempo}. Las porciones y las compras ya están actualizadas.</p>
    <dl>
      <dt>Receta</dt><dd>Antes: {cambio.antes.receta}</dd><dd>Ahora: {cambio.despues.receta}</dd>
      {[['energia_kcal', 'Energía', 'kcal'], ['proteina_g', 'Proteína', 'g'], ['carbohidrato_g', 'Carbohidratos', 'g'], ['grasa_g', 'Grasa', 'g']].map(([k, texto, unidad]) => <div key={k} className="cambio-comida__fila"><dt>{texto}</dt><dd>Antes: {cambio.antes[k]} {unidad}</dd><dd>Ahora: {cambio.despues[k]} {unidad}</dd></div>)}
      <dt>Costo estimado de la comida</dt><dd>Antes: {precio(cambio.antes.costo_quetzales)}</dd><dd>Ahora: {precio(cambio.despues.costo_quetzales)}</dd>
      <dt>Costo estimado de los siete días</dt><dd>Antes: {precio(cambio.costoSemanaAntes)}</dd><dd>Ahora: {precio(cambio.costoSemanaDespues)}</dd>
    </dl>
    <details><summary>Comparar porciones antes y después</summary><div className="cambio-comida__porciones">{[['antes', 'Antes'], ['despues', 'Ahora']].map(([k, texto]) => <div key={k}><h3>{texto}</h3><ul>{cambio[k].porciones.map(p => <li key={p.nombre}>{p.nombre}: {p.gramos} g · {p.estado}</li>)}</ul></div>)}</div></details>
    <button className="boton-texto" onClick={alCerrar}>Cerrar comparación</button>
  </section>
}
