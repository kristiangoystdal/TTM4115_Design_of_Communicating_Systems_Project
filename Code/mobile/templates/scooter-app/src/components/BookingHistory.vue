<template>
  <v-container class="py-8">
    <v-card elevation="2" class="pa-4">
      <v-card-title class="text-h5">Your Booking History</v-card-title>
      <v-divider class="my-4"></v-divider>

      <v-alert v-if="!history.length" type="info" class="my-4">
        You have no past bookings.
      </v-alert>

      <v-expansion-panels v-else v-model="expandedPanels">
        <v-expansion-panel v-for="(booking, index) in history" :key="booking.id">
          <v-expansion-panel-title>
            <strong>Scooter ID: </strong> {{ booking.id }}
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <p><strong>Location: </strong> ({{ booking.latitude }}, {{ booking.longitude }})</p>
            <p><strong>Battery: </strong> {{ booking.battery_level }}%</p>
            <p><strong>Duration: </strong> {{ findDuration(booking.booking_time, booking.end_time) }}</p>
            <p><strong>Price: </strong> {{ booking.price }} NOK</p>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
      <v-divider class="my-4"></v-divider>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: 'BookingHistory',
  data() {
    return {
      history: [],
      expandedPanels: []
    }
  },
  async mounted() {
    await this.fetchHistory()
  },
  methods: {
    async fetchHistory() {
      try {
        const response = await fetch('/history')
        const data = await response.json()
        console.log('Booking history:', data)
        if (!response.ok) {
          throw new Error(data.message || 'Failed to fetch booking history')
        }
        this.history = data.history || []
      } catch (err) {
        console.error('Failed to load booking history:', err)
      }
    },
    findDuration(start_time, end_time) {
      const start = new Date(start_time)
      const end = new Date(end_time)
      const duration = Math.abs(end - start) / 1000 // in seconds
      const hours = Math.floor(duration / 3600)
      const minutes = Math.floor((duration % 3600) / 60)
      const seconds = Math.floor(duration % 60)
      const formattedDuration = `${hours}h ${minutes}m ${seconds}s`
      return formattedDuration
    }
  },

}
</script>
