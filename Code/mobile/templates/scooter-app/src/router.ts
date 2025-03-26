import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Home from './components/HelloWorld.vue'
import LoginPage from './components/Login.vue'
import AccountPage from './components/Account.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: Home,

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
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
