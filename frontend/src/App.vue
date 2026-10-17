<script setup>
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <AppHeader />
  <main>
    <RouterView v-slot="{ Component, route }">
      <Transition name="pagina" mode="out-in">
        <component :is="Component" :key="route.path" />
      </Transition>
    </RouterView>
  </main>
  <footer class="pie">
    <div class="contenedor">
      <div class="marca-pie">
        <span class="franja"><i></i><i></i><i></i></span>
        <span>Colegio Privado San Marcos · Galería de Arte Virtual</span>
      </div>
      <span>© {{ new Date().getFullYear() }}</span>
    </div>
  </footer>
</template>

<style scoped>
main {
  min-height: calc(100vh - 150px);
  padding-bottom: 4rem;
}
.pie {
  border-top: 1px solid var(--borde);
  background: var(--superficie);
  color: var(--texto-suave);
  font-size: 0.85rem;
}
.pie .contenedor {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding-block: 1.5rem;
}
.marca-pie {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.franja {
  display: inline-flex;
  border-radius: 999px;
  overflow: hidden;
  box-shadow: 0 0 0 1px var(--borde);
}
.franja i {
  width: 14px;
  height: 6px;
}
.franja i:nth-child(1) {
  background: var(--bordo);
}
.franja i:nth-child(2) {
  background: var(--blanco);
}
.franja i:nth-child(3) {
  background: var(--azul);
}
</style>
