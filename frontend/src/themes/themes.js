import { monterreyToday } from '../format.js'

// Estaciones del hemisferio norte. Los colores viven en themes.css (data-theme).
export const SEASONS = [
  { id: 'primavera', label: 'Primavera' },
  { id: 'verano', label: 'Verano' },
  { id: 'otono', label: 'Otoño' },
  { id: 'invierno', label: 'Invierno' },
]

const IDS = SEASONS.map((s) => s.id)

// La vista previa de temas solo existe en desarrollo (npm run dev).
// En la versión final el tema depende únicamente de la fecha real en Monterrey.
export const THEME_PREVIEW = import.meta.env.DEV

// Límites aproximados: equinoccios y solsticios (20 mar, 21 jun, 23 sep, 21 dic).
export function seasonFor({ month, day }) {
  const md = month * 100 + day
  if (md >= 1221 || md < 320) return 'invierno'
  if (md < 621) return 'primavera'
  if (md < 923) return 'verano'
  return 'otono'
}

export function themeFromUrl(search = window.location.search) {
  const value = new URLSearchParams(search).get('tema')
  return IDS.includes(value) ? value : null
}

export function initialTheme() {
  const season = seasonFor(monterreyToday())
  return THEME_PREVIEW ? (themeFromUrl() ?? season) : season
}

export function applyTheme(id) {
  document.documentElement.dataset.theme = id
}

export function setThemeInUrl(id) {
  const url = new URL(window.location.href)
  url.searchParams.set('tema', id)
  window.history.replaceState(null, '', url)
}
