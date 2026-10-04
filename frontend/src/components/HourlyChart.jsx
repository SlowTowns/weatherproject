import { useEffect, useRef, useState } from 'react'
import { hourLabel, number } from '../format.js'
import { describeWeather } from '../weatherCodes.js'

// Línea del tiempo de las próximas 24 horas (temperatura o lluvia), estilo Google.
const HOURS = 24
const HEIGHT = 210
const PAD = { top: 30, right: 18, bottom: 30, left: 18 }
// Rango vertical mínimo: evita que variaciones de décimas parezcan picos dramáticos.
const MIN_TEMP_SPAN = 6

const TABS = [
  { id: 'temp', label: 'Temperatura' },
  { id: 'rain', label: 'Lluvia' },
]

function useWidth() {
  const ref = useRef(null)
  const [width, setWidth] = useState(0)
  useEffect(() => {
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width))
    observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])
  return [ref, width]
}

// Divide la serie en tramos continuos, saltando horas sin dato.
function segments(xs, ys) {
  const result = []
  let current = []
  ys.forEach((y, i) => {
    if (y == null) {
      if (current.length) result.push(current)
      current = []
    } else {
      current.push([xs[i], y])
    }
  })
  if (current.length) result.push(current)
  return result
}

const linePath = (segs) => segs.map((s) => 'M' + s.map(([x, y]) => `${x},${y}`).join('L')).join('')

const areaPath = (segs, base) =>
  segs
    .map((s) => `M${s[0][0]},${base}L${s.map(([x, y]) => `${x},${y}`).join('L')}L${s.at(-1)[0]},${base}Z`)
    .join('')

const label = (point, i) => (i === 0 ? 'Ahora' : hourLabel(point.time))

function TemperaturePlot({ points, xs, plotH, every, index }) {
  const temps = points.map((p) => p.temperature)
  const valid = temps.filter((v) => v != null)
  if (!valid.length) return null
  const mid = (Math.max(...valid) + Math.min(...valid)) / 2
  const half = Math.max(Math.max(...valid) - Math.min(...valid) + 2, MIN_TEMP_SPAN) / 2
  const max = mid + half
  const min = mid - half
  const y = (v) => PAD.top + ((max - v) / (max - min)) * plotH
  const segs = segments(xs, temps.map((v) => (v == null ? null : y(v))))
  const selected = temps[index]

  return (
    <g>
      <path d={areaPath(segs, PAD.top + plotH)} className="chart-area" />
      <path d={linePath(segs)} className="chart-line" />
      {temps.map((v, i) =>
        v != null && i % every === 0 ? (
          <text key={i} x={xs[i]} y={y(v) - 10} textAnchor={i === 0 ? 'start' : 'middle'} className="chart-value">
            {number(v)}°
          </text>
        ) : null,
      )}
      {selected != null && <circle cx={xs[index]} cy={y(selected)} r={5} className="chart-marker" />}
    </g>
  )
}

function RainPlot({ points, xs, plotH, step, every, index }) {
  const base = PAD.top + plotH
  const barWidth = Math.max(4, step * 0.6)
  return (
    <g>
      {points.map((p, i) => {
        const prob = p.precipitation_probability ?? 0
        const h = (prob / 100) * plotH
        return (
          <g key={i}>
            {h > 0 && (
              <rect
                x={xs[i] - barWidth / 2}
                y={base - h}
                width={barWidth}
                height={h}
                rx={2}
                className={i === index ? 'chart-bar selected' : 'chart-bar'}
              />
            )}
            {i % every === 0 && (
              <text x={xs[i]} y={base - h - 8} textAnchor={i === 0 ? 'start' : 'middle'} className="chart-value">
                {number(prob)}%
              </text>
            )}
          </g>
        )
      })}
    </g>
  )
}

export default function HourlyChart({ hourly }) {
  const points = hourly.slice(0, HOURS)
  const [tab, setTab] = useState('temp')
  const [index, setIndex] = useState(0)
  const [plotRef, width] = useWidth()

  const n = points.length
  const plotW = Math.max(width - PAD.left - PAD.right, 1)
  const plotH = HEIGHT - PAD.top - PAD.bottom
  const step = n > 1 ? plotW / (n - 1) : plotW
  const xs = points.map((_, i) => PAD.left + i * step)
  const every = step * 3 < 48 ? 6 : 3
  const selected = points[index]

  const select = (i) => setIndex(Math.max(0, Math.min(n - 1, i)))
  const onPointer = (event) => {
    const rect = event.currentTarget.getBoundingClientRect()
    select(Math.round((event.clientX - rect.left - PAD.left) / step))
  }
  const onKeyDown = (event) => {
    const moves = { ArrowRight: index + 1, ArrowLeft: index - 1, Home: 0, End: n - 1 }
    if (event.key in moves) {
      event.preventDefault()
      select(moves[event.key])
    }
  }

  const readout = !selected
    ? ''
    : tab === 'temp'
      ? `${label(selected, index)} · ${number(selected.temperature)}°C · ${describeWeather(selected.weather_code)}`
      : `${label(selected, index)} · ${number(selected.precipitation_probability)}% de probabilidad · ${number(selected.precipitation, 1)} mm`

  return (
    <section className="panel chart" aria-labelledby="chart-title">
      <div className="panel-head">
        <h2 id="chart-title">Próximas 24 horas</h2>
        <div className="chart-tabs" role="tablist" aria-label="Variable">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              role="tab"
              aria-selected={tab === t.id}
              className="pixel-button small"
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <p className="chart-readout" aria-live="polite">
        {readout}
      </p>

      <div
        ref={plotRef}
        className="chart-plot"
        tabIndex={0}
        role="group"
        aria-label="Gráfica por hora. Usa las flechas izquierda y derecha para recorrer las horas."
        onKeyDown={onKeyDown}
      >
        {width > 0 && n > 1 && (
          <svg width={width} height={HEIGHT} aria-hidden="true">
            <line x1={PAD.left} x2={width - PAD.right} y1={PAD.top + plotH} y2={PAD.top + plotH} className="chart-baseline" />
            <line x1={xs[index]} x2={xs[index]} y1={PAD.top - 8} y2={PAD.top + plotH} className="chart-cross" />
            {tab === 'temp' ? (
              <TemperaturePlot points={points} xs={xs} plotH={plotH} every={every} index={index} />
            ) : (
              <RainPlot points={points} xs={xs} plotH={plotH} step={step} every={every} index={index} />
            )}
            {points.map((p, i) =>
              i % every === 0 ? (
                <text key={i} x={xs[i]} y={HEIGHT - 8} textAnchor={i === 0 ? 'start' : 'middle'} className="chart-axis">
                  {label(p, i)}
                </text>
              ) : null,
            )}
            <rect
              x={0}
              y={0}
              width={width}
              height={HEIGHT}
              fill="transparent"
              onPointerMove={onPointer}
              onPointerDown={onPointer}
            />
          </svg>
        )}
      </div>

      <table className="sr-only">
        <caption>Pronóstico por hora</caption>
        <thead>
          <tr>
            <th scope="col">Hora</th>
            <th scope="col">Temperatura (°C)</th>
            <th scope="col">Probabilidad de lluvia (%)</th>
          </tr>
        </thead>
        <tbody>
          {points.map((p, i) => (
            <tr key={p.time}>
              <th scope="row">{label(p, i)}</th>
              <td>{number(p.temperature)}</td>
              <td>{number(p.precipitation_probability)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
