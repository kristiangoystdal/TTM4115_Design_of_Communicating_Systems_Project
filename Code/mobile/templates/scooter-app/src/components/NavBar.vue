<template>
  <v-bottom-navigation app color="primary" grow height="56" class="bottom-navbar">
    <v-btn to="/" icon>
      <v-icon>mdi-home</v-icon> Home
    </v-btn>

    <template v-if="user?.username">
      <v-btn to="/bookings" icon>
        <v-icon>mdi-calendar-check</v-icon> Booking History
      </v-btn>
      <v-btn icon @click="logout">
        <v-icon>mdi-logout</v-icon> Logout
      </v-btn>
    </template>

    <template v-else>
      <v-btn to="/login" icon>
        <v-icon>mdi-login</v-icon> Login
      </v-btn>
      <v-btn to="/register" icon>
        <v-icon>mdi-account-plus</v-icon> Register
      </v-btn>
    </template>
  </v-bottom-navigation>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

export default {
  name: 'BottomNavbar',
  setup() {
    const auth = useAuthStore()
    const { user } = storeToRefs(auth)
    const router = useRouter()

    const logout = async () => {
      try {
        await auth.logout()
        console.log('Logged out successfully')
        router.push('/login')
      } catch (error) {
        console.error('Error during logout:', error)
      }
    }

    return { user, logout }
  }
}

</script>

<style scoped>
.bottom-navbar {
  position: fixed;
  bottom: 0;
  width: 100%;
  z-index: 1001;
}
</style>
