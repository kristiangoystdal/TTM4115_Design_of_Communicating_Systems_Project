<template>
  <v-container class="py-8">
    <v-card elevation="2" class="pa-4">
      <v-card-title class="text-h5">Your Booking History</v-card-title>
      <v-divider></v-divider>

      <v-alert v-if="!history.length" type="info" class="my-4">
        You have no past bookings.
      </v-alert>

      <v-list v-else>
        <v-list-item
          v-for="booking in history"
          :key="booking.id"
          class="mb-4"
        >
          <v-card outlined>
            <v-card-text>
              <p><strong>Scooter ID:</strong> {{ booking.id }}</p>
              <p><strong>Location:</strong> ({{ booking.latitude }}, {{ booking.longitude }})</p>
              <p><strong>Battery:</strong> {{ booking.battery_level }}%</p>
              <p><strong>Booked At:</strong> {{ booking.booking_time }}</p>
              <p><strong>Ended At:</strong> {{ booking.end_time }}</p>
              <p><strong>Price:</strong> {{ booking.price }} NOK</p>
            </v-card-text>
          </v-card>
        </v-list-item>
      </v-list>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: 'BookingHistory',
  data() {
    return {
      history: [] // Fetched on mount
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
        this.history = data.history || []
      } catch (err) {
        console.error('Failed to load booking history:', err)
      }
    }
  }
}
</script>
