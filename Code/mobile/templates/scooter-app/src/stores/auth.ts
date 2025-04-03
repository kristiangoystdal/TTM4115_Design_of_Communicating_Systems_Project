import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null
  }),

  actions: {
    /**
     * Called after login to set and store user info.
     */
    login(userData: { username: string }) {
      this.user = userData
      localStorage.setItem('user', JSON.stringify(userData))
    },

    /**
     * Logs out user from backend and clears local session.
     */
    async logout() {
      try {
        await fetch('/logout', {
          method: 'POST',
          credentials: 'include'
        })
      } catch (err) {
        console.warn('Backend logout failed:', err)
      }

      this.user = null
      localStorage.removeItem('user')
    },

    /**
     * Tries to get the current user from the backend (/me).
     * Useful on app load or refresh to restore session.
     */
    async fetchUser() {
      try {
        const res = await fetch('/me', {
          method: 'GET',
          credentials: 'include'
        })

        if (!res.ok) throw new Error('Session expired')

        const data = await res.json()
        this.user = { username: data.username }
        localStorage.setItem('user', JSON.stringify(this.user))
      } catch (err) {
        this.user = null
        localStorage.removeItem('user')
        console.warn('No valid session found:', err)
      }
    }
  }
})
