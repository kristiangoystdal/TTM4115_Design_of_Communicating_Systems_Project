<template>
  <v-dialog v-model="localOpen" max-width="400">
    <v-card>
      <v-card-title>Scooter {{ scooter.id }}</v-card-title>
      <v-card-text>
        <p>Battery: {{ scooter.battery_level }}%</p>

        <p v-if="scooter.is_user_booked && !scooter.is_driving">
          This scooter is booked by you.
        </p>

        <form v-else :action="`/book/${scooter.id}`" method="POST">
          <v-btn type="submit" color="primary" block>Book</v-btn>
        </form>

        <form :action="scooter.is_driving
          ? `/end_drive/${scooter.id}`
          : `/start_drive/${scooter.id}`" method="POST">
          <v-btn type="submit" color="secondary" block class="mt-2">
            {{ scooter.is_driving ? 'End Drive' : 'Start Drive' }}
          </v-btn>
        </form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn text @click="localOpen = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  scooter: Object,
})

const emit = defineEmits(['update:modelValue'])

const localOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})
</script>
