import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/components/Login.vue'
import AccountPage from '@/components/Account.vue'
import MapView from '@/components/MapView.vue'
import Register from '@/components/Register.vue'
import ActiveBookings from '@/components/ActiveBookings.vue'
import BookingHistory from '@/components/BookingHistory.vue'


import type { RouteRecordRaw } from 'vue-router';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: MapView,

  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/account',
    name: 'Account',
    component: AccountPage,
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: {
      template: '<h1>404 - Page Not Found</h1>'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
  },
  {
    path: '/active-bookings',
    name: 'ActiveBookings',
    component: ActiveBookings,
  },
  {
    path: '/bookings',
    name: 'BookingHistory',
    component: BookingHistory,
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
