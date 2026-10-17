<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { login } from '../auth'
import AccesoLayout from '../components/AccesoLayout.vue'

const router = useRouter()
const route = useRoute()
const email = ref('')
const password = ref('')
const error = ref('')
const enviando = ref(false)

async function enviar() {
  error.value = ''
  enviando.value = true
  try {
    await login(email.value, password.value)
    router.push(route.query.volver || '/')
  } catch (e) {
    error.value = e.message
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <AccesoLayout titulo="Bienvenido/a" subtitulo="Ingresá para subir y gestionar las obras de la galería.">
    <form @submit.prevent="enviar">
      <div v-if="error" class="alerta alerta-error">{{ error }}</div>
      <div class="campo">
        <label for="email">Email</label>
        <input id="email" v-model="email" type="email" autocomplete="email" placeholder="nombre@ejemplo.com" required />
      </div>
      <div class="campo">
        <label for="password">Contraseña</label>
        <input id="password" v-model="password" type="password" autocomplete="current-password" required />
      </div>
      <button class="btn btn-primario ancho" :disabled="enviando">
        {{ enviando ? 'Ingresando…' : 'Ingresar' }}
      </button>
      <p class="alt">¿No tenés cuenta? <RouterLink to="/registro">Creá una</RouterLink></p>
    </form>
  </AccesoLayout>
</template>

<style scoped>
.ancho {
  width: 100%;
  margin-top: 0.5rem;
  padding-block: 0.85rem;
}
.alt {
  text-align: center;
  margin: 1.5rem 0 0;
  color: var(--texto-suave);
  font-size: 0.92rem;
}
.alt a {
  font-weight: 600;
}
</style>
