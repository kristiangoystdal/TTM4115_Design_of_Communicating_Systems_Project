<template>
  <nav class="bottom-navbar">
    <a href="/">Elleve</a>
    <template v-if="username">
      <a href="/bookings">Bookings</a>
      <a href="/logout">Logout</a>
    </template>
    <template v-else>
      <a href="/login">Login</a>
      <a href="/register">Register</a>
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
