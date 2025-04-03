<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="4">
        <v-card elevation="4">
          <v-card-title class="text-h5 justify-center">Login</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleLogin" ref="loginForm">
              <v-text-field label="Username" v-model="form.username" prepend-icon="mdi-account" required />
              <v-text-field label="Password" v-model="form.password" type="password" prepend-icon="mdi-lock" required />

              <v-btn type="submit" color="primary" block class="mt-4">Login</v-btn>

              <v-alert v-if="error" type="error" dense class="mt-3">
                {{ error }}
              </v-alert>
            </v-form>
          </v-card-text>

          <v-card-actions class="justify-center">
            <v-btn text to="/register">Don't have an account? Register</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useToast } from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'LoginForm',
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      try {
        const response = await fetch('/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include', // 🔥 important: include cookie!
          body: JSON.stringify(this.form)
        })

        const data = await response.json()

        if (response.ok) {
          const auth = useAuthStore()
          auth.login({ username: this.form.username })
          useToast().success('Login successful!')
          this.$router.push('/')
        } else {
          this.error = data.error || 'Login failed.'
        }
      } catch (err) {
        this.error = 'Something went wrong during login.'
        console.error(err)
      }
    }
  }
}
</script>
