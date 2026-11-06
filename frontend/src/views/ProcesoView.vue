<script setup>
import { computed, onMounted, ref } from 'vue'
import { api, urlArchivo } from '../api'
import { auth, puedeGestionar } from '../auth'
import { prepararImagen } from '../imagen'

const obras = ref([])
const buscando = ref(true)
const artistaBuscado = ref('')
const error = ref('')
const obraAbierta = ref(null)
const imagen = ref(null)
const descripcion = ref('')
const procesando = ref(false)
const guardando = ref(false)
const claveInput = ref(0)

function normalizar(texto) {
  return texto
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .toLocaleLowerCase('es')
}

const grupos = computed(() => {
  const porArtista = new Map()
  for (const obra of obras.value) {
    const artista = `${obra.autor_nombre} ${obra.autor_apellido}`.trim()
    const clave = normalizar(artista)
    if (!porArtista.has(clave)) porArtista.set(clave, { clave, artista, obras: [] })
    porArtista.get(clave).obras.push(obra)
  }
  const busqueda = normalizar(artistaBuscado.value)
  return [...porArtista.values()]
    .filter((grupo) => normalizar(grupo.artista).includes(busqueda))
    .sort((a, b) => a.artista.localeCompare(b.artista, 'es', { sensitivity: 'base' }))
})

async function cargar() {
  buscando.value = true
  error.value = ''
  try {
    obras.value = await api('/api/obras')
  } catch (e) {
    error.value = e.message
  } finally {
    buscando.value = false
  }
}

function abrirCarga(obra) {
  error.value = ''
  imagen.value = null
  descripcion.value = ''
  obraAbierta.value = obraAbierta.value === obra.id ? null : obra.id
  claveInput.value += 1
}

function cancelarCarga() {
  obraAbierta.value = null
  imagen.value = null
  descripcion.value = ''
  error.value = ''
  claveInput.value += 1
}

async function elegirImagen(event) {
  error.value = ''
  const seleccionada = event.target.files?.[0]
  event.target.value = ''
  if (!seleccionada) return
  if (!seleccionada.type.startsWith('image/')) {
    error.value = 'El archivo debe ser una imagen (JPG, PNG, WEBP o GIF)'
    imagen.value = null
    return
  }

  procesando.value = true
  try {
    imagen.value = await prepararImagen(seleccionada)
  } catch (e) {
    error.value = e.message
    imagen.value = null
  } finally {
    procesando.value = false
  }
}

async function guardarProceso(obra) {
  if (!imagen.value) {
    error.value = 'Seleccioná una imagen del proceso'
    return
  }

  const datos = new FormData()
  datos.append('imagen', imagen.value)
  datos.append('descripcion', descripcion.value)
  guardando.value = true
  error.value = ''
  try {
    const actualizada = await api(`/api/obras/${obra.id}/proceso`, { method: 'POST', form: datos })
    obras.value = obras.value.map((item) => (item.id === actualizada.id ? actualizada : item))
    cancelarCarga()
  } catch (e) {
    error.value = e.message
  } finally {
    guardando.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <div class="contenedor seccion-proceso">
    <header class="encabezado">
      <span class="sobretitulo">Galería de arte · San Marcos</span>
      <h1>Proceso de obra</h1>
      <p>Buscá un artista para ver sus obras y las etapas de creación reunidas.</p>
    </header>

    <div class="busqueda-artista">
      <label for="buscar-artista">Filtrar por nombre de artista</label>
      <input
        id="buscar-artista"
        v-model="artistaBuscado"
        type="search"
        placeholder="Escribí el nombre o apellido…"
      />
      <span>{{ grupos.length }} {{ grupos.length === 1 ? 'artista' : 'artistas' }}</span>
    </div>

    <div v-if="error && obraAbierta === null" class="alerta alerta-error">{{ error }}</div>
    <div v-if="buscando" class="vacio">Cargando obras y procesos…</div>
    <div v-else-if="!grupos.length && !error" class="vacio">
      {{ obras.length ? 'No encontramos artistas con ese nombre.' : 'Todavía no hay obras para mostrar.' }}
    </div>

    <section v-for="grupo in grupos" :key="grupo.clave" class="grupo-artista">
      <header class="cabecera-artista">
        <h2>{{ grupo.artista }}</h2>
        <span>{{ grupo.obras.length }} {{ grupo.obras.length === 1 ? 'obra' : 'obras' }}</span>
      </header>

      <article v-for="obra in grupo.obras" :key="obra.id" class="tarjeta obra-proceso">
        <div class="obra-final">
          <a :href="urlArchivo(obra.imagen_url)" target="_blank" rel="noopener">
            <img :src="urlArchivo(obra.miniatura_url)" :alt="obra.titulo || `Obra de ${grupo.artista}`" loading="lazy" />
          </a>
          <div class="datos-obra">
            <span class="sobretitulo">Obra final · {{ obra.anio }}</span>
            <h3>{{ obra.titulo || 'Sin título' }}</h3>
            <p>{{ obra.tecnica }} · {{ obra.colegio }}</p>
            <p v-if="obra.proceso_descripcion" class="descripcion-general">{{ obra.proceso_descripcion }}</p>
          </div>
        </div>

        <div class="etapas">
          <h3>Etapas del proceso <span>({{ obra.proceso.length }}/12)</span></h3>
          <div v-if="obra.proceso.length" class="grilla-etapas">
            <a
              v-for="etapa in obra.proceso"
              :key="etapa.id"
              class="etapa"
              :href="urlArchivo(etapa.imagen_url)"
              target="_blank"
              rel="noopener"
            >
              <img :src="urlArchivo(etapa.miniatura_url)" :alt="etapa.descripcion || 'Imagen del proceso'" loading="lazy" />
              <span v-if="etapa.descripcion">{{ etapa.descripcion }}</span>
            </a>
          </div>
          <p v-else class="sin-etapas">Todavía no se cargaron imágenes del proceso.</p>

          <button
            v-if="puedeGestionar(obra) && obra.proceso.length < 12"
            class="btn btn-borde btn-chico"
            :disabled="guardando || procesando"
            @click="abrirCarga(obra)"
          >
            {{ obraAbierta === obra.id ? 'Cerrar formulario' : 'Agregar etapa' }}
          </button>
          <p v-else-if="auth.logueado && !puedeGestionar(obra)" class="ayuda">
            Solo una cuenta con permisos sobre este colegio puede agregar etapas.
          </p>

          <form v-if="obraAbierta === obra.id" class="formulario-proceso" @submit.prevent="guardarProceso(obra)">
            <div v-if="error" class="alerta alerta-error">{{ error }}</div>
            <label>
              Imagen del proceso
              <input :key="claveInput" type="file" accept="image/*" required @change="elegirImagen" />
            </label>
            <span v-if="imagen" class="ayuda">Imagen lista: {{ imagen.name }}</span>
            <span v-if="procesando" class="ayuda">Optimizando imagen…</span>
            <label>
              Descripción <span class="ayuda">(opcional)</span>
              <textarea v-model="descripcion" maxlength="300" rows="2" placeholder="Boceto inicial, mezcla de colores…"></textarea>
            </label>
            <div class="acciones-formulario">
              <button type="button" class="btn btn-borde btn-chico" :disabled="guardando" @click="cancelarCarga">Cancelar</button>
              <button class="btn btn-primario btn-chico" :disabled="guardando || procesando">
                {{ guardando ? 'Guardando…' : 'Guardar etapa' }}
              </button>
            </div>
          </form>
        </div>
      </article>
    </section>
  </div>
</template>

<style scoped>
.seccion-proceso {
  padding-bottom: 3rem;
}
.encabezado {
  margin: 2.5rem 0 1.75rem;
}
.encabezado h1 {
  font-size: clamp(2rem, 4vw, 2.8rem);
  margin: 0.6rem 0 0.4rem;
}
.encabezado p {
  color: var(--texto-suave);
  margin: 0;
}
.busqueda-artista {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.5rem 1rem;
  align-items: center;
  max-width: 720px;
  margin-bottom: 2rem;
}
.busqueda-artista label {
  grid-column: 1 / -1;
  font-weight: 600;
  font-size: 0.88rem;
}
.busqueda-artista span,
.cabecera-artista span,
.etapas h3 span {
  color: var(--texto-suave);
  font-size: 0.85rem;
}
.grupo-artista {
  margin-top: 2.5rem;
}
.cabecera-artista {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  border-bottom: 1px solid var(--borde);
  margin-bottom: 1rem;
}
.cabecera-artista h2 {
  font-size: 1.6rem;
  margin: 0 0 0.8rem;
}
.obra-proceso {
  display: grid;
  grid-template-columns: minmax(220px, 0.8fr) minmax(0, 1.2fr);
  gap: 1.5rem;
  margin-bottom: 1rem;
}
.obra-final img {
  width: 100%;
  max-height: 340px;
  object-fit: contain;
  border-radius: var(--radio-chico);
  background: var(--fondo);
}
.datos-obra {
  padding-top: 0.8rem;
}
.datos-obra h3 {
  margin: 0.35rem 0;
  font-size: 1.35rem;
}
.datos-obra p {
  margin: 0.25rem 0;
  color: var(--texto-suave);
}
.datos-obra .descripcion-general {
  margin-top: 0.75rem;
  color: var(--texto);
}
.etapas h3 {
  margin: 0 0 0.75rem;
  font-family: var(--sans);
  font-size: 0.95rem;
}
.grilla-etapas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
  margin-bottom: 0.9rem;
}
.etapa {
  color: var(--texto);
  font-size: 0.8rem;
  text-decoration: none;
}
.etapa img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: var(--radio-chico);
  background: var(--fondo);
  margin-bottom: 0.3rem;
}
.sin-etapas,
.ayuda {
  color: var(--texto-suave);
  font-size: 0.84rem;
}
.formulario-proceso {
  display: grid;
  gap: 0.75rem;
  margin-top: 1rem;
  padding: 1rem;
  background: var(--fondo);
  border: 1px solid var(--borde);
  border-radius: var(--radio-chico);
}
.formulario-proceso label {
  display: grid;
  gap: 0.4rem;
  font-size: 0.85rem;
  font-weight: 600;
}
.formulario-proceso input[type='file'] {
  max-width: 100%;
  font: 0.85rem var(--sans);
}
.formulario-proceso textarea {
  width: 100%;
  resize: vertical;
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--borde);
  border-radius: var(--radio-chico);
  font: 0.92rem var(--sans);
}
.formulario-proceso textarea:focus {
  outline: none;
  border-color: var(--azul);
  box-shadow: 0 0 0 4px rgba(27, 54, 93, 0.12);
}
.acciones-formulario {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

@media (max-width: 720px) {
  .obra-proceso {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
  .datos-obra {
    padding-top: 0.6rem;
  }
}
</style>
