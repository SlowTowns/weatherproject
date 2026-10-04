// Íconos del clima en pixel art, 12x12.
const EMPTY = '............'

const SUN = [
  '.....YY.....',
  '.Y........Y.',
  '..Y.yyyy.Y..',
  '...yyyyyy...',
  '..yyyyyyyy..',
  'Y.yyyyyyyy.Y',
  'Y.yyyyyyyy.Y',
  '..yyyyyyyy..',
  '...yyyyyy...',
  '..Y.yyyy.Y..',
  '.Y........Y.',
  '.....YY.....',
]

const MOON = [
  '....mmmm....',
  '..mmmm......',
  '.mmmm.......',
  '.mmmm.......',
  'mmmm........',
  'mmmm........',
  'mmmm........',
  'mmmm........',
  '.mmmm.......',
  '.mmmm.......',
  '..mmmm......',
  '....mmmm....',
]

const CLOUD_BODY = [
  EMPTY,
  EMPTY,
  '.....ccc....',
  '..ccccccc...',
  '.cccccccccc.',
  'cccccccccccc',
  'cccccccccccc',
  'CCCCCCCCCCCC',
  '.CCCCCCCCCC.',
]

const CLOUD = [...CLOUD_BODY, EMPTY, EMPTY, EMPTY]

const PARTLY = [
  '...Y........',
  '.Y.y.Y......',
  '..yyyy......',
  '.Yyyyy.cccc.',
  '..yyy.cccccc',
  '...Y.ccccccc',
  '..cccccccccc',
  '.cccccccccc.',
  '.CCCCCCCCCC.',
  EMPTY,
  EMPTY,
  EMPTY,
]

const RAIN = [...CLOUD_BODY, '..r...r...r.', '.r...r...r..', EMPTY]

const STORM = [
  ...CLOUD_BODY.map((row) => row.replaceAll('c', 'D').replaceAll('C', 'K')),
  '.....zz.....',
  '....zz......',
  '.....z......',
]

const FOG = [...CLOUD_BODY, EMPTY, '.CCCCCCCCCC.', '..CCCCCCCC..']

export const WEATHER_PALETTE = {
  Y: '#f28c28',
  y: '#ffd23f',
  m: '#f4e9a8',
  c: '#eef3f8',
  C: '#aab8c8',
  D: '#7d8898',
  K: '#4a5363',
  r: '#4aa3e0',
  z: '#ffe14d',
}

export const WEATHER_SPRITES = { SUN, MOON, CLOUD, PARTLY, RAIN, STORM, FOG }

// Código WMO -> sprite.
export function spriteFor(code, isDay = true) {
  if (code === 0 || code === 1) return isDay === false ? MOON : SUN
  if (code === 2) return isDay === false ? CLOUD : PARTLY
  if (code === 45 || code === 48) return FOG
  if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) return RAIN
  if (code >= 95 && code <= 99) return STORM
  return CLOUD
}
