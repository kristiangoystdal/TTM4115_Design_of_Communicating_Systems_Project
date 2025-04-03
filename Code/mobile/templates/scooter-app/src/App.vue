<template>
  <v-app>
    <v-main>
      <v-container>
        <router-view />
        <NavBar></NavBar>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  import NavBar from './components/NavBar.vue';

  const username = ref(null); // You can bind this to a real auth system
</script>
