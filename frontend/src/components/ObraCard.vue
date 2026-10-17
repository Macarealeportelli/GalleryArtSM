<script setup>
import { ref } from 'vue'
import { urlArchivo } from '../api'

defineProps({ obra: { type: Object, required: true } })
defineEmits(['abrir'])
const cargada = ref(false)
</script>

<template>
  <article class="obra" tabindex="0" @click="$emit('abrir')" @keydown.enter="$emit('abrir')">
    <div class="marco" :class="{ cargada }">
      <img
        :src="urlArchivo(obra.miniatura_url)"
        :alt="`${obra.titulo || 'Obra'} de ${obra.autor_nombre} ${obra.autor_apellido}`"
        loading="lazy"
        @load="cargada = true"
      />
      <div class="velo">
        <span class="ver">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" /></svg>
        </span>
        <span class="tecnica">{{ obra.tecnica }} · {{ obra.anio }}</span>
      </div>
    </div>
    <div class="epigrafe pie-obra">
      <div v-if="obra.titulo" class="titulo">{{ obra.titulo }}</div>
      <div class="autor">{{ obra.autor_nombre }} {{ obra.autor_apellido }}</div>
      <div class="detalle">{{ obra.colegio }}</div>
    </div>
  </article>
</template>

<style scoped>
.obra {
  break-inside: avoid;
  margin-bottom: 1.75rem;
  cursor: zoom-in;
  outline: none;
  animation: aparecer 0.5s var(--transicion) both;
}
.marco {
  position: relative;
  border-radius: var(--radio);
  overflow: hidden;
  background: linear-gradient(110deg, #ecebe8 30%, #f5f4f2 50%, #ecebe8 70%);
  background-size: 200% 100%;
  animation: brillo 1.4s linear infinite;
  box-shadow: var(--sombra);
  transition: box-shadow 0.35s var(--transicion), transform 0.35s var(--transicion);
}
.marco.cargada {
  animation: none;
  background: var(--azul-claro);
}
.marco img {
  width: 100%;
  height: auto;
  min-height: 160px;
  object-fit: cover;
  opacity: 0;
  transform: scale(1.02);
  transition: opacity 0.5s ease, transform 0.6s var(--transicion);
}
.marco.cargada img {
  opacity: 1;
  transform: none;
}
.velo {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  padding: 0.85rem;
  background: linear-gradient(180deg, rgba(14, 31, 56, 0) 45%, rgba(14, 31, 56, 0.75) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}
.ver {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  color: var(--azul-oscuro);
  transform: scale(0.8);
  transition: transform 0.3s var(--transicion);
}
.tecnica {
  align-self: flex-start;
  color: var(--blanco);
  font-size: 0.82rem;
  font-weight: 500;
  transform: translateY(6px);
  transition: transform 0.3s var(--transicion);
}
.obra:hover .marco,
.obra:focus-visible .marco {
  transform: translateY(-4px);
  box-shadow: var(--sombra-fuerte);
}
.obra:hover img,
.obra:focus-visible img {
  transform: scale(1.04);
}
.obra:hover .velo,
.obra:focus-visible .velo {
  opacity: 1;
}
.obra:hover .ver,
.obra:hover .tecnica,
.obra:focus-visible .ver,
.obra:focus-visible .tecnica {
  transform: none;
}
.obra:focus-visible .marco {
  outline: 3px solid var(--bordo);
  outline-offset: 3px;
}
.pie-obra {
  padding: 0.8rem 0.25rem 0;
}
.pie-obra .titulo {
  font-size: 1.08rem;
  line-height: 1.25;
  margin-bottom: 0.1rem;
}
@keyframes brillo {
  to {
    background-position: -200% 0;
  }
}
@keyframes aparecer {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
}
@media (hover: none) {
  .velo {
    opacity: 1;
    background: linear-gradient(180deg, rgba(14, 31, 56, 0) 60%, rgba(14, 31, 56, 0.6) 100%);
  }
  .ver {
    display: none;
  }
  .tecnica {
    transform: none;
  }
}
</style>
