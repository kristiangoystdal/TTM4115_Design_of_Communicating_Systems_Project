<template>
  <div>
    <div v-if="message" class="notification success">{{ message }}</div>
    <div v-if="error" class="notification error">{{ error }}</div>

    <div id="map">
      <div id="loading-text">{{ loadingText }}</div>
    </div>
  </div>

  <ScooterPopup v-if="selectedScooter" v-model:modelValue="showPopup" :scooter="selectedScooter"
    @update:scooter="handleScooterUpdate" @drive-data="handleDriveData" />

  <ReceiptOverlay :show="showReceipt" :driveData="receiptData" @update:show="showReceipt = $event" />
</template>

<script>
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import ScooterPopup from '@/components/ScooterPopup.vue'
import { useToast } from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import ReceiptOverlay from './ReceiptOverlay.vue'

export default {
  name: 'MapView',
  components: { ScooterPopup, ReceiptOverlay },
  data() {
    return {
      session: {},
      message: '',
      error: '',
      loadingText: 'Loading map...',
      map: null,
      scooters: [],
      selectedScooter: null,
      showPopup: false,
      showReceipt: false,
      receiptData: null,
    }
  },
  mounted() {
    this.displayMap()
    this.fetchScooters()
  },
  watch: {
    showPopup(newValue) {
      if (!newValue) {
        this.displayMap()
        this.clearScooters()
        this.fetchScooters()
      }
    },
  },
  methods: {
    async displayMap() {
      if (this.map) {
        this.map.off(); // Remove all event listeners
        this.map.remove(); // Remove the map instance
      }

      this.map = L.map('map').setView([63.422, 10.395], 14);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(this.map);
    },
    async fetchScooters() {
      try {
        const scooterRes = await fetch('/scooters')
        this.scooters = await scooterRes.json()

        const scooter_taken = this.scooters.some(
          (scooter) => scooter.is_driving || scooter.is_user_booked
        );

        if (!this.scooters.length) {
          useToast().error('No scooters available.')
        } else if (scooter_taken) {
          this.scooters.forEach((scooter) => {
            if (scooter.is_driving || scooter.is_user_booked) {
              const scooterIcon = L.icon({
                iconUrl: '/assets/e_scooter_icon.png',
                iconSize: [40, 40],
                iconAnchor: [20, 40],
              })

              const marker = L.marker([scooter.latitude, scooter.longitude], {
                icon: scooterIcon,
                opacity: scooter.is_user_booked ? 0.5 : 1.0,
              }).addTo(this.map)
              scooter.marker = marker

              marker.on('click', () => {
                this.selectedScooter = scooter
                this.showPopup = true
              })
            }
          })
        } else {
          this.scooters.forEach((scooter) => {
            const scooterIcon = L.icon({
              iconUrl: '/assets/e_scooter_icon.png',
              iconSize: [40, 40],
              iconAnchor: [20, 40],
            })

            const marker = L.marker([scooter.latitude, scooter.longitude], {
              icon: scooterIcon,
              opacity: scooter.is_user_booked ? 0.5 : 1.0,
            }).addTo(this.map)

            marker.on('click', () => {
              this.selectedScooter = scooter
              this.showPopup = true
            })
          })
        }

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
    clearScooters() {
      this.scooters.forEach((scooter) => {
        if (scooter.marker) {
          this.map.removeLayer(scooter.marker)
        }
      })
      this.scooters = []
    },
    handleDriveData(data) {
      if (data) {
        console.log("Drive data received:", data)
        this.showReceipt = true;
        this.receiptData = data;
      }
    }

  },
}
</script>


<style scoped>
#map {
  height: 90vh;
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
