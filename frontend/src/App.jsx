import { useEffect, useState } from 'react'
import CurrentCard from './components/CurrentCard.jsx'
import ThemeSwitcher from './components/ThemeSwitcher.jsx'
import { applyTheme, initialTheme, setThemeInUrl } from './themes/themes.js'
import { useApi } from './useApi.js'

export default function App() {
  const [theme, setTheme] = useState(initialTheme)
  const clima = useApi('/api/clima')

  useEffect(() => applyTheme(theme), [theme])

  const changeTheme = (id) => {
    setTheme(id)
    setThemeInUrl(id)
  }

  return (
    <main className="page">
      <header className="header">
        <h1>Clima Monterrey</h1>
        <p className="subtitle">Nuevo León, México</p>
      </header>

      <ThemeSwitcher value={theme} onChange={changeTheme} />

      {clima.status === 'loading' && (
        <p className="panel status" role="status" aria-live="polite">
          Cargando clima…
        </p>
      )}

      {clima.status === 'error' && (
        <div className="panel status error" role="alert">
          <p>{clima.error}</p>
          <button type="button" className="pixel-button" onClick={clima.reload}>
            Reintentar
          </button>
        </div>
      )}

      {clima.status === 'ready' && (
        <CurrentCard current={clima.data.current} stale={clima.data.stale} />
      )}
    </main>
  )
}
