import { number, timeLabel, windDirection } from '../format.js'
import { describeWeather } from '../weatherCodes.js'
import WeatherIcon from './WeatherIcon.jsx'

function Stat({ label, value, unit }) {
  return (
    <div className="stat">
      <dt>{label}</dt>
      <dd>
        {value}
        {unit && <span className="unit"> {unit}</span>}
      </dd>
    </div>
  )
}

export default function CurrentCard({ current, today, stale }) {
  return (
    <section className="panel now" aria-labelledby="now-title">
      <div className="panel-head">
        <h2 id="now-title">Ahora</h2>
        <p className="muted">Actualizado {timeLabel(current.time)}</p>
      </div>

      <div className="now-main">
        <WeatherIcon code={current.weather_code} isDay={current.is_day} size={96} />
        <div>
          <p className="temperature">{number(current.temperature)}°C</p>
          <p className="description">{describeWeather(current.weather_code)}</p>
          {today && (
            <p className="muted">
              Máx {number(today.temperature_max)}° · Mín {number(today.temperature_min)}°
            </p>
          )}
        </div>
      </div>

      {stale && (
        <p className="notice" role="status">
          Mostrando el último dato disponible.
        </p>
      )}

      <dl className="stats">
        <Stat label="Sensación" value={number(current.apparent_temperature)} unit="°C" />
        <Stat label="Humedad" value={number(current.humidity)} unit="%" />
        <Stat
          label="Viento"
          value={number(current.wind_speed)}
          unit={`km/h ${windDirection(current.wind_direction)}`}
        />
        <Stat label="Lluvia" value={number(current.precipitation, 1)} unit="mm" />
      </dl>
    </section>
  )
}
