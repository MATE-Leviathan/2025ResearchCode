import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  // <StrictMode> // Strictmode was causing the useEffects to run twice, causing lag
    <App />
  //</StrictMode>,
)
