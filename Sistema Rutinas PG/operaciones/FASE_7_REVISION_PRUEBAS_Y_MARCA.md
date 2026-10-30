# Revisión de pruebas y marca Senda

30 de octubre de 2026. Alcance individual; comunidad apagada.

## Marca implementada

El autor eligió **Camino: una S que termina en avance**. Se aplicó la geometría
vectorial original junto al nombre Senda en cabeceras públicas, cuentas, sistema
y administración. Se actualizaron tarjeta de insignia, favicon, icono Apple y
PWA. Las rutas con sufijo `-camino` cambian las URLs de los iconos anteriores.
No hubo publicación ni instalación en teléfono físico.

Fuente común: `frontend/src/marca/identidad.mjs`. Los PNG se reproducen mediante
`frontend/operaciones/generar-marca.mjs`, con Sharp y `--modulos` para señalar su
ubicación. No se añadió una dependencia al proyecto.

## Pruebas de esta revisión

- **21 pruebas de entrenamiento y 11 de interacción aprobadas**, después de las
  correcciones. Construcción y verificador aprobados: diez páginas públicas y
  seis armazones privados sin datos.
- Manifiesto compilado: iconos existentes con dimensiones 192 y 512 correctas,
  contenido visible; maskable sin transparencia y con la tinta dentro del círculo
  central del 80 %. Favicon PNG de 96 y Apple de 180 correctos.
- axe-core 4.14.0: portada y acceso en ambos temas, registro inicial y recuperación
  en claro, sin infracciones automáticas finales. Hay comprobaciones incompletas
  de contraste en claro y atributos/nombres en portada que requieren revisión
  manual. No acredita conformidad completa ni uso con lector de pantalla.
- Se corrigieron dos infracciones en acceso: nombre accesible Ver/Ocultar acorde
  con su texto y enlaces dentro de texto subrayados. El ajuste del botón se aplicó
  también a registro y cambio de contraseña. Se comprobó Ver/Ocultar y su estado.
- Proceso nuevo con PostgreSQL ficticio: salud **3.71 s**, primer plan neuronal
  **6.29 s**, siguiente **0.044 s**. El primero **no cumple** la meta de 3 s.
  Se conserva también el ensayo histórico de 7.46 s.
- Perfil SQL local secuencial: rutina 8 consultas; menú 12; compras 19; reporte 4;
  historial 4; juego 9. Tiempos totales entre 0.014 y 0.066 s. No se modificaron
  consultas ni fórmulas; este escenario no acredita capacidad con 50 usuarios.

Evidencia local: `evidencias/fase7-revision/`, con logs, `verificacion-iconos.json`,
`arranque.json`, `perfil-consultas.json`, auditorías y capturas de marca. Se conservan
los hallazgos iniciales. `accesibilidad-acceso-claro.json` capturó accidentalmente
«Cargando Senda» en portada; no se usa como auditoría final. Son finales los archivos
`acceso-claro-final`, `acceso-oscuro-final`, `portada-claro`, `portada-oscuro`,
`registro-claro` y `recuperacion-claro`. La inyección temporal de axe se retiró al
recargar y se restauró el tema oscuro original.

Instrumento: [API oficial de axe-core](https://github.com/dequelabs/axe-core/blob/develop/doc/API.md).

## Pendientes y límites

**El plan completo no está cerrado.** El logo y esta revisión técnica están
terminados. Los ensayos históricos de 50 usuarios incluyen fallos de tiempo;
no hay estabilidad acreditada ni una nueva repetición de carga aquí. La suite
histórica del servidor conserva 812 aprobadas y 4 omitidas: no se volvió a ejecutar
en esta revisión ni se suma a las 32 pruebas del cliente.

Al retomar la comprobación visual, Docker estaba detenido y la API no disponible.
Se reinició solo Vite en 15176. Recuperación mostró el servicio no consultable y
deshabilitó el envío. No se afirma una nueva validación privada ni de correo.

Siguen pendientes Gmail OAuth/entrega real, estabilidad y arranque, dictamen de
ejercicios y dosis/series de plancha, revisión profesional de recetas, participantes,
observación de cuatro semanas, teléfono/red móvil y accesibilidad manual completa.
También quedan publicación y actualización de tesis en copia versionada. El autor
ya indicó que no dispone de los recursos externos; no se inventaron validaciones.
Se conservaron evidencias anteriores, cambios locales y tesis de referencia.
No se borraron bases ni se reactivaron amigos/grupos.
