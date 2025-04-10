<template>
  <v-dialog v-model="localOpen" max-width="400">
    <v-card>
      <v-card-title>Scooter {{ scooter.id }}</v-card-title>
      <v-card-text>
        <p>Battery: {{ scooter.battery_level }}%</p>
        <br>
        <p v-if="scooter.is_user_booked && !scooter.is_driving">
          This scooter is booked by you.
        </p>

        <v-btn v-if="!scooter.is_driving" :disabled="loading" color="secondary" block class="mt-2"
          @click="scooter.is_user_booked ? cancelScooter() : bookScooter()">
          {{ scooter.is_user_booked ? 'Cancel Reservation' : 'Reserve Scooter' }}
        </v-btn>

        <v-btn :disabled="loading" color="primary" block class="mt-2" @click="toggleDrive">
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
import { ref, computed } from 'vue'
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
const loading = ref(false)

const handleFetchResponse = async (response) => {
  if (response.status === 401) {
    toast.error('You must be logged in to perform this action.')
    router.push('/login')
    return null
  } else if (response.status === 403) {
    toast.error('You do not have permission to perform this action.')
    return null
  } else if (response.status === 404) {
    toast.error('Scooter not found.')
    return null
  } else if (response.status === 500) {
    toast.error('Server error. Please try again later.')
    return null
  } else if (response.status === 503) {
    toast.error('Service unavailable. Please try again later.')
    return null
  } else if (response.status === 429) {
    toast.error('Too many requests. Please try again later.')
    return null
  } else if (response.status === 400) {
    toast.error('Bad request. Please check your input.')
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
  loading.value = true
  const response = await fetch(`/book/${props.scooter.id}`, {
    method: 'POST',
  })
  const data = await handleFetchResponse(response)
  if (data) {
    localOpen.value = false
    toast.success('Scooter booked successfully!')
  }
  loading.value = false
}

const cancelScooter = async () => {
  loading.value = true
  const response = await fetch(`/end_booking/${props.scooter.id}`, {
    method: 'POST',
    body: {
      on_charging_station: false, // this function is for someone who is cancelling a reservation, meaning they have not started a drive
    },
  })
  const data = await handleFetchResponse(response)
  if (data) {
    localOpen.value = false
    toast.success('Reservation canceled successfully!')
  }
  loading.value = false
}

const toggleDrive = async (on_charging_station = false) => {
  loading.value = true
  const end_drive = props.scooter.is_driving
  const response = await fetch(`${end_drive ? "/end_drive" : "/start_drive"}/${props.scooter.id}`, {
    method: 'POST',
    body: {
      on_charging_station: on_charging_station,
    },
  })
  const data = await handleFetchResponse(response)
  if (data) {
    localOpen.value = false
    toast.success(
      end_drive ? 'Drive ended successfully!' : 'Drive started successfully!'
    )
    if (end_drive) {
      emit('drive-data', data)
      console.log(data)
    }
  }
  loading.value = false
}
</script>
