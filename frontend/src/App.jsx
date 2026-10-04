import { useEffect, useState } from 'react'
import { bearTip } from './bearTips.js'
import AirCard from './components/AirCard.jsx'
import AlertsPanel from './components/AlertsPanel.jsx'
import CurrentCard from './components/CurrentCard.jsx'
import DailyForecast from './components/DailyForecast.jsx'
import Hero from './components/Hero.jsx'
import HourlyChart from './components/HourlyChart.jsx'
import MapCard from './components/MapCard.jsx'
import ThemeSwitcher from './components/ThemeSwitcher.jsx'
import { applyTheme, initialTheme, setThemeInUrl, THEME_PREVIEW } from './themes/themes.js'
import { useApi } from './useApi.js'

export default function App() {
  const [theme, setTheme] = useState(initialTheme)
  const clima = useApi('/api/clima')
  const pronostico = useApi('/api/pronostico')
  const aire = useApi('/api/aire')
  const alertas = useApi('/api/alertas')

  useEffect(() => applyTheme(theme), [theme])

  const changeTheme = (id) => {
    setTheme(id)
    setThemeInUrl(id)
  }

  const ready = clima.status === 'ready' && pronostico.status === 'ready'
  const failed = clima.status === 'error' || pronostico.status === 'error'
  const current = clima.data?.current
  const alerts = alertas.data?.alerts ?? []
  const retry = () => {
    for (const source of [clima, pronostico, aire, alertas]) {
      if (source.status === 'error') source.reload()
    }
  }

  return (
    <>
      <Hero
        season={theme}
        current={current}
        tip={ready ? bearTip({ current, alerts, air: aire.data, season: theme }) : null}
      />

      <main className="page">
        {failed && (
          <div className="panel status error" role="alert">
            <p>{clima.error ?? pronostico.error}</p>
            <button type="button" className="pixel-button" onClick={retry}>
              Reintentar
            </button>
          </div>
        )}

        {!failed && !ready && (
          <p className="panel status" role="status" aria-live="polite">
            Cargando clima…
          </p>
        )}

        {ready && (
          <>
            <AlertsPanel alerts={alerts} />
            <div className="dashboard">
              <CurrentCard current={current} today={pronostico.data.daily[0]} stale={clima.data.stale} />
              <MapCard temperature={current.temperature} />
              <HourlyChart hourly={pronostico.data.hourly} />
              <AirCard state={aire} />
              <DailyForecast daily={pronostico.data.daily} />
            </div>
          </>
        )}
      </main>

      <footer className="footer">
        <p>
          Datos del clima: <a href="https://open-meteo.com/">Open-Meteo</a> (CC BY 4.0). Mapa: ©{' '}
          <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>.
        </p>
        {THEME_PREVIEW && (
          <div className="preview">
            <p>Vista previa de temas (solo en desarrollo):</p>
            <ThemeSwitcher value={theme} onChange={changeTheme} />
          </div>
        )}
      </footer>
    </>
  )
}
