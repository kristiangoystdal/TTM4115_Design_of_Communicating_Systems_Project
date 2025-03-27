<template>
  <div id="map">
    <div id="loading-text">Loading map...</div>
  </div>
</template>

<script>
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

export default {
  name: 'MapView',
  mounted() {
    this.displayMap()
  },
  methods: {
    async displayMap() {
      const map = L.map("map").setView([63.422, 10.395], 14)

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map)

      try {
        const response = await fetch("/scooters")
        const scooters = await response.json()

        scooters.forEach((scooter) => {
          const marker = L.marker([scooter.latitude, scooter.longitude]).addTo(map)
          const popupContent = `
            ID: ${scooter.id}<br>
            Battery: ${scooter.battery_level}%<br>
            <form action="/book/${scooter.id}" method="POST" style="margin-top: 5px;">
              <button type="submit">Book</button>
            </form>
          `
          marker.bindPopup(popupContent)
        })
      } catch (error) {
        console.error('Failed to load scooters:', error)
      }
    }
  }
}
</script>

<style scoped>
#map {
  height: 100vh;
  width: 100%;
}

#loading-text {
  position: absolute;
  top: 10px;
  left: 10px;
  background: white;
  padding: 5px;
  z-index: 999;
}
</style>
