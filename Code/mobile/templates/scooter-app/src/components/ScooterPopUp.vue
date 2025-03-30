<template>
  <v-dialog v-model="localOpen" max-width="400">
    <v-card>
      <v-card-title>Scooter {{ scooter.id }}</v-card-title>
      <v-card-text>
        <p>Battery: {{ scooter.battery_level }}%</p>

        <p v-if="scooter.is_user_booked && !scooter.is_driving">
          This scooter is booked by you.
        </p>

        <v-btn v-else color="primary" block @click="bookScooter">
          Book
        </v-btn>

        <v-btn color="secondary" block class="mt-2" @click="toggleDrive">
          {{ scooter.is_driving ? 'End Drive' : 'Start Drive' }}
        </v-btn>
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
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import 'vue-toastification/dist/index.css'

const toast = useToast()

const props = defineProps({
  modelValue: Boolean,
  scooter: Object,
})

const emit = defineEmits(['update:modelValue'])

const localOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const router = useRouter()

const handleFetchResponse = async (response) => {
  if (response.status === 401) {
    toast.error('You must be logged in to perform this action.')
    router.push('/login')
    return null
  }

  try {
    const json = await response.json()
    return response.ok ? json : null
  } catch (err) {
    toast.error('Server returned an invalid response.')
    return null
  }
}

const bookScooter = async () => {
  const response = await fetch(`/book/${props.scooter.id}`, {
    method: 'POST',
  })
  const data = await handleFetchResponse(response)
  if (data) {
    // Update scooter state if needed
    // props.scooter.is_user_booked = true
    localOpen.value = false
    // router.push('/')
    toast.success('Scooter booked successfully!')
  }
}

const toggleDrive = async () => {
  const endpoint = props.scooter.is_driving
    ? `/end_drive/${props.scooter.id}`
    : `/start_drive/${props.scooter.id}`
  const response = await fetch(endpoint, {
    method: 'POST',
  })
  const data = await handleFetchResponse(response)
  if (data) {
    // Update scooter state if needed
    props.scooter.is_driving = !props.scooter.is_driving
  }
}
</script>
