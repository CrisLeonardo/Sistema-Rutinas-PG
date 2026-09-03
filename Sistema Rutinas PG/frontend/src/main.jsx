import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

import 'bootstrap/dist/css/bootstrap.min.css'
// El paquete de comportamiento de Bootstrap activa el menú desplegable de la
// barra de navegación en pantallas angostas.
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import './estilos.css'

import App from './App.jsx'
import { ProveedorSesion } from './contexto/ContextoSesion.jsx'

createRoot(document.getElementById('raiz')).render(
  <StrictMode>
    <BrowserRouter>
      <ProveedorSesion>
        <App />
      </ProveedorSesion>
    </BrowserRouter>
  </StrictMode>,
)
