import { BEAR_PALETTE, bearRows } from '../sprites/bear.js'
import PixelSprite from './PixelSprite.jsx'

export default function Bear({ season, tip }) {
  return (
    <div className="bear">
      {tip && (
        <p className="bubble" role="status">
          {tip}
        </p>
      )}
      <PixelSprite
        rows={bearRows(season)}
        palette={BEAR_PALETTE}
        className="bear-sprite"
        title="Oso, la mascota del clima regio"
      />
    </div>
  )
}
