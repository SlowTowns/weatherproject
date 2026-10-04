import { dayLabel, number } from '../format.js'
import WeatherIcon from './WeatherIcon.jsx'

export default function DailyForecast({ daily }) {
  const mins = daily.map((d) => d.temperature_min).filter((v) => v != null)
  const maxs = daily.map((d) => d.temperature_max).filter((v) => v != null)
  const low = Math.min(...mins)
  const span = Math.max(...maxs) - low || 1

  return (
    <section className="panel days" aria-labelledby="days-title">
      <h2 id="days-title">Próximos 7 días</h2>
      <ol className="day-list">
        {daily.map((d, i) => {
          const hasRange = d.temperature_min != null && d.temperature_max != null
          return (
            <li key={d.date} className="day">
              <span className="day-name">{i === 0 ? 'Hoy' : dayLabel(d.date)}</span>
              <WeatherIcon code={d.weather_code} size={44} />
              <span className="day-temps">
                <span className="max">{number(d.temperature_max)}°</span>{' '}
                <span className="min">{number(d.temperature_min)}°</span>
              </span>
              <span className="range" aria-hidden="true">
                {hasRange && (
                  <span
                    className="range-fill"
                    style={{
                      left: `${((d.temperature_min - low) / span) * 100}%`,
                      width: `${((d.temperature_max - d.temperature_min) / span) * 100}%`,
                    }}
                  />
                )}
              </span>
              <span className="day-rain">
                {d.precipitation_probability_max != null &&
                  `Lluvia ${number(d.precipitation_probability_max)}%`}
              </span>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
