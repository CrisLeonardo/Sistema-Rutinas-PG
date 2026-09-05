import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

// Los tokens definen las variables que usan las demás hojas, de modo que
// index.css los importa primero y nada se carga por su cuenta.
import './estilos/index.css'

import App from './App.jsx'
import { ProveedorPreferencias } from './contexto/ContextoPreferencias.jsx'
import { ProveedorSesion } from './contexto/ContextoSesion.jsx'

createRoot(document.getElementById('raiz')).render(
  <StrictMode>
    <BrowserRouter>
      <ProveedorPreferencias>
        <ProveedorSesion>
          <App />
        </ProveedorSesion>
      </ProveedorPreferencias>
    </BrowserRouter>
  </StrictMode>,
)
