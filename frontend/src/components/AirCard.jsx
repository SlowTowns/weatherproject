import { number } from '../format.js'

// Escala ICA (EE. UU.): límite superior, categoría y color de estado.
const SCALE = [
  { limit: 50, label: 'Buena', color: '#3fae5a' },
  { limit: 100, label: 'Moderada', color: '#e5c33b' },
  { limit: 150, label: 'Dañina para grupos sensibles', color: '#ec8a35' },
  { limit: 200, label: 'Dañina', color: '#d9453d' },
  { limit: 300, label: 'Muy dañina', color: '#8e44ad' },
]
const SCALE_MAX = 300
const SEGMENTS = SCALE.map((s, i) => ({
  ...s,
  width: ((s.limit - (SCALE[i - 1]?.limit ?? 0)) / SCALE_MAX) * 100,
}))

function AirBody({ air }) {
  const level = SCALE.find((s) => s.label === air.category)
  const marker = air.us_aqi == null ? null : (Math.min(air.us_aqi, SCALE_MAX) / SCALE_MAX) * 100

  return (
    <>
      <div className="air-main">
        <span className="air-swatch" style={{ background: level?.color ?? '#7e2a35' }} aria-hidden="true" />
        <div>
          <p className="air-value">
            {number(air.us_aqi)}
            <span className="unit"> ICA</span>
          </p>
          <p className="air-category">{air.category ?? 'Sin dato'}</p>
        </div>
      </div>

      <div className="aqi-scale" aria-hidden="true">
        {SEGMENTS.map((s) => (
          <span key={s.label} style={{ width: `${s.width}%`, background: s.color }} />
        ))}
        {marker != null && <span className="aqi-marker" style={{ left: `${marker}%` }} />}
      </div>

      <dl className="air-list">
        <div>
          <dt>PM2.5</dt>
          <dd>{number(air.pm2_5, 1)} µg/m³</dd>
        </div>
        <div>
          <dt>PM10</dt>
          <dd>{number(air.pm10, 1)} µg/m³</dd>
        </div>
        <div>
          <dt>Ozono</dt>
          <dd>{number(air.ozone, 1)} µg/m³</dd>
        </div>
        <div>
          <dt>NO₂</dt>
          <dd>{number(air.nitrogen_dioxide, 1)} µg/m³</dd>
        </div>
      </dl>

      {air.stale && <p className="notice">Mostrando el último dato disponible.</p>}
    </>
  )
}

export default function AirCard({ state }) {
  return (
    <section className="panel air" aria-labelledby="air-title">
      <h2 id="air-title">Calidad del aire</h2>
      {state.status === 'loading' && <p className="muted">Cargando…</p>}
      {state.status === 'error' && <p className="muted">No disponible por el momento.</p>}
      {state.status === 'ready' && <AirBody air={state.data} />}
    </section>
  )
}
