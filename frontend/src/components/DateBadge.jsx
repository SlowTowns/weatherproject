import { useEffect, useState } from 'react'
import { formatLongDate, monterreyToday } from '../format.js'

const pad = (n) => String(n).padStart(2, '0')

export default function DateBadge() {
  const [now, setNow] = useState(() => new Date())

  // Se actualiza cada minuto para cambiar de día a medianoche.
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60_000)
    return () => clearInterval(id)
  }, [])

  const { year, month, day } = monterreyToday(now)
  return (
    <p className="date-badge">
      <time dateTime={`${year}-${pad(month)}-${pad(day)}`}>{formatLongDate(now)}</time>
    </p>
  )
}
