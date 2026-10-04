// Dibuja un sprite (filas de caracteres -> colores de la paleta) como SVG nítido.
// Los píxeles contiguos del mismo color en una fila se agrupan en un solo rectángulo.
export default function PixelSprite({ rows, palette, size, title, className }) {
  const width = rows[0].length
  const height = rows.length
  const rects = []

  rows.forEach((row, y) => {
    let x = 0
    while (x < width) {
      const char = row[x]
      let run = 1
      while (x + run < width && row[x + run] === char) run++
      const fill = palette[char]
      if (fill) {
        rects.push(<rect key={`${x}-${y}`} x={x} y={y} width={run} height={1} style={{ fill }} />)
      }
      x += run
    }
  })

  return (
    <svg
      className={className}
      viewBox={`0 0 ${width} ${height}`}
      width={size}
      height={size && (size * height) / width}
      shapeRendering="crispEdges"
      role={title ? 'img' : undefined}
      aria-hidden={title ? undefined : true}
    >
      {title && <title>{title}</title>}
      {rects}
    </svg>
  )
}
