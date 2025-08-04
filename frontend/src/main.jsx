import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App-debug.jsx'

// Use the debug version to test component errors
const AppComponent = App

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppComponent />
  </StrictMode>,
)
