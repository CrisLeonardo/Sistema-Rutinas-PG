import { Navigate, Route, Routes } from 'react-router-dom'

import BarraNavegacion from './componentes/BarraNavegacion.jsx'
import RutaProtegida from './componentes/RutaProtegida.jsx'
import { useSesion } from './contexto/ContextoSesion.jsx'
import AvisoDeSesion from './componentes/AvisoDeSesion.jsx'
import Acceso from './paginas/Acceso.jsx'
import AdministracionCatalogos from './paginas/AdministracionCatalogos.jsx'
import AdministracionCuentas from './paginas/AdministracionCuentas.jsx'
import AjustesCuenta from './paginas/AjustesCuenta.jsx'
import BitacoraSesion from './paginas/BitacoraSesion.jsx'
import HistorialEntrenamiento from './paginas/HistorialEntrenamiento.jsx'
import HistorialMedidas from './paginas/HistorialMedidas.jsx'
import ListaDeCompras from './paginas/ListaDeCompras.jsx'
import MenuDiario from './paginas/MenuDiario.jsx'
import Panel from './paginas/Panel.jsx'
import PerfilBiometrico from './paginas/PerfilBiometrico.jsx'
import PlanNutricional from './paginas/PlanNutricional.jsx'
import Registro from './paginas/Registro.jsx'
import RegistroProgreso from './paginas/RegistroProgreso.jsx'
import Reportes from './paginas/Reportes.jsx'
import Rutina from './paginas/Rutina.jsx'

export default function App() {
  const { autenticado } = useSesion()

  return (
    <>
      <BarraNavegacion />
      <AvisoDeSesion />
      <main className="container py-4 contenido-principal">
        <Routes>
          <Route
            path="/acceso"
            element={autenticado ? <Navigate to="/panel" replace /> : <Acceso />}
          />
          <Route
            path="/registro"
            element={autenticado ? <Navigate to="/panel" replace /> : <Registro />}
          />
          <Route
            path="/panel"
            element={
              <RutaProtegida>
                <Panel />
              </RutaProtegida>
            }
          />
          <Route
            path="/perfil-biometrico"
            element={
              <RutaProtegida>
                <PerfilBiometrico />
              </RutaProtegida>
            }
          />
          <Route
            path="/historial-medidas"
            element={
              <RutaProtegida>
                <HistorialMedidas />
              </RutaProtegida>
            }
          />
          <Route
            path="/plan-nutricional"
            element={
              <RutaProtegida>
                <PlanNutricional />
              </RutaProtegida>
            }
          />
          <Route
            path="/rutina"
            element={
              <RutaProtegida>
                <Rutina />
              </RutaProtegida>
            }
          />
          <Route
            path="/progreso"
            element={
              <RutaProtegida>
                <RegistroProgreso />
              </RutaProtegida>
            }
          />
          <Route
            path="/reportes"
            element={
              <RutaProtegida>
                <Reportes />
              </RutaProtegida>
            }
          />
          <Route
            path="/menu"
            element={
              <RutaProtegida>
                <MenuDiario />
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
          <Route
            path="/bitacora"
            element={
              <RutaProtegida>
                <HistorialEntrenamiento />
              </RutaProtegida>
            }
          />
          <Route
            path="/compras"
            element={
              <RutaProtegida>
                <ListaDeCompras />
              </RutaProtegida>
            }
          />
          <Route
            path="/cuenta"
            element={
              <RutaProtegida>
                <AjustesCuenta />
              </RutaProtegida>
            }
          />
          <Route
            path="/catalogos"
            element={
              <RutaProtegida soloAdministrador>
                <AdministracionCatalogos />
              </RutaProtegida>
            }
          />
          <Route
            path="/cuentas"
            element={
              <RutaProtegida soloAdministrador>
                <AdministracionCuentas />
              </RutaProtegida>
            }
          />
          <Route path="/" element={<Navigate to={autenticado ? '/panel' : '/acceso'} replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  )
}
