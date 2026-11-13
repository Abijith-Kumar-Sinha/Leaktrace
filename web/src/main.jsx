import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import './styles.css'

// Dense console: scale the whole layout with the viewport between laptop and large-desktop widths (designed at 1536px).
const fit = () => { const w = window.innerWidth, z = w >= 1100 ? Math.min(1.12, Math.max(0.8, w / 1536)) : 1
  document.documentElement.style.zoom = z; document.documentElement.style.setProperty('--z', z) }
fit(); window.addEventListener('resize', fit)
createRoot(document.getElementById('root')).render(<App />)
