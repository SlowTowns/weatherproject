import { spriteFor, WEATHER_PALETTE } from '../sprites/weather.js'
import PixelSprite from './PixelSprite.jsx'

export default function WeatherIcon({ code, isDay, size = 48, title, className }) {
  return (
    <PixelSprite
      rows={spriteFor(code, isDay)}
      palette={WEATHER_PALETTE}
      size={size}
      title={title}
      className={className}
    />
  )
}
