/** Conserva cada resultado y distingue ausencia real de una consulta fallida. */
export async function cargarRecursos(recursos) {
  const claves = Object.keys(recursos)
  const resultados = await Promise.allSettled(Object.values(recursos))
  const datos = {}, fallos = {}
  resultados.forEach((resultado, i) => {
    const clave = claves[i]
    datos[clave] = resultado.status === 'fulfilled' ? resultado.value : null
    if (resultado.status === 'rejected') fallos[clave] = resultado.reason
  })
  return { ...datos, fallos }
}
