// Estaciones del hemisferio norte. Los colores viven en themes.css (data-theme).
export const SEASONS = [
  { id: 'primavera', label: 'Primavera' },
  { id: 'verano', label: 'Verano' },
  { id: 'otono', label: 'Otoño' },
  { id: 'invierno', label: 'Invierno' },
]

const IDS = SEASONS.map((s) => s.id)

// Límites aproximados: equinoccios y solsticios (20 mar, 21 jun, 23 sep, 21 dic).
export function seasonForDate(date = new Date()) {
  const md = (date.getMonth() + 1) * 100 + date.getDate()
  if (md >= 1221 || md < 320) return 'invierno'
  if (md < 621) return 'primavera'
  if (md < 923) return 'verano'
  return 'otono'
}

// ?tema=verano fuerza una estación (útil para revisar los cuatro temas).
export function themeFromUrl(search = window.location.search) {
  const value = new URLSearchParams(search).get('tema')
  return IDS.includes(value) ? value : null
}

export function initialTheme() {
  return themeFromUrl() ?? seasonForDate()
}

export function applyTheme(id) {
  document.documentElement.dataset.theme = id
}

export function setThemeInUrl(id) {
  const url = new URL(window.location.href)
  url.searchParams.set('tema', id)
  window.history.replaceState(null, '', url)
}
