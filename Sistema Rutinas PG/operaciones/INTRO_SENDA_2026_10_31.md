# Corto introductorio de Senda

31 de octubre de 2026, Guatemala. Implementación y entrega local.

Se preparó una pieza audiovisual de 30 segundos con música instrumental original,
gráficos de Senda y texto en español, sin locución por elección del autor.
Hay dos exportaciones Full HD: cierre promocional para web y cierre académico
para abrir el video del proyecto de graduación. Fuentes, música y guion en
`Presentacion/intro-senda/`, junto con instrucciones de reproducción.

La portada pública incorpora una copia H.264/AAC a 720p y una portada WebP.
El reproductor tiene controles, `playsInline`, `preload="none"`, sin autoplay,
sin bucle y con contenido escrito desplegable. No se incluyó el MP4 en la
precaché PWA. La llamada a la acción lleva a registro o panel según la sesión.

Las funciones explicadas son entrenamiento, alimentación y avance individual.
Las imágenes de interfaz son conceptuales, sin datos de participantes ni
resultados físicos. La pieza no afirma eficacia clínica ni eficacia de marketing
medida. No se modificaron API, reglas de negocio, migraciones ni tesis.
`COMUNIDAD_HABILITADA=false` permanece fuera del alcance de este cambio.

La compilación del cliente y el verificador de las diez páginas públicas y los
seis armazones privados finalizaron correctamente. La primera compilación falló
por una dependencia local ausente (`vite-plugin-pwa`); se instalaron las
dependencias ya declaradas sin modificar `package.json` ni su archivo de bloqueo,
y la nueva compilación pasó. No se volvió a ejecutar la suite histórica del
servidor ni se sumaron sus cifras a las de otras revisiones.

Los tres MP4 finales (dos másteres y copia web) se decodificaron completos sin
errores y conservan `faststart`; sus SHA-256 y tamaños están en
`Presentacion/intro-senda/verificacion-exportaciones.json`. La copia web ocupa
1,325,180 bytes y su portada 32,828 bytes. Ambos másteres son Full HD a 30 fps.

En navegador se comprobó reproducción hasta el final, duración nominal de 30 s,
ausencia de error de video y aparición de los controles al iniciar. Antes del
clic el reproductor permanecía pausado, con `readyState=0` y sin autoplay. El
botón sobre la portada tiene nombre accesible y todo el póster inicia el corto.
El enlace del encabezado lleva al bloque del video; la transcripción está en
el HTML público. En la comprobación a 320 px, el ancho del documento fue 305 px
y el video ocupó 268 px, sin desbordamiento. Esto es emulación de escritorio,
no prueba en teléfono físico. Se restauró el tamaño del navegador.
La captura de integración está en `Presentacion/intro-senda/portada-web-revision.png`.

La revisión de esta pieza no cierra la fase 7, las validaciones humanas, teléfono
físico, revisión profesional, primera generación ni estabilidad de 50 usuarios.
No hubo publicación, migración de producción ni cambios a la tesis de 667 pruebas.
