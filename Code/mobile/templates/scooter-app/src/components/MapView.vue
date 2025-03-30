<template>
  <div>
    <div v-if="message" class="notification success">{{ message }}</div>
    <div v-if="error" class="notification error">{{ error }}</div>

    <div id="map">
      <div id="loading-text">{{ loadingText }}</div>
    </div>
  </div>
</template>

<script>
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

export default {
  name: 'MapView',
  data() {
    return {
      session: {}, // You can bind this to an auth system
      message: '',
      error: '',
      loadingText: 'Loading map...',
      map: null,
    }
  },
  mounted() {
    this.displayMap()
  },
  methods: {
    async displayMap() {
      this.map = L.map('map').setView([63.422, 10.395], 14)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(this.map)

      try {
        const scooterRes = await fetch('/scooters')
        const scooters = await scooterRes.json()

        if (!scooters.length) {
          this.loadingText = 'No scooters available.'
        }

        scooters.forEach((scooter) => {
          const scooterIcon = L.icon({
            iconUrl: '/assets/e_scooter_icon.png',
            iconSize: [40, 40],
            iconAnchor: [20, 40],
            className: scooter.is_user_booked ? 'user-booked' : '',
          })

          const marker = L.marker([scooter.latitude, scooter.longitude], {
            icon: scooterIcon,
            opacity: scooter.is_user_booked ? 0.5 : 1.0,
          }).addTo(this.map)

          const popupContent = `
            ID: ${scooter.id}<br>
            Battery: ${scooter.battery_level}%<br>
            ${scooter.is_user_booked && !scooter.is_driving
              ? '<p>This scooter is booked by you.</p>'
              : `<form action="/book/${scooter.id}" method="POST">
                    <button type="submit">Book</button>
                  </form>`
            }
            <br>
            ${scooter.is_driving
              ? `<form action="/end_drive/${scooter.id}" method="POST">
                    <button type="submit">End Drive</button>
                  </form>`
              : `<form action="/start_drive/${scooter.id}" method="POST">
                    <button type="submit">Start Drive</button>
                  </form>`
            }
          `
          marker.bindPopup(popupContent)
        })

        const stationRes = await fetch('/charging_stations')
        const stations = await stationRes.json()

        const stationIcon = L.icon({
          iconUrl: '/assets/charging_station_icon.png',
          iconSize: [40, 40],
          iconAnchor: [20, 40],
        })

        stations.forEach((station) => {
          const marker = L.marker([station.latitude, station.longitude], {
            icon: stationIcon,
          }).addTo(this.map)
          marker.bindPopup(`Charging Station ID: ${station.id}`)
        })
      } catch (err) {
        console.error('Map loading failed', err)
        this.error = 'Failed to load map data.'
      }
    },
  },
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

.navbar {
  display: flex;
  justify-content: space-between;
  background-color: #333;
  padding: 0.75rem 1.5rem;
  color: white;
}

.navbar-menu a,
.navbar-brand a {
  color: white;
  text-decoration: none;
  margin: 0 1rem;
}

.notification {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 1rem;
  z-index: 1000;
  border-radius: 5px;
}

.notification.success {
  background-color: #4caf50;
  color: white;
}

.notification.error {
  background-color: #f44336;
  color: white;
}
</style>
