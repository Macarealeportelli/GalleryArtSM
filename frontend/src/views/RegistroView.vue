<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { login } from '../auth'
import AccesoLayout from '../components/AccesoLayout.vue'

const router = useRouter()
const form = reactive({ nombre: '', email: '', colegio: '', password: '', repetir: '' })
const colegios = ref([])
const error = ref('')
const enviando = ref(false)

async function enviar() {
  error.value = ''
  if (form.password !== form.repetir) {
    error.value = 'Las contraseñas no coinciden'
    return
  }
  enviando.value = true
  try {
    await api('/api/auth/registro', {
      method: 'POST',
      body: { nombre: form.nombre, email: form.email, colegio: form.colegio, password: form.password }
    })
    await login(form.email, form.password)
    router.push({ name: 'galeria' })
  } catch (e) {
    error.value = e.message
  } finally {
    enviando.value = false
  }
}

onMounted(async () => {
  try {
    colegios.value = await api('/api/auth/colegios')
  } catch {
    /* las sugerencias son opcionales */
  }
})
</script>

<template>
  <AccesoLayout
    titulo="Crear cuenta"
    subtitulo="Con tu cuenta vas a poder subir obras de tu colegio, y editar o borrar las que pertenezcan a él."
  >
    <form @submit.prevent="enviar">
      <div v-if="error" class="alerta alerta-error">{{ error }}</div>
      <div class="campo">
        <label for="nombre">Nombre y apellido</label>
        <input id="nombre" v-model="form.nombre" type="text" autocomplete="name" required minlength="2" />
      </div>
      <div class="campo">
        <label for="email">Email</label>
        <input id="email" v-model="form.email" type="email" autocomplete="email" placeholder="nombre@ejemplo.com" required />
      </div>
      <div class="campo">
        <label for="colegio">Colegio</label>
        <input
          id="colegio"
          v-model="form.colegio"
          type="text"
          list="colegios"
          placeholder="Ej.: Colegio San Marcos"
          autocomplete="organization"
          required
          minlength="2"
          maxlength="150"
        />
        <datalist id="colegios">
          <option v-for="c in colegios" :key="c" :value="c" />
        </datalist>
        <span class="ayuda">Si tu colegio aparece en la lista, elegilo tal cual para que tus obras queden agrupadas.</span>
      </div>
      <div class="fila">
        <div class="campo">
          <label for="password">Contraseña</label>
          <input id="password" v-model="form.password" type="password" autocomplete="new-password" required minlength="6" />
          <span class="ayuda">Mínimo 6 caracteres.</span>
        </div>
        <div class="campo">
          <label for="repetir">Repetir contraseña</label>
          <input id="repetir" v-model="form.repetir" type="password" autocomplete="new-password" required />
        </div>
      </div>
      <button class="btn btn-primario ancho" :disabled="enviando">
        {{ enviando ? 'Creando…' : 'Crear cuenta' }}
      </button>
      <p class="alt">¿Ya tenés cuenta? <RouterLink to="/ingresar">Ingresá</RouterLink></p>
    </form>
  </AccesoLayout>
</template>

<style scoped>
.fila {
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
}
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
