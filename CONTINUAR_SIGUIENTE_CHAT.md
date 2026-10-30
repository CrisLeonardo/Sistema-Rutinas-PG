# Continuar fase 7 con alcance individual

Lee `PLAN_MAESTRO_EVOLUCION.md` y los informes de `Sistema Rutinas PG/operaciones`,
en especial `FASE_7_VALIDACION_INDIVIDUAL.md`. Conserva los cambios locales.

El autor decidió posponer amigos, grupos, invitaciones y retos sociales. La entrega
actual conserva Mi senda individual: puntos, niveles, insignias e historial. La ruta
antigua `/avance/amigos` redirige a `/avance/senda`. El backend social permanece
apagado por defecto; sus archivos y la revisión 0005 se conservan, sin borrar datos.
No reactivarlo al retomar y no seguir el guion social como alcance vigente.

La fase 7 tiene regresión técnica, retiro social, inferencia para una fila,
admisión asíncrona (cinco solicitudes activas por proceso), instrumentos de carga
corregidos, respaldo/restauración de 25 tablas y revisión parcial en navegador.
Suite final: 812 aprobadas y 4 omitidas; cliente: 21 + 11 aprobadas, construcción correcta.
Ver `evidencias/fase7/suite-configuracion-final.xml` para la última suite y los
JSON de carga. Hay ensayos favorables y fallidos: la estabilidad de 50 usuarios
no está acreditada. El primer plan desde proceso nuevo tardó 7.46 s; no cumple 3 s.
No presentar solo el mejor ensayo como cumplimiento ni excluir la espera sin decirlo.

Siguen pendientes Gmail real, dictámenes de diez ejercicios y 18 recetas (incluida
la dosis de plancha), participantes, teléfono/red móvil real, publicación y copia
versionada de tesis. El autor confirmó que todavía no tiene los recursos externos.
Están listos `PILOTO_INDIVIDUAL_FASE7.md` y `CAMBIOS_TESIS_FASE_7.md`; no contienen
sesiones humanas ni dictámenes inventados.

Cliente de revisión: `http://127.0.0.1:15176`, API UI: `127.0.0.1:18160`, con la
base ficticia de fase 6 para comprobar puntos conservados. Ensayos de carga:
API `127.0.0.1:18170`, base identificada en `evidencias/fase7/base-ui.txt`. Los
procesos pueden necesitar reinicio al retomar. Ninguna de esas cuentas describe
personas reales. No hubo despliegue ni migración de producción.
