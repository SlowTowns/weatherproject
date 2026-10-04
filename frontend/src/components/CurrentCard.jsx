import { describeWeather } from '../weatherCodes.js'

const number = (value, digits = 0) =>
  value == null ? '—' : Number(value).toLocaleString('es-MX', { maximumFractionDigits: digits })

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

export default function CurrentCard({ current, stale }) {
  return (
    <section className="panel" aria-labelledby="ahora-titulo">
      <h2 id="ahora-titulo">Ahora</h2>
      <p className="temperature" aria-label={`Temperatura ${number(current.temperature)} grados`}>
        {number(current.temperature)}°C
      </p>
      <p className="description">{describeWeather(current.weather_code)}</p>
      {stale && (
        <p className="notice" role="status">
          Mostrando el último dato disponible.
        </p>
      )}
      <dl className="stats">
        <Stat label="Sensación" value={number(current.apparent_temperature)} unit="°C" />
        <Stat label="Humedad" value={number(current.humidity)} unit="%" />
        <Stat label="Viento" value={number(current.wind_speed)} unit="km/h" />
        <Stat label="Presión" value={number(current.pressure)} unit="hPa" />
        <Stat label="Lluvia" value={number(current.precipitation, 1)} unit="mm" />
      </dl>
    </section>
  )
}
