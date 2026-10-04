// Oso mascota, 16x16. Se define la mitad izquierda y se refleja para que sea simétrico.
const mirror = (left) => left + [...left].reverse().join('')

const BASE = [
  '..oooo..',
  '.obllbo.',
  '.obbbbbo',
  'obbbbbbb',
  'obbbbbbb',
  'obbwkbbb',
  'obbkkbbb',
  'obpbmmmm',
  'obbmmmmk',
  'obbmmmkm',
  '.obbbbbb',
  '..oooooo',
  '.obbbbbb',
  '.obbbllm',
  '.obbbllm',
  '..oooooo',
].map(mirror)

// Accesorio por estación: filas completas reemplazadas y píxeles sueltos [fila, columna, color].
const SEASON_PATCHES = {
  invierno: { rows: { 12: mirror('.oaaaaaa') }, cells: [[13, 4, 'a'], [14, 4, 'a']] }, // bufanda
  verano: {
    rows: { 5: mirror('obkkkkkk'), 6: mirror('obkkkkbb') }, // lentes de sol
    cells: [[5, 3, 'w'], [5, 11, 'w']],
  },
  otono: { cells: [[0, 7, 'a'], [0, 8, 'a'], [1, 8, 'a'], [1, 7, 'o']] }, // hoja
  primavera: { cells: [[0, 6, 'a'], [0, 7, 'y'], [0, 8, 'a'], [1, 7, 'a']] }, // flor
}

export const BEAR_PALETTE = {
  o: '#2b1a14',
  b: '#8a5a34',
  l: '#c58b57',
  m: '#e3bf8f',
  k: '#1b1210',
  w: '#ffffff',
  p: '#e07a7a',
  y: '#ffd23f',
  a: 'var(--accent)',
}

export function bearRows(season) {
  const patch = SEASON_PATCHES[season] ?? {}
  const grid = BASE.map((row, i) => [...(patch.rows?.[i] ?? row)])
  for (const [row, col, color] of patch.cells ?? []) grid[row][col] = color
  return grid.map((row) => row.join(''))
}
