import { hourLabel } from '../format.js'

export default function AlertsPanel({ alerts }) {
  if (!alerts.length) return null
  return (
    <section className="alerts" aria-labelledby="alerts-title">
      <h2 id="alerts-title" className="sr-only">
        Alertas
      </h2>
      {alerts.map((alert) => (
        <article key={alert.type} className={`panel alert alert-${alert.severity}`}>
          <span className="alert-icon" aria-hidden="true">
            !
          </span>
          <div>
            <h3>
              {alert.title}
              <span className="sr-only"> (severidad {alert.severity})</span>
            </h3>
            <p>{alert.message}</p>
            <p className="muted">
              Desde las {hourLabel(alert.starts_at)} · {alert.hours} h
            </p>
          </div>
        </article>
      ))}
    </section>
  )
}
