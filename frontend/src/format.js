export const TIMEZONE = 'America/Monterrey'

export const capitalize = (text) => text.charAt(0).toUpperCase() + text.slice(1)

export const number = (value, digits = 0) =>
  value == null ? '—' : Number(value).toLocaleString('es-MX', { maximumFractionDigits: digits })

// Las horas de la API vienen en hora local de Monterrey sin zona ("2026-10-04T15:00:00"),
// así que se leen como texto para no depender de la zona horaria del navegador.
export const hourOf = (isoLocal) => Number(isoLocal.slice(11, 13))

const meridiem = (hour) => (hour < 12 ? 'a.m.' : 'p.m.')

export function hourLabel(isoLocal) {
  const hour = hourOf(isoLocal)
  return `${hour % 12 || 12} ${meridiem(hour)}`
}

export function timeLabel(isoLocal) {
  const hour = hourOf(isoLocal)
  return `${hour % 12 || 12}:${isoLocal.slice(14, 16)} ${meridiem(hour)}`
}

export const isDaytimeHour = (isoLocal) => {
  const hour = hourOf(isoLocal)
  return hour >= 7 && hour < 19
}

const weekdayFormat = new Intl.DateTimeFormat('es-MX', { weekday: 'short', timeZone: 'UTC' })

export function dayLabel(isoDate) {
  const [year, month, day] = isoDate.split('-').map(Number)
  const weekday = weekdayFormat.format(new Date(Date.UTC(year, month - 1, day))).replace('.', '')
  return `${capitalize(weekday)} ${day}`
}

const WIND_POINTS = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']

export const windDirection = (degrees) =>
  degrees == null ? '' : WIND_POINTS[Math.round(degrees / 45) % 8]

// Fecha actual en Monterrey, sin importar la zona horaria del navegador.
export function monterreyToday(now = new Date()) {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: TIMEZONE,
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
  }).formatToParts(now)
  const get = (type) => Number(parts.find((part) => part.type === type).value)
  return { year: get('year'), month: get('month'), day: get('day') }
}

const longDateFormat = new Intl.DateTimeFormat('es-MX', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  timeZone: TIMEZONE,
})

export const formatLongDate = (now = new Date()) => capitalize(longDateFormat.format(now))
