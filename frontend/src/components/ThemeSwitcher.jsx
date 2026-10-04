import { SEASONS } from '../themes/themes.js'

export default function ThemeSwitcher({ value, onChange }) {
  return (
    <div className="theme-switcher" role="group" aria-label="Tema de estación">
      {SEASONS.map((season) => (
        <button
          key={season.id}
          type="button"
          className="pixel-button"
          aria-pressed={value === season.id}
          onClick={() => onChange(season.id)}
        >
          {season.label}
        </button>
      ))}
    </div>
  )
}
