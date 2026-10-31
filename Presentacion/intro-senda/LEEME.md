# Senda · Tu siguiente paso

Entrega local, 31 de octubre de 2026. Corto de 30 segundos, horizontal 16:9,
con música instrumental original, animación y texto en español. Sin voz,
según la preferencia del autor. No se publicó el sitio.

## Archivos para usar

- `senda-intro-web-1080p.mp4`: versión Full HD para uso promocional. Termina en
  «Tu siguiente paso empieza hoy» y «Crea tu cuenta gratis».
- `senda-intro-presentacion-1080p.mp4`: misma introducción, con cierre de proyecto
  de graduación, nombre del autor y universidad. Insertarla al comienzo del video
  explicativo; iniciar la explicación propia al terminar el segundo 30.
- `senda-musica-original.wav`: banda instrumental separada, estéreo a 48 kHz.
- `senda-portada.png`: portada de la pieza.
- `senda-guion-visual.jpg`: seis escenas para revisar de un vistazo.
- `generar_intro.py`: fuente editable de los gráficos, animación, composición
  musical y exportación. No se utilizan servicios pagados ni material de stock.
- `manifiesto.json`: especificaciones y tiempos de escenas.

Ambos másteres son H.264/AAC, 1920 × 1080, 30 fotogramas por segundo, con
`faststart`. La música no requiere añadir atribución a un proveedor de stock;
es una composición procedimental realizada para esta entrega. No se afirma
exclusividad registral ni se ha efectuado un registro de derechos.

## Mensaje y estructura

| Tiempo | Idea | Propósito creativo |
|---|---|---|
| 0–4 s | Quieres empezar. ¿Por dónde? | Reconocer una duda cotidiana sin culpabilizar. |
| 4–8 s | Senda: entrenamiento, alimentación y tu progreso. | Explicar rápidamente qué es el sistema. |
| 8–13 s | Ten claro qué entrenar hoy. | Mostrar rutina y registro de series. |
| 13–18 s | Organiza tus comidas. | Explicar menú, porciones y compras. |
| 18–24 s | Cada paso cuenta. | Mostrar seguimiento y logros individuales. |
| 24–30 s | Dar el primer paso / cierre según versión. | Invitar a actuar o abrir la presentación académica. |

La pieza busca identificación, claridad y una acción sencilla. Su eficacia
promocional todavía no se ha medido con personas ni mediante un experimento.
No promete resultados físicos, reducción de peso ni eficacia clínica.
Las interfaces son esquemas conceptuales, identificados como tales; las barras
no representan resultados de participantes. No anuncia funciones sociales.

## Integración en la portada

El componente `frontend/src/publico/IntroSenda.jsx` se incorpora después del
encabezado principal, antes de los pasos de registro. Incluye controles nativos,
reproducción iniciada por la persona, vista en línea en móvil, texto alternativo
al contenido visual, transcripción desplegable y acceso al registro o al panel.

Recursos públicos, con rutas versionadas:

- `/media/senda-intro-v1.mp4`: copia optimizada a 1280 × 720 para web.
- `/media/senda-intro-poster-v1.webp`: portada ligera.

`preload="none"` solicita no descargar el video anticipadamente. No hay
reproducción automática ni bucle; el movimiento comienza por decisión de la
persona. El video no se incluye en la precaché de la PWA. No añade bibliotecas
al cliente ni altera backend, migraciones, tesis o comunidad.

## Reproducir las exportaciones

Con Python, Pillow, numpy e imageio-ffmpeg instalados, desde la raíz del proyecto:

```powershell
python Presentacion/intro-senda/generar_intro.py
```

Para regenerar solo las muestras visuales:

```powershell
python Presentacion/intro-senda/generar_intro.py --preview
```

El script usa las fuentes Segoe UI de Windows y respeta la geometría Camino y
los colores de Senda. Las exportaciones sustituyen únicamente los archivos
generados de esta entrega y sus dos recursos de video/portada en `public/media`.
