import Bear from './Bear.jsx'
import DateBadge from './DateBadge.jsx'
import Scene from './Scene.jsx'
import WeatherIcon from './WeatherIcon.jsx'

export default function Hero({ season, tip, current }) {
  return (
    <header className="hero">
      <Scene />
      <div className="hero-inner">
        <div className="hero-top">
          <div>
            <h1>Clima Monterrey</h1>
            <p className="subtitle">Nuevo León, México</p>
          </div>
          <DateBadge />
        </div>
        {current && (
          <WeatherIcon
            className="sky-icon"
            code={current.weather_code}
            isDay={current.is_day}
            size={72}
          />
        )}
        <Bear season={season} tip={tip} />
      </div>
    </header>
  )
}
