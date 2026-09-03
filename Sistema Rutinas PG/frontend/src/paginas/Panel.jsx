import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { OBJETIVOS, etiquetaDe } from '../datos/catalogos.js'
import { useSesion } from '../contexto/ContextoSesion.jsx'
import { servicioPerfil } from '../servicios/api.js'

/** Módulos previstos en la pila de producto (Tabla 11 del Capítulo IV). */
const MODULOS = [
  {
    titulo: 'Perfil biométrico',
    detalle: 'Registro de peso, estatura, edad, sexo, nivel de actividad y objetivo.',
    iteracion: 2,
    historias: 'HU-04 y HU-05',
    disponible: true,
  },
  {
    titulo: 'Plan nutricional',
    detalle: 'Cálculo del requerimiento energético y la distribución de macronutrientes.',
    iteracion: 3,
    historias: 'HU-06',
    disponible: true,
  },
  {
    titulo: 'Rutina de entrenamiento',
    detalle: 'Sesiones semanales con series, repeticiones y repeticiones en reserva.',
    iteracion: 3,
    historias: 'HU-07',
    disponible: true,
  },
  {
    titulo: 'Catálogo local',
    detalle: 'Alimentos y ejercicios disponibles en el municipio.',
    iteracion: 4,
    historias: 'HU-08 y HU-11',
    disponible: true,
  },
  {
    titulo: 'Seguimiento del progreso',
    detalle: 'Registro semanal de avance, reajuste del plan y reportes gráficos.',
    iteracion: 5,
    historias: 'HU-09 y HU-10',
    disponible: true,
  },
]

function fechaLegible(valor) {
  if (!valor) return 'Sin registro'
  return new Date(valor).toLocaleString('es-GT', {
    dateStyle: 'long',
    timeStyle: 'short',
  })
}

/** Panel principal del usuario autenticado. */
export default function Panel() {
  const { usuario, esAdministrador, token } = useSesion()

  const [perfil, setPerfil] = useState(null)
  const [consultando, setConsultando] = useState(true)

  // El perfil vigente determina si el usuario ya puede avanzar hacia su plan:
  // el apartado 4.8.3 impide generarlo mientras el perfil esté incompleto.
  useEffect(() => {
    let vigente = true
    servicioPerfil
      .consultarVigente(token)
      .then((datos) => {
        if (vigente) setPerfil(datos)
      })
      .catch(() => {
        if (vigente) setPerfil(null)
      })
      .finally(() => {
        if (vigente) setConsultando(false)
      })
    return () => {
      vigente = false
    }
  }, [token])

  return (
    <div className="row g-4">
      <div className="col-12">
        <h1 className="h3 mb-1">Hola, {usuario?.nombre}</h1>
        <p className="texto-ayuda mb-0">
          Su cuenta está activa. Aquí verá sus planes de nutrición y entrenamiento conforme
          se habiliten los módulos del sistema.
        </p>
      </div>

      {!consultando && (
        <div className="col-12">
          {perfil ? (
            <div className="card shadow-sm">
              <div className="card-body d-flex flex-column flex-md-row justify-content-between gap-3">
                <div>
                  <h2 className="h5 card-title">Su perfil biométrico está completo</h2>
                  <p className="texto-ayuda mb-0">
                    Última medición del {fechaLegible(perfil.fecha_registro)}: {perfil.peso_kg} kg
                    y {perfil.estatura_cm} cm, con índice de masa corporal de{' '}
                    {perfil.indice_masa_corporal} ({perfil.clasificacion_masa_corporal}).
                    Objetivo declarado: {etiquetaDe(OBJETIVOS, perfil.objetivo).toLowerCase()}.
                  </p>
                </div>
                <Link
                  to="/historial-medidas"
                  className="btn btn-outline-secondary control-tactil align-self-start flex-shrink-0"
                >
                  Ver mi historial
                </Link>
              </div>
            </div>
          ) : (
            <div className="card shadow-sm border-warning">
              <div className="card-body d-flex flex-column flex-md-row justify-content-between gap-3">
                <div>
                  <h2 className="h5 card-title">Complete su perfil biométrico</h2>
                  <p className="texto-ayuda mb-0">
                    Sin sus medidas el sistema no puede calcular su requerimiento de
                    energía ni armar su rutina. Toma menos de dos minutos.
                  </p>
                </div>
                <Link
                  to="/perfil-biometrico"
                  className="btn btn-principal control-tactil align-self-start flex-shrink-0"
                >
                  Registrar mis medidas
                </Link>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="col-12 col-lg-5">
        <div className="card shadow-sm h-100">
          <div className="card-body">
            <h2 className="h5 card-title">Datos de la cuenta</h2>
            <dl className="row mb-0 mt-3">
              <dt className="col-5 col-sm-4">Nombre</dt>
              <dd className="col-7 col-sm-8">{usuario?.nombre}</dd>

              <dt className="col-5 col-sm-4">Correo</dt>
              <dd className="col-7 col-sm-8 text-break">{usuario?.correo}</dd>

              <dt className="col-5 col-sm-4">Rol</dt>
              <dd className="col-7 col-sm-8">
                <span className={`badge ${esAdministrador ? 'bg-warning text-dark' : 'bg-success'}`}>
                  {esAdministrador ? 'Administrador' : 'Usuario deportista'}
                </span>
              </dd>

              <dt className="col-5 col-sm-4">Registro</dt>
              <dd className="col-7 col-sm-8">{fechaLegible(usuario?.fecha_registro)}</dd>

              <dt className="col-5 col-sm-4">Último acceso</dt>
              <dd className="col-7 col-sm-8 mb-0">{fechaLegible(usuario?.ultimo_acceso)}</dd>
            </dl>
          </div>
        </div>
      </div>

      <div className="col-12 col-lg-7">
        <div className="card shadow-sm h-100">
          <div className="card-body">
            <h2 className="h5 card-title">Módulos del sistema</h2>
            <p className="texto-ayuda">
              Todas las historias de usuario del sistema se encuentran en
              funcionamiento.
            </p>
            <ul className="list-group list-group-flush">
              {MODULOS.map((modulo) => (
                <li
                  key={modulo.titulo}
                  className="list-group-item d-flex justify-content-between align-items-start gap-3 px-0"
                >
                  <div>
                    <div className="fw-semibold">{modulo.titulo}</div>
                    <div className="texto-ayuda">{modulo.detalle}</div>
                    <div className="texto-ayuda">Historias {modulo.historias}</div>
                  </div>
                  <span
                    className={`badge flex-shrink-0 ${
                      modulo.disponible ? 'bg-success' : 'bg-secondary'
                    }`}
                  >
                    {modulo.disponible ? 'Disponible' : `Iteración ${modulo.iteracion}`}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
