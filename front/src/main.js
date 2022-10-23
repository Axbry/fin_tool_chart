import { createApp } from 'vue'
import App from './App.vue'
import sse from "vue-sse";

const app = createApp(App)

app.use(sse)
app.mount('#app')
