// Paisaje pixel art: Sierra Madre al fondo, Cerro de la Silla y la ciudad al frente.
const W = 120
const H = 28

// Perfiles [columna, altura]; el Cerro tiene dos cimas con la "silla" en medio.
const SIERRA = [[0, 8], [12, 10], [22, 9], [34, 11], [46, 10], [58, 12], [72, 10], [86, 12], [100, 10], [112, 11], [120, 9]]
const CERRO = [
  [0, 2], [8, 3], [16, 5], [24, 8], [30, 13], [35, 16], [39, 17], [43, 15], [47, 11], [51, 9],
  [55, 10], [59, 13], [63, 16], [67, 17], [71, 16], [76, 14], [82, 11], [90, 7], [100, 4], [110, 3], [120, 2],
]

function heights(points) {
  return Array.from({ length: W }, (_, x) => {
    const i = points.findIndex(([px]) => px > x)
    const [x0, h0] = points[i - 1]
    const [x1, h1] = points[i]
    return Math.round(h0 + ((h1 - h0) * (x - x0)) / (x1 - x0))
  })
}

// Silueta escalonada (bordes de píxel) como un solo path, sin costuras.
function stepPath(columnHeights) {
  const steps = columnHeights.map((h, x) => `V${H - h}H${x + 1}`).join('')
  return `M0 ${H}${steps}V${H}Z`
}

const sierra = heights(SIERRA).map((h, x) => h + (x % 7 === 3 ? 1 : 0) - (x % 11 === 5 ? 1 : 0))

const city = Array.from({ length: W }, (_, x) => {
  if (x === 33 || x === 34) return 9 // torre
  const block = Math.floor(x / 3)
  const downtown = block >= 6 && block <= 16 ? (block * 5) % 3 : 0
  return 1 + ((block * 7) % 4) + downtown
})

const PATHS = {
  far: stepPath(sierra),
  cerro: stepPath(heights(CERRO)),
  city: stepPath(city),
}

export default function Scene() {
  return (
    <svg
      className="scene"
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="xMidYMax slice"
      shapeRendering="crispEdges"
      aria-hidden="true"
    >
      <path d={PATHS.far} className="scene-far" />
      <path d={PATHS.cerro} className="scene-cerro" />
      <path d={PATHS.city} className="scene-city" />
    </svg>
  )
}
