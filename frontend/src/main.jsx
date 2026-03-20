import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'

// Register service worker for PWA offline support (REM-039)
if ('serviceWorker' in navigator) {
  if (import.meta.env.PROD) {
    // Production: register SW for offline support
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch(() => {
        // SW registration failure is non-fatal
      })
    })
  } else {
    // Development: unregister any existing SW + clear all caches to avoid serving stale Vite modules
    navigator.serviceWorker.getRegistrations().then(async (registrations) => {
      for (const registration of registrations) {
        await registration.unregister()
      }
      if (registrations.length > 0) {
        const cacheNames = await caches.keys()
        await Promise.all(cacheNames.map(name => caches.delete(name)))
        window.location.reload()
      }
    })
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
