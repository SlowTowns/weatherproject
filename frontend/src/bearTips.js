// Mensaje de la mascota según alertas, clima actual y calidad del aire.
const SEASON_TIPS = {
  primavera: '¡Feliz primavera, regio!',
  verano: 'Verano regio: ¡bloqueador y agua!',
  otono: 'Ya se siente el otoño en Monterrey.',
  invierno: 'Invierno regio: ¡sácale a la chamarra!',
}

const isRain = (code) => (code >= 51 && code <= 67) || (code >= 80 && code <= 82)

export function bearTip({ current, alerts = [], air, season }) {
  const types = alerts.map((alert) => alert.type)
  if (types.includes('tormenta')) return 'Viene tormenta. Mejor quédate bajo techo.'
  if (types.includes('calor_extremo')) return '¡Calor extremo! Toma agua y busca sombra.'
  if (types.includes('frente_frio')) return 'Se acerca un frente frío. ¡Abrígate!'

  if (current) {
    const code = current.weather_code
    if (code >= 95) return 'Hay tormenta eléctrica. No salgas si no es necesario.'
    if (isRain(code)) return 'Está lloviendo. No olvides el paraguas.'
    if (current.temperature >= 35) return 'Hace mucho calor. ¡Hidrátate!'
    if (current.temperature <= 10) return 'Hace frío. Ponte una chamarra.'
  }

  if (air?.us_aqi > 100) return 'El aire no está bien hoy. Evita ejercitarte afuera.'
  return SEASON_TIPS[season]
}
