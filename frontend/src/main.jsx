import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './metamask-polyfill.js' // Load MetaMask polyfill
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)
