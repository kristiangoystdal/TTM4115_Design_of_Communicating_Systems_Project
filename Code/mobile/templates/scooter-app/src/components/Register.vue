<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="4">
        <v-card elevation="4">
          <v-card-title class="text-h5 justify-center">Register</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleRegister" ref="registerForm">
              <v-text-field
                label="Username"
                v-model="form.username"
                prepend-icon="mdi-account"
                required
              ></v-text-field>

              <v-text-field
                label="Password"
                v-model="form.password"
                type="password"
                prepend-icon="mdi-lock"
                required
              ></v-text-field>

              <v-btn type="submit" color="primary" block class="mt-4">
                Register
              </v-btn>

              <v-alert v-if="error" type="error" dense class="mt-3">
                {{ error }}
              </v-alert>
            </v-form>
          </v-card-text>

          <v-card-actions class="justify-center">
            <v-btn text to="/login">Already have an account? Login</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'RegisterForm',
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
    async handleRegister() {
      try {
        const response = await fetch('/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.form)
        })

        if (response.redirected) {
          window.location.href = response.url
        } else {
          const data = await response.json()
          if (data.error) {
            this.error = data.error
          }
        }
      } catch (err) {
        this.error = 'Something went wrong during registration.'
        console.error(err)
      }
    }
  }
}
</script>
