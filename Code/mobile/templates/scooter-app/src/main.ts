/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'

// Styles 
// import './styles/index.css'

// Router
import router from './router'

// Toastification
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'

const app = createApp(App)

registerPlugins(app)
app.use(router)
app.use(Toast)

app.mount('#app')
