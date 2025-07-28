import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Use the new Tailored Agents dashboard
const AppComponent = App

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppComponent />
  </StrictMode>,
)
