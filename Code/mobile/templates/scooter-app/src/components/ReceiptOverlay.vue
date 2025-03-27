<template>
  <v-dialog v-model="show" max-width="500px" persistent>
    <v-card>
      <v-card-title class="text-h5">Booking Receipt</v-card-title>
      <v-divider></v-divider>

      <v-card-text v-if="booking">
        <p><strong>Scooter ID:</strong> {{ booking.id }}</p>
        <p><strong>Start Time:</strong> {{ booking.booking_time }}</p>
        <p><strong>End Time:</strong> {{ booking.end_time }}</p>
        <p><strong>Duration:</strong> {{ booking.duration }} minutes</p>
        <p><strong>Total Price:</strong> {{ booking.price }} NOK</p>
      </v-card-text>

      <v-card-actions class="justify-end">
        <v-btn text @click="goHome">Return to Home</v-btn>
        <v-btn color="primary" @click="close">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'ReceiptOverlay',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    booking: {
      type: Object,
      required: true
    }
  },
  emits: ['update:show'],
  methods: {
    close() {
      this.$emit('update:show', false)
    },
    goHome() {
      window.location.href = '/'
    }
  }
}
</script>
