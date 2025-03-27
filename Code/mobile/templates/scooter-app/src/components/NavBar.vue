<template>
  <nav class="bottom-navbar">
    <router-link to="/">Home</router-link>
    <template v-if="username">
      <router-link to="/bookings">Bookings</router-link>
      <router-link to="/logout">Logout</router-link>
    </template>
    <template v-else>
      <router-link to="/login">Login</router-link>
      <router-link to="/register">Register</router-link>
    </template>
  </nav>
</template>

<script>
export default {
  name: 'BottomNavbar',
  props: {
    username: String
  }
}
</script>

<style scoped>
.bottom-navbar {
  position: fixed;
  bottom: 0;
  width: 100%;
  background-color: #2c3e50;
  color: white;
  display: flex;
  justify-content: space-around;
  padding: 10px 0;
  z-index: 1001;
}

.bottom-navbar a {
  color: white;
  text-decoration: none;
}
</style>
