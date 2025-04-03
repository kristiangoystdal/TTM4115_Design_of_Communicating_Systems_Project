<template>
  <v-container class="py-8">
    <v-card elevation="2" class="pa-4">
      <v-card-title class="text-h5">Your Active Bookings</v-card-title>
      <v-divider></v-divider>

      <v-alert v-if="!bookings.length" type="info" class="my-4">
        You don't have any active bookings.
      </v-alert>

      <v-list v-else>
        <v-list-item
          v-for="booking in bookings"
          :key="booking.id"
          class="mb-4"
        >
          <v-card outlined>
            <v-card-text>
              <p><strong>Scooter ID:</strong> {{ booking.id }}</p>
              <p><strong>Location:</strong> ({{ booking.latitude }}, {{ booking.longitude }})</p>
              <p><strong>Battery:</strong> {{ booking.battery_level }}%</p>
              <p><strong>Booked At:</strong> {{ booking.booking_time }}</p>

              <v-btn
                color="error"
                class="mt-3"
                @click="endBooking(booking.id)"
              >
                End Booking
              </v-btn>
            </v-card-text>
          </v-card>
        </v-list-item>
      </v-list>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: 'ActiveBookings',
  data() {
    return {
      bookings: [] // Loaded via fetch or prop
    }
  },
  async mounted() {
    await this.fetchBookings()
  },
  methods: {
    async fetchBookings() {
      try {
        const response = await fetch('/bookings')
        const data = await response.json()
        this.bookings = data.bookings || []
      } catch (err) {
        console.error('Failed to load bookings:', err)
      }
    },
    async endBooking(id) {
      try {
        const response = await fetch(`/end_booking/${id}`, {
          method: 'POST'
        })

        if (response.ok) {
          this.bookings = this.bookings.filter(b => b.id !== id)
        } else {
          console.error('Failed to end booking')
        }
      } catch (err) {
        console.error('Error ending booking:', err)
      }
    }
  }
}
</script>
