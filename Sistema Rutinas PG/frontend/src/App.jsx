import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'

import BarraNavegacion from './componentes/BarraNavegacion.jsx'
import RutaProtegida from './componentes/RutaProtegida.jsx'
import { useSesion } from './contexto/ContextoSesion.jsx'
import AvisoDeSesion from './componentes/AvisoDeSesion.jsx'
import AvisoInstalacion from './componentes/AvisoInstalacion.jsx'
import Acceso from './paginas/Acceso.jsx'
import AdministracionCatalogos from './paginas/AdministracionCatalogos.jsx'
import AdministracionCuentas from './paginas/AdministracionCuentas.jsx'
import AjustesCuenta from './paginas/AjustesCuenta.jsx'
import BitacoraSesion from './paginas/BitacoraSesion.jsx'
import CambioContrasena from './paginas/CambioContrasena.jsx'
import HistorialEntrenamiento from './paginas/HistorialEntrenamiento.jsx'
import HistorialMedidas from './paginas/HistorialMedidas.jsx'
import Informes from './paginas/Informes.jsx'
import ListaDeCompras from './paginas/ListaDeCompras.jsx'
import MenuDiario from './paginas/MenuDiario.jsx'
import Panel from './paginas/Panel.jsx'
import PerfilBiometrico from './paginas/PerfilBiometrico.jsx'
import PlanNutricional from './paginas/PlanNutricional.jsx'
import Registro from './paginas/Registro.jsx'
import RegistroProgreso from './paginas/RegistroProgreso.jsx'
import Reportes from './paginas/Reportes.jsx'
import Rutina from './paginas/Rutina.jsx'
import Senda from './paginas/Senda.jsx'
import Bienvenida from './paginas/Bienvenida.jsx'
import RecuperarAcceso from './paginas/RecuperarAcceso.jsx'
import MetadatosPrivados from './componentes/MetadatosPrivados.jsx'
import CabeceraCuenta from './componentes/MarcaProducto.jsx'
import { PAGINAS_PUBLICAS } from './publico/contenido.js'

const PrototipoFase1 = lazy(() => import('./prototipo/PrototipoFase1.jsx'))
const SitioPublico = lazy(() => import('./publico/SitioPublico.jsx'))
const BibliotecaEjercicios = lazy(() => import('./paginas/BibliotecaEjercicios.jsx'))
const RevisionFase3 = lazy(() => import('./prototipo/RevisionFase3.jsx'))
const AlimentacionPractica = lazy(() => import('./paginas/AlimentacionPractica.jsx'))

/**
 * Direcciones de la versión anterior. Se conservan como redirecciones porque
 * hay usuarios que las tienen guardadas en el navegador y compartidas por
 * mensaje: una dirección que deja de existir es un error que el usuario no
 * puede corregir.
 */
const RUTAS_ANTERIORES = [
  ['/menu', '/comer'],
  ['/plan-nutricional', '/comer/plan'],
  ['/compras', '/comer/compras'],
  ['/rutina', '/entrenar'],
  ['/bitacora', '/entrenar/bitacora'],
  ['/progreso', '/avance'],
  ['/reportes', '/avance/evolucion'],
  ['/historial-medidas', '/avance/medidas'],
  ['/perfil-biometrico', '/avance/medidas/editar'],
  ['/cuenta', '/mas'],
  ['/catalogos', '/admin/catalogos'],
  ['/cuentas', '/admin/cuentas'],
]

/**
 * La sesión de entrenamiento en curso es modo enfoque: sin barra de navegación,
 * porque salir a otra pantalla en mitad de una serie es un accidente, no una
 * intención. Las dos pestañas de la sección sí la conservan.
 */
function esSesionEnCurso(ruta) {
  return /^\/entrenar\/\d+\/?$/.test(ruta)
}

export default function App() {
  const { autenticado } = useSesion()
  const { pathname } = useLocation()

  if (pathname.replace(/\/+$/, '') === '/prototipo/fase-3') {
    return <Suspense fallback={<p role="status">Cargando el piloto de ejercicios…</p>}><RevisionFase3 /></Suspense>
  }

  // La fase de diseño tiene datos ficticios y navegación propia. Carga aparte
  // para poder evaluarla sin sustituir las pantallas ni la sesión existentes.
  if (pathname === '/prototipo/fase-1' || pathname.startsWith('/prototipo/fase-1/')) {
    return (
      <Suspense fallback={<p role="status">Cargando prototipo de Senda…</p>}>
        <Routes>
          <Route path="/prototipo/fase-1/*" element={<PrototipoFase1 />} />
        </Routes>
      </Suspense>
    )
  }

  if (Object.hasOwn(PAGINAS_PUBLICAS, pathname.replace(/\/+$/, '') || '/')) {
    return <Suspense fallback={<p role="status">Cargando Senda…</p>}><SitioPublico /></Suspense>
  }

  const modoEnfoque = esSesionEnCurso(pathname)
  const esAdministracion = pathname.startsWith('/admin')
  const esRecuperacion = /^\/(recuperar-acceso|restablecer-acceso)\/?$/.test(pathname)
  const sinBarra = modoEnfoque || esRecuperacion || !autenticado

  const clases = ['contenido-principal']
  if (sinBarra) clases.push('contenido-principal--enfoque')
  if (esAdministracion) clases.push('contenido-principal--administracion')

  return (
    <div className={`armazon${esAdministracion ? ' armazon--administracion' : ''}`}>
      <MetadatosPrivados />
      <main className={clases.join(' ')}>
        {autenticado && !modoEnfoque && !esRecuperacion && !esAdministracion && <div className="cabecera-producto"><CabeceraCuenta /></div>}
        <Routes>
          <Route path="/recuperar-acceso" element={<RecuperarAcceso key="solicitar" />} />
          <Route path="/restablecer-acceso" element={<RecuperarAcceso key="restablecer" restablecer />} />
          <Route path="/bienvenida" element={<RutaProtegida><Bienvenida /></RutaProtegida>} />
          <Route
            path="/acceso"
            element={autenticado ? <Navigate to="/panel" replace /> : <Acceso />}
          />
          <Route
            path="/registro"
            element={autenticado ? <Navigate to="/panel" replace /> : <Registro />}
          />

          {/* Hoy */}
          <Route
            path="/panel"
            element={
              <RutaProtegida>
                <Panel />
              </RutaProtegida>
            }
          />

          {/* Comer */}
          {['semana', 'recetas', 'preferencias'].map(vista => <Route key={vista} path={`/comer/${vista}`} element={<RutaProtegida><Suspense fallback={<p role="status">Cargando alimentación…</p>}><AlimentacionPractica key={vista} vista={vista} /></Suspense></RutaProtegida>} />)}
          <Route
            path="/comer"
            element={
              <RutaProtegida>
                <MenuDiario />
              </RutaProtegida>
            }
          />
          <Route
            path="/comer/plan"
            element={
              <RutaProtegida>
                <PlanNutricional />
              </RutaProtegida>
            }
          />
          <Route
            path="/comer/compras"
            element={
              <RutaProtegida>
                <ListaDeCompras />
              </RutaProtegida>
            }
          />

          {/* Entrenar */}
          <Route path="/entrenar/biblioteca" element={<RutaProtegida><Suspense fallback={<p role="status">Cargando biblioteca…</p>}><BibliotecaEjercicios /></Suspense></RutaProtegida>} />
          <Route path="/entrenar/biblioteca/:ejercicioId" element={<RutaProtegida><Suspense fallback={<p role="status">Cargando ficha…</p>}><BibliotecaEjercicios /></Suspense></RutaProtegida>} />
          <Route
            path="/entrenar"
            element={
              <RutaProtegida>
                <Rutina />
              </RutaProtegida>
            }
          />
          <Route
            path="/entrenar/bitacora"
            element={
              <RutaProtegida>
                <HistorialEntrenamiento vista="bitacora" />
              </RutaProtegida>
            }
          />
          <Route
            path="/entrenar/marcas"
            element={
              <RutaProtegida>
                <HistorialEntrenamiento vista="marcas" />
              </RutaProtegida>
            }
          />
          <Route
            path="/entrenar/:sesionId"
            element={
              <RutaProtegida>
                <BitacoraSesion />
              </RutaProtegida>
            }
          />

          <Route path="/avance/amigos" element={<RutaProtegida><Navigate to="/avance/senda" replace /></RutaProtegida>} />
          {/* Avance */}
          <Route
            path="/avance"
            element={
              <RutaProtegida>
                <RegistroProgreso />
              </RutaProtegida>
            }
          />
          <Route
            path="/avance/senda"
            element={
              <RutaProtegida>
                <Senda />
              </RutaProtegida>
            }
          />
          <Route
            path="/avance/evolucion"
            element={
              <RutaProtegida>
                <Reportes />
              </RutaProtegida>
            }
          />
          <Route
            path="/avance/medidas"
            element={
              <RutaProtegida>
                <HistorialMedidas />
              </RutaProtegida>
            }
          />
          <Route
            path="/avance/informes"
            element={
              <RutaProtegida>
                <Informes ambito="personal" />
              </RutaProtegida>
            }
          />
          <Route
            path="/avance/medidas/editar"
            element={
              <RutaProtegida>
                <PerfilBiometrico />
              </RutaProtegida>
            }
          />

          {/* Más */}
          <Route
            path="/mas"
            element={
              <RutaProtegida>
                <AjustesCuenta />
              </RutaProtegida>
            }
          />
          <Route
            path="/mas/contrasena"
            element={
              <RutaProtegida>
                <CambioContrasena />
              </RutaProtegida>
            }
          />
          <Route
            path="/admin/catalogos"
            element={
              <RutaProtegida soloAdministrador>
                <AdministracionCatalogos />
              </RutaProtegida>
            }
          />
          <Route
            path="/admin/informes"
            element={
              <RutaProtegida soloAdministrador>
                <Informes ambito="administracion" />
              </RutaProtegida>
            }
          />
          <Route
            path="/admin/cuentas"
            element={
              <RutaProtegida soloAdministrador>
                <AdministracionCuentas />
              </RutaProtegida>
            }
          />

          {RUTAS_ANTERIORES.map(([anterior, nueva]) => (
            <Route key={anterior} path={anterior} element={<Navigate to={nueva} replace />} />
          ))}

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      {!sinBarra && <BarraNavegacion />}
      <AvisoDeSesion />
      {!modoEnfoque && !esRecuperacion && <AvisoInstalacion conBarra={autenticado} />}
    </div>
  )
}
