<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { puedeGestionar } from '../auth'
import { urlArchivo } from '../api'

const props = defineProps({
  obra: { type: Object, required: true },
  posicion: { type: String, default: '' }
})
const emit = defineEmits(['cerrar', 'anterior', 'siguiente', 'borrar'])
const confirmando = ref(false)
const cargada = ref(false)

watch(
  () => props.obra.id,
  () => {
    confirmando.value = false
    cargada.value = false
  }
)

function teclas(e) {
  if (e.key === 'Escape') emit('cerrar')
  if (e.key === 'ArrowLeft') emit('anterior')
  if (e.key === 'ArrowRight') emit('siguiente')
}

// Deslizar con el dedo para pasar de obra en el celular
let inicioX = null
const tocar = (e) => (inicioX = e.touches[0].clientX)
function soltar(e) {
  if (inicioX === null) return
  const dx = e.changedTouches[0].clientX - inicioX
  if (Math.abs(dx) > 50) emit(dx > 0 ? 'anterior' : 'siguiente')
  inicioX = null
}

onMounted(() => {
  window.addEventListener('keydown', teclas)
  document.body.style.overflow = 'hidden'
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', teclas)
  document.body.style.overflow = ''
})
</script>

<template>
  <div class="fondo" role="dialog" aria-modal="true" @click.self="emit('cerrar')">
    <div class="escenario" @click.self="emit('cerrar')" @touchstart.passive="tocar" @touchend="soltar">
      <img
        :key="obra.id"
        :src="urlArchivo(obra.imagen_url)"
        :alt="obra.titulo || 'Obra'"
        :class="{ cargada }"
        @load="cargada = true"
      />
      <button class="nav izq" aria-label="Anterior" @click="emit('anterior')">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6" /></svg>
      </button>
      <button class="nav der" aria-label="Siguiente" @click="emit('siguiente')">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6" /></svg>
      </button>
    </div>

    <aside class="panel">
      <div class="panel-sup">
        <span class="posicion">{{ posicion }}</span>
        <button class="cerrar" aria-label="Cerrar" @click="emit('cerrar')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12" /></svg>
        </button>
      </div>

      <div class="ficha">
        <span class="sobretitulo">{{ obra.tecnica }}</span>
        <h2>{{ obra.titulo || 'Sin título' }}</h2>
        <dl>
          <div>
            <dt>Autor</dt>
            <dd>{{ obra.autor_nombre }} {{ obra.autor_apellido }}</dd>
          </div>
          <div>
            <dt>Año</dt>
            <dd>{{ obra.anio }}</dd>
          </div>
          <div>
            <dt>Técnica</dt>
            <dd>{{ obra.tecnica }}</dd>
          </div>
          <div>
            <dt>Colegio</dt>
            <dd>{{ obra.colegio }}</dd>
          </div>
        </dl>
      </div>

      <div class="acciones">
        <a class="btn btn-borde btn-chico" :href="urlArchivo(obra.imagen_url)" target="_blank" rel="noopener">
          Ver original
        </a>
        <template v-if="puedeGestionar(obra)">
          <RouterLink class="btn btn-azul btn-chico" :to="`/obras/${obra.id}/editar`">Editar</RouterLink>
          <button v-if="!confirmando" class="btn btn-peligro btn-chico" @click="confirmando = true">Borrar</button>
        </template>
        <div v-if="confirmando" class="confirmar">
          <span>¿Borrar esta obra definitivamente?</span>
          <div>
            <button class="btn btn-borde btn-chico" @click="confirmando = false">Cancelar</button>
            <button class="btn btn-primario btn-chico" @click="emit('borrar', props.obra)">Sí, borrar</button>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.fondo {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  grid-template-columns: 1fr 380px;
  background: rgba(9, 16, 30, 0.96);
  backdrop-filter: blur(6px);
  animation: entrar 0.25s ease both;
}
.escenario {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2.5rem 5rem;
  min-height: 0;
}
.escenario img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 30px 80px -20px rgba(0, 0, 0, 0.6);
  opacity: 0;
  transform: scale(0.985);
  transition: opacity 0.35s ease, transform 0.45s var(--transicion);
}
.escenario img.cargada {
  opacity: 1;
  transform: none;
}
.nav,
.cerrar {
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s var(--transicion);
}
.nav {
  position: absolute;
  top: 50%;
  translate: 0 -50%;
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--blanco);
}
.nav:hover {
  background: var(--bordo);
  transform: scale(1.06);
}
.izq {
  left: 1.25rem;
}
.der {
  right: 1.25rem;
}
.panel {
  background: var(--superficie);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1.75rem 1.75rem;
  overflow-y: auto;
  animation: deslizar 0.35s var(--transicion) both;
}
.panel-sup {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.posicion {
  font-size: 0.8rem;
  color: var(--texto-suave);
  font-variant-numeric: tabular-nums;
}
.cerrar {
  width: 40px;
  height: 40px;
  background: var(--fondo);
  color: var(--texto);
}
.cerrar:hover {
  background: var(--bordo-claro);
  color: var(--bordo);
}
.ficha {
  flex: 1;
  padding-top: 2rem;
}
.ficha h2 {
  font-size: 2rem;
  font-style: italic;
  font-weight: 500;
  margin: 0.4rem 0 1.75rem;
}
dl {
  margin: 0;
  display: grid;
  gap: 0;
}
dl div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 0;
  border-top: 1px solid var(--borde);
}
dl div:last-child {
  border-bottom: 1px solid var(--borde);
}
dt {
  color: var(--texto-suave);
  font-size: 0.85rem;
}
dd {
  margin: 0;
  font-weight: 600;
  text-align: right;
  font-size: 0.92rem;
}
.acciones {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding-top: 1.5rem;
}
.confirmar {
  width: 100%;
  margin-top: 0.5rem;
  padding: 1rem;
  border-radius: var(--radio-chico);
  background: var(--bordo-claro);
  color: var(--bordo-oscuro);
  font-size: 0.9rem;
  font-weight: 500;
}
.confirmar div {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
@keyframes entrar {
  from {
    opacity: 0;
  }
}
@keyframes deslizar {
  from {
    transform: translateX(30px);
    opacity: 0;
  }
}

@media (max-width: 900px) {
  .fondo {
    grid-template-columns: 1fr;
    grid-template-rows: minmax(0, 1fr) auto;
  }
  .escenario {
    padding: 1rem;
  }
  .nav {
    top: auto;
    bottom: 1rem;
    translate: none;
    width: 42px;
    height: 42px;
  }
  .izq {
    left: auto;
    right: 4.25rem;
  }
  .der {
    right: 1rem;
  }
  .panel {
    border-radius: 22px 22px 0 0;
    max-height: 48vh;
    padding: 1.1rem 1.25rem 1.5rem;
    animation-name: subir;
  }
  .ficha {
    padding-top: 0.5rem;
  }
  .ficha h2 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
  }
  dl div {
    padding: 0.55rem 0;
  }
  @keyframes subir {
    from {
      transform: translateY(40px);
      opacity: 0;
    }
  }
}
</style>
