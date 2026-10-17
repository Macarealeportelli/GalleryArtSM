<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, urlArchivo } from '../api'
import { auth, puedeGestionar } from '../auth'
import Epigrafe from '../components/Epigrafe.vue'

const props = defineProps({ id: { type: String, default: null } })
const router = useRouter()
const editando = computed(() => !!props.id)

const TECNICAS = [
  'Acrílico',
  'Acuarela',
  'Arte digital',
  'Carbonilla',
  'Collage',
  'Escultura',
  'Fotografía',
  'Grabado',
  'Lápiz grafito',
  'Lápices de color',
  'Óleo',
  'Pastel',
  'Témpera',
  'Técnica mixta',
  'Tinta'
]

const form = reactive({
  titulo: '',
  autor_nombre: '',
  autor_apellido: '',
  anio: new Date().getFullYear(),
  tecnica: '',
  // El invitado siempre publica con el colegio de su perfil
  colegio: auth.esAdmin ? 'Colegio San Marcos' : auth.usuario?.colegio || ''
})
const archivo = ref(null)
const vistaPrevia = ref('')
const arrastrando = ref(false)
const colegios = ref([])
const error = ref('')
const enviando = ref(false)
const cargando = ref(false)
const sinPermiso = ref(false)

const MAX_MB = 15

function elegir(file) {
  error.value = ''
  if (!file) return
  if (!file.type.startsWith('image/')) {
    error.value = 'El archivo debe ser una imagen (JPG, PNG, WEBP o GIF)'
    return
  }
  if (file.size > MAX_MB * 1024 * 1024) {
    error.value = `La imagen supera los ${MAX_MB} MB`
    return
  }
  if (vistaPrevia.value.startsWith('blob:')) URL.revokeObjectURL(vistaPrevia.value)
  archivo.value = file
  vistaPrevia.value = URL.createObjectURL(file)
}

function soltar(e) {
  arrastrando.value = false
  elegir(e.dataTransfer.files[0])
}

async function enviar() {
  error.value = ''
  if (!editando.value && !archivo.value) {
    error.value = 'Seleccioná una imagen de la obra'
    return
  }
  const datos = new FormData()
  for (const [k, v] of Object.entries(form)) datos.append(k, v ?? '')
  if (archivo.value) datos.append('imagen', archivo.value)

  enviando.value = true
  try {
    await api(editando.value ? `/api/obras/${props.id}` : '/api/obras', {
      method: editando.value ? 'PUT' : 'POST',
      form: datos
    })
    router.push({ name: 'galeria' })
  } catch (e) {
    error.value = e.message
  } finally {
    enviando.value = false
  }
}

onMounted(async () => {
  api('/api/auth/colegios')
    .then((lista) => (colegios.value = lista))
    .catch(() => {})
  if (!editando.value) return
  cargando.value = true
  try {
    const obra = await api(`/api/obras/${props.id}`)
    if (!puedeGestionar(obra)) {
      sinPermiso.value = true
      return
    }
    Object.assign(form, {
      titulo: obra.titulo || '',
      autor_nombre: obra.autor_nombre,
      autor_apellido: obra.autor_apellido,
      anio: obra.anio,
      tecnica: obra.tecnica,
      colegio: obra.colegio
    })
    vistaPrevia.value = urlArchivo(obra.miniatura_url)
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
})

onBeforeUnmount(() => {
  if (vistaPrevia.value.startsWith('blob:')) URL.revokeObjectURL(vistaPrevia.value)
})
</script>

<template>
  <div class="contenedor">
    <header class="encabezado">
      <RouterLink to="/" class="volver">← Volver a la galería</RouterLink>
      <h1>{{ editando ? 'Editar obra' : 'Subir una obra' }}</h1>
      <p>Completá el epígrafe y elegí una imagen de buena calidad. Se verá así en la galería.</p>
    </header>

    <div v-if="cargando" class="vacio">Cargando…</div>
    <div v-else-if="sinPermiso" class="alerta alerta-error">
      Esta obra pertenece a otro colegio. Solo podés editar obras de <strong>{{ auth.usuario?.colegio }}</strong>.
    </div>
    <form v-else class="tarjeta formulario" @submit.prevent="enviar">
      <div
        class="zona"
        :class="{ arrastrando, conImagen: vistaPrevia }"
        @dragover.prevent="arrastrando = true"
        @dragleave="arrastrando = false"
        @drop.prevent="soltar"
      >
        <label class="selector">
          <img v-if="vistaPrevia" :src="vistaPrevia" alt="Vista previa" />
          <span v-else class="indicacion">
            <span class="icono">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4M6 10l6-6 6 6" /><path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" /></svg>
            </span>
            <strong>Arrastrá la imagen aquí</strong>
            o tocá para elegirla / sacar una foto
            <small>JPG, PNG, WEBP o GIF · hasta {{ MAX_MB }} MB</small>
          </span>
          <input type="file" accept="image/*" @change="elegir($event.target.files[0])" />
        </label>
        <p v-if="vistaPrevia" class="cambiar">Tocá la imagen para reemplazarla</p>
      </div>

      <div class="datos">
        <div v-if="error" class="alerta alerta-error">{{ error }}</div>

        <h3>Epígrafe</h3>
        <div class="fila">
          <div class="campo">
            <label for="nombre">Nombre del autor *</label>
            <input id="nombre" v-model="form.autor_nombre" type="text" required maxlength="100" />
          </div>
          <div class="campo">
            <label for="apellido">Apellido del autor *</label>
            <input id="apellido" v-model="form.autor_apellido" type="text" required maxlength="100" />
          </div>
        </div>
        <div class="campo">
          <label for="titulo">Título de la obra</label>
          <input id="titulo" v-model="form.titulo" type="text" maxlength="200" placeholder="Opcional" />
        </div>
        <div class="fila">
          <div class="campo">
            <label for="anio">Año *</label>
            <input id="anio" v-model.number="form.anio" type="number" min="1900" max="2100" required />
          </div>
          <div class="campo">
            <label for="tecnica">Técnica *</label>
            <input id="tecnica" v-model="form.tecnica" type="text" list="tecnicas" required maxlength="150" />
            <datalist id="tecnicas">
              <option v-for="t in TECNICAS" :key="t" :value="t" />
            </datalist>
          </div>
        </div>
        <div class="campo">
          <label for="colegio">Colegio *</label>
          <input
            id="colegio"
            v-model="form.colegio"
            type="text"
            list="colegios"
            required
            maxlength="150"
            :readonly="!auth.esAdmin"
          />
          <span v-if="!auth.esAdmin" class="ayuda">Se asigna automáticamente el colegio de tu perfil.</span>
          <datalist id="colegios">
            <option v-for="c in colegios" :key="c" :value="c" />
          </datalist>
        </div>

        <div class="previa-epigrafe">
          <span class="ayuda">Así se verá el epígrafe:</span>
          <Epigrafe
            :obra="{
              ...form,
              autor_nombre: form.autor_nombre || 'Nombre',
              autor_apellido: form.autor_apellido || 'Apellido',
              tecnica: form.tecnica || 'Técnica'
            }"
          />
        </div>

        <div class="botones">
          <RouterLink to="/" class="btn btn-borde">Cancelar</RouterLink>
          <button class="btn btn-primario" :disabled="enviando">
            {{ enviando ? 'Guardando…' : editando ? 'Guardar cambios' : 'Publicar obra' }}
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<style scoped>
.encabezado {
  margin: 2.25rem 0 1.75rem;
}
.volver {
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--texto-suave);
  text-decoration: none;
}
.volver:hover {
  color: var(--bordo);
}
.encabezado h1 {
  font-size: clamp(2rem, 4vw, 2.8rem);
  margin: 0.75rem 0 0.4rem;
}
.encabezado p {
  margin: 0;
  color: var(--texto-suave);
}
.formulario {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) 1.2fr;
  gap: clamp(1.5rem, 4vw, 3rem);
}
h3 {
  margin: 0 0 1.25rem;
  font-size: 1.4rem;
}
.zona {
  display: flex;
  flex-direction: column;
}
.selector {
  position: relative;
  flex: 1;
  min-height: 360px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed #d3d0ca;
  border-radius: var(--radio);
  background: var(--fondo);
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.2s, background 0.2s;
}
.zona.arrastrando .selector,
.selector:hover {
  border-color: var(--bordo);
  background: var(--bordo-claro);
}
.zona.conImagen .selector {
  border: 0;
  background: #0e1525;
}
.selector img {
  max-height: 560px;
  object-fit: contain;
}
.selector input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}
.indicacion {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  text-align: center;
  color: var(--texto-suave);
  padding: 1.5rem;
  font-size: 0.92rem;
}
.icono {
  display: grid;
  place-items: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--superficie);
  color: var(--bordo);
  box-shadow: var(--sombra);
  margin-bottom: 0.75rem;
  transition: transform 0.3s var(--transicion);
}
.selector:hover .icono {
  transform: translateY(-4px);
}
.indicacion strong {
  font-size: 1.05rem;
  color: var(--texto);
}
.indicacion small {
  margin-top: 0.5rem;
  font-size: 0.78rem;
}
.cambiar {
  text-align: center;
  font-size: 0.82rem;
  color: var(--texto-suave);
  margin: 0.75rem 0 0;
}
.previa-epigrafe {
  background: var(--fondo);
  border: 1px solid var(--borde);
  padding: 1rem 1.15rem;
  border-radius: var(--radio-chico);
  margin: 0.5rem 0 1.75rem;
  position: relative;
}
.previa-epigrafe::before {
  content: '';
  position: absolute;
  left: 0;
  top: 1rem;
  bottom: 1rem;
  width: 3px;
  border-radius: 3px;
  background: var(--bordo);
}
.previa-epigrafe .ayuda {
  display: block;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--texto-suave);
  margin-bottom: 0.4rem;
}
.botones {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--borde);
}
@media (max-width: 860px) {
  .formulario {
    grid-template-columns: 1fr;
  }
  .selector {
    min-height: 240px;
  }
  .botones .btn {
    flex: 1;
  }
}
input[readonly] {
  background: var(--azul-claro);
  color: var(--azul-oscuro);
  cursor: not-allowed;
}
</style>
