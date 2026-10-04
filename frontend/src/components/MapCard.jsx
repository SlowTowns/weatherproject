import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useEffect, useRef } from 'react'
import { number } from '../format.js'

const CENTER = [25.6866, -100.3161]

// Mosaicos estándar de OpenStreetMap: gratuitos, sin API key, con atribución obligatoria.
const TILES = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
const ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'

const pin = (text) =>
  L.divIcon({ className: 'map-pin', html: `<div class="map-temp">${text}</div>`, iconSize: null })

export default function MapCard({ temperature }) {
  const containerRef = useRef(null)
  const markerRef = useRef(null)

  useEffect(() => {
    const container = containerRef.current
    const map = L.map(container, { center: CENTER, zoom: 11, scrollWheelZoom: false })
    L.tileLayer(TILES, { maxZoom: 19, attribution: ATTRIBUTION }).addTo(map)
    markerRef.current = L.marker(CENTER, { icon: pin('—'), interactive: false, keyboard: false }).addTo(map)

    // El zoom con la rueda se activa solo al hacer clic, para no secuestrar el scroll de la página.
    map.on('click', () => map.scrollWheelZoom.enable())
    map.on('mouseout', () => map.scrollWheelZoom.disable())

    const observer = new ResizeObserver(() => map.invalidateSize())
    observer.observe(container)
    return () => {
      observer.disconnect()
      map.remove()
    }
  }, [])

  useEffect(() => {
    markerRef.current?.setIcon(pin(`${number(temperature)}°`))
  }, [temperature])

  return (
    <section className="panel map-card" aria-labelledby="map-title">
      <h2 id="map-title">Mapa</h2>
      <div ref={containerRef} className="map" role="region" aria-label="Mapa de Monterrey" />
    </section>
  )
}
