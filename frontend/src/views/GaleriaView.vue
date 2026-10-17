<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { api, urlArchivo } from '../api'
import { auth } from '../auth'
import ObraCard from '../components/ObraCard.vue'
import VisorObra from '../components/VisorObra.vue'

const obras = ref([])
const destacadas = ref([]) // últimas obras, para la portada
const resumen = ref({ obras: 0, autores: 0, tecnicas: 0 })
const opciones = ref({ tecnicas: [], colegios: [], anios: [] })
const filtros = reactive({ q: '', tecnica: '', colegio: '', anio: '' })
const cargando = ref(true)
const error = ref('')
const abierta = ref(null) // índice de la obra en el visor

const hayFiltros = computed(() => Object.values(filtros).some(Boolean))

function resumir(lista) {
  resumen.value = {
    obras: lista.length,
    autores: new Set(lista.map((o) => `${o.autor_nombre} ${o.autor_apellido}`.toLowerCase())).size,
    tecnicas: new Set(lista.map((o) => o.tecnica.toLowerCase())).size
  }
  destacadas.value = lista.slice(0, 3)
}

async function cargar() {
  cargando.value = true
  error.value = ''
  const params = new URLSearchParams(Object.entries(filtros).filter(([, v]) => v))
  try {
    obras.value = await api(`/api/obras?${params}`)
    if (!hayFiltros.value) resumir(obras.value)
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}

async function cargarOpciones() {
  try {
    opciones.value = await api('/api/obras/filtros')
  } catch {
    /* los filtros son opcionales */
  }
}

let demora
watch(
  () => ({ ...filtros }),
  () => {
    clearTimeout(demora)
    demora = setTimeout(cargar, 250)
  }
)

function limpiarFiltros() {
  Object.assign(filtros, { q: '', tecnica: '', colegio: '', anio: '' })
}

function elegirTecnica(t) {
  filtros.tecnica = filtros.tecnica === t ? '' : t
}

function mover(paso) {
  const n = obras.value.length
  abierta.value = (abierta.value + paso + n) % n
}

function abrirDestacada(obra) {
  const i = obras.value.findIndex((o) => o.id === obra.id)
  if (i >= 0) abierta.value = i
}

async function borrar(obra) {
  try {
    await api(`/api/obras/${obra.id}`, { method: 'DELETE' })
    abierta.value = null
    obras.value = obras.value.filter((o) => o.id !== obra.id)
    if (!hayFiltros.value) resumir(obras.value)
    cargarOpciones()
  } catch (e) {
    error.value = e.message
    abierta.value = null
  }
}

onMounted(() => {
  cargar()
  cargarOpciones()
})
</script>

<template>
  <div>
    <section class="portada">
      <div class="contenedor portada-grilla">
        <div class="portada-texto">
          <span class="sobretitulo">Colegio San Marcos</span>
          <h1>El arte de <em>nuestros estudiantes</em>, en un solo lugar.</h1>
          <p>Explorá las obras realizadas en las clases de arte: pintura, dibujo, grabado, fotografía y mucho más.</p>
          <div class="cta">
            <a href="#obras" class="btn btn-primario">Explorar la galería</a>
            <RouterLink v-if="auth.puedeEditar" to="/obras/nueva" class="btn btn-borde">Subir obra</RouterLink>
          </div>
          <dl class="cifras">
            <div>
              <dt>Obras</dt>
              <dd>{{ resumen.obras }}</dd>
            </div>
            <div>
              <dt>Artistas</dt>
              <dd>{{ resumen.autores }}</dd>
            </div>
            <div>
              <dt>Técnicas</dt>
              <dd>{{ resumen.tecnicas }}</dd>
            </div>
          </dl>
        </div>

        <div class="collage" :class="`n${destacadas.length}`" aria-hidden="true">
          <button
            v-for="(o, i) in destacadas"
            :key="o.id"
            class="pieza"
            :class="`p${i}`"
            tabindex="-1"
            @click="abrirDestacada(o)"
          >
            <img :src="urlArchivo(o.miniatura_url)" alt="" />
          </button>
          <template v-if="!destacadas.length">
            <span class="forma f1"></span>
            <span class="forma f2"></span>
            <span class="forma f3"></span>
          </template>
        </div>
      </div>
    </section>

    <div id="obras" class="contenedor">
      <div class="herramientas">
        <div class="buscador">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><path d="M20 20l-3.5-3.5" /></svg>
          <input v-model="filtros.q" type="search" placeholder="Buscar por artista, título, técnica…" aria-label="Buscar" />
        </div>
        <select v-model="filtros.colegio" aria-label="Colegio">
          <option value="">Todos los colegios</option>
          <option v-for="c in opciones.colegios" :key="c">{{ c }}</option>
        </select>
        <select v-model="filtros.anio" aria-label="Año">
          <option value="">Todos los años</option>
          <option v-for="a in opciones.anios" :key="a">{{ a }}</option>
        </select>
      </div>

      <div v-if="opciones.tecnicas.length" class="chips" role="group" aria-label="Filtrar por técnica">
        <button class="chip" :class="{ activo: !filtros.tecnica }" @click="filtros.tecnica = ''">Todas</button>
        <button
          v-for="t in opciones.tecnicas"
          :key="t"
          class="chip"
          :class="{ activo: filtros.tecnica === t }"
          @click="elegirTecnica(t)"
        >
          {{ t }}
        </button>
      </div>

      <div class="estado">
        <span>
          {{ obras.length }} {{ obras.length === 1 ? 'obra' : 'obras' }}
          <template v-if="hayFiltros">encontradas</template>
        </span>
        <button v-if="hayFiltros" class="limpiar" @click="limpiarFiltros">Limpiar filtros ×</button>
      </div>

      <div v-if="error" class="alerta alerta-error">{{ error }}</div>

      <div v-if="cargando && !obras.length" class="grilla">
        <div v-for="n in 8" :key="n" class="esqueleto" :style="{ height: `${180 + ((n * 67) % 160)}px` }"></div>
      </div>
      <div v-else-if="!obras.length" class="vacio">
        <div class="vacio-icono">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3" /><circle cx="9" cy="9" r="2" /><path d="M21 15l-5-5L5 21" /></svg>
        </div>
        <h3>{{ hayFiltros ? 'No encontramos obras con esos filtros' : 'Todavía no hay obras' }}</h3>
        <p v-if="hayFiltros"><button class="btn btn-borde" @click="limpiarFiltros">Limpiar filtros</button></p>
        <RouterLink v-else-if="auth.puedeEditar" to="/obras/nueva" class="btn btn-primario">Subir la primera obra</RouterLink>
      </div>
      <div v-else class="grilla">
        <ObraCard
          v-for="(obra, i) in obras"
          :key="obra.id"
          :obra="obra"
          :style="{ animationDelay: `${Math.min(i, 12) * 40}ms` }"
          @abrir="abierta = i"
        />
      </div>
    </div>

    <VisorObra
      v-if="abierta !== null && obras[abierta]"
      :obra="obras[abierta]"
      :posicion="`${abierta + 1} / ${obras.length}`"
      @cerrar="abierta = null"
      @anterior="mover(-1)"
      @siguiente="mover(1)"
      @borrar="borrar"
    />
  </div>
</template>

<style scoped>
/* Portada */
.portada {
  position: relative;
  overflow: hidden;
  padding: clamp(2.5rem, 6vw, 5rem) 0 clamp(2.5rem, 5vw, 4rem);
}
.portada::before {
  content: '';
  position: absolute;
  inset: -40% -10% auto auto;
  width: 60vw;
  height: 60vw;
  max-width: 820px;
  max-height: 820px;
  background: radial-gradient(circle, rgba(27, 54, 93, 0.1), transparent 65%);
  pointer-events: none;
}
.portada-grilla {
  position: relative;
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: clamp(2rem, 5vw, 4rem);
  align-items: center;
}
.portada h1 {
  font-size: clamp(2.4rem, 5.5vw, 4.4rem);
  margin: 0.75rem 0 1.25rem;
}
.portada h1 em {
  color: var(--bordo);
  font-weight: 500;
}
.portada p {
  font-size: 1.12rem;
  color: var(--texto-suave);
  max-width: 34rem;
  margin: 0 0 2rem;
}
.cta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.cifras {
  display: flex;
  gap: clamp(1.5rem, 4vw, 3rem);
  margin: 2.75rem 0 0;
  padding-top: 1.75rem;
  border-top: 1px solid var(--borde);
}
.cifras div {
  display: flex;
  flex-direction: column-reverse;
}
.cifras dt {
  font-size: 0.82rem;
  color: var(--texto-suave);
}
.cifras dd {
  margin: 0;
  font-family: var(--display);
  font-size: 2.2rem;
  font-weight: 600;
  color: var(--azul-oscuro);
  line-height: 1;
}

/* Collage de la portada */
.collage {
  position: relative;
  aspect-ratio: 1 / 0.92;
  width: 100%;
  max-width: 560px;
  justify-self: end;
}
.pieza,
.forma {
  position: absolute;
  border-radius: 22px;
  overflow: hidden;
  border: 0;
  padding: 0;
  box-shadow: var(--sombra-fuerte);
}
.pieza {
  cursor: pointer;
  background: var(--azul-claro);
  transition: transform 0.5s var(--transicion);
}
.pieza img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.pieza:hover {
  transform: translateY(-6px) rotate(0deg) !important;
  z-index: 5;
}
.p0,
.f1 {
  inset: 0 22% 18% 0;
  transform: rotate(-2deg);
}
.p1,
.f2 {
  width: 46%;
  height: 52%;
  right: 0;
  top: 8%;
  transform: rotate(3deg);
  border: 6px solid var(--blanco);
}
.p2,
.f3 {
  width: 40%;
  height: 40%;
  left: 30%;
  bottom: 0;
  transform: rotate(-4deg);
  border: 6px solid var(--blanco);
}
.n1 .p0 {
  inset: 0;
  transform: rotate(-1.5deg);
}
.n2 .p0 {
  inset: 0 22% 8% 0;
}
.n2 .p1 {
  top: auto;
  bottom: 0;
}
.f1 {
  background: linear-gradient(135deg, var(--azul) 0%, var(--azul-oscuro) 100%);
}
.f2 {
  background: linear-gradient(135deg, var(--bordo) 0%, var(--bordo-oscuro) 100%);
}
.f3 {
  background: var(--azul-claro);
}

/* Herramientas de búsqueda */
.herramientas {
  display: grid;
  grid-template-columns: 1fr 220px 180px;
  gap: 0.75rem;
  padding: 0.6rem;
  background: var(--superficie);
  border: 1px solid var(--borde);
  border-radius: 999px;
  box-shadow: var(--sombra);
  scroll-margin-top: 90px;
}
.herramientas select,
.buscador input {
  border: 0;
  border-radius: 999px;
  background-color: var(--fondo);
}
.buscador {
  position: relative;
  display: flex;
  align-items: center;
}
.buscador svg {
  position: absolute;
  left: 1rem;
  color: var(--texto-suave);
  pointer-events: none;
}
.buscador input {
  padding-left: 2.75rem;
}
.chips {
  display: flex;
  gap: 0.5rem;
  margin: 1.25rem 0 0;
  overflow-x: auto;
  padding-bottom: 0.25rem;
  scrollbar-width: none;
}
.chips::-webkit-scrollbar {
  display: none;
}
.chip {
  flex-shrink: 0;
  padding: 0.45rem 1rem;
  border-radius: 999px;
  border: 1px solid var(--borde);
  background: var(--superficie);
  color: var(--texto);
  font: 500 0.86rem var(--sans);
  cursor: pointer;
  transition: all 0.2s;
}
.chip:hover {
  border-color: var(--azul);
}
.chip.activo {
  background: var(--azul-oscuro);
  border-color: var(--azul-oscuro);
  color: var(--blanco);
}
.estado {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 1.5rem 0 1.25rem;
  font-size: 0.88rem;
  color: var(--texto-suave);
}
.limpiar {
  background: none;
  border: 0;
  color: var(--bordo);
  font: 600 0.86rem var(--sans);
  cursor: pointer;
}

/* Grilla tipo mosaico */
.grilla {
  columns: 4 270px;
  column-gap: 1.75rem;
}
.esqueleto {
  break-inside: avoid;
  margin-bottom: 1.75rem;
  border-radius: var(--radio);
  background: linear-gradient(110deg, #ecebe8 30%, #f5f4f2 50%, #ecebe8 70%);
  background-size: 200% 100%;
  animation: brillo 1.4s linear infinite;
}
.vacio-icono {
  display: inline-grid;
  place-items: center;
  width: 84px;
  height: 84px;
  border-radius: 50%;
  background: var(--azul-claro);
  color: var(--azul);
  margin-bottom: 0.5rem;
}
.vacio h3 {
  font-size: 1.5rem;
  margin: 0.75rem 0 1.25rem;
}
@keyframes brillo {
  to {
    background-position: -200% 0;
  }
}

@media (max-width: 900px) {
  .portada-grilla {
    grid-template-columns: 1fr;
  }
  .collage {
    justify-self: center;
    max-width: 440px;
  }
  .herramientas {
    grid-template-columns: 1fr 1fr;
    border-radius: var(--radio);
  }
  .buscador {
    grid-column: 1 / -1;
  }
}
@media (max-width: 520px) {
  .collage {
    display: none;
  }
  .grilla {
    columns: 2 150px;
    column-gap: 0.9rem;
  }
}
</style>
