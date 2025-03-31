<template>
  <v-bottom-navigation app color="primary" grow height="56" class="bottom-navbar">
    <v-btn to="/" icon>
      <v-icon>mdi-home</v-icon>
    </v-btn>

    <template v-if="user?.username">
      <v-btn to="/bookings" icon>
        <v-icon>mdi-calendar-check</v-icon>
      </v-btn>
      <v-btn icon @click="logout">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </template>

    <template v-else>
      <v-btn to="/login" icon>
        <v-icon>mdi-login</v-icon>
      </v-btn>
      <v-btn to="/register" icon>
        <v-icon>mdi-account-plus</v-icon>
      </v-btn>
    </template>
  </v-bottom-navigation>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'

export default {
  name: 'BottomNavbar',
  setup() {
    const auth = useAuthStore()
    const { user } = storeToRefs(auth)

    const logout = async () => {
      try {
        await auth.logout() // Assuming the `logout` method is defined in the auth store
        
        console.log('Logged out successfully')
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
