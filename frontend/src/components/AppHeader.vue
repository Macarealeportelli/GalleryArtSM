<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { auth, logout } from '../auth'

const router = useRouter()
const route = useRoute()
const menuAbierto = ref(false)
const conSombra = ref(false)

const iniciales = computed(() =>
  (auth.usuario?.nombre || '?')
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join('')
)

watch(() => route.fullPath, () => (menuAbierto.value = false))

const alDesplazar = () => (conSombra.value = window.scrollY > 8)
onMounted(() => window.addEventListener('scroll', alDesplazar, { passive: true }))
onBeforeUnmount(() => window.removeEventListener('scroll', alDesplazar))

function salir() {
  logout()
  router.push({ name: 'galeria' })
}
</script>

<template>
  <header class="cabecera" :class="{ conSombra }">
    <div class="contenedor barra">
      <RouterLink to="/" class="marca">
        <img src="/escudo.png" alt="Escudo del Colegio San Marcos" width="42" height="54" />
        <span>
          <small>Colegio Privado San Marcos</small>
          <strong>Galería de Arte Virtual</strong>
        </span>
      </RouterLink>

      <button
        class="hamburguesa"
        :class="{ abierto: menuAbierto }"
        :aria-expanded="menuAbierto"
        aria-label="Menú"
        @click="menuAbierto = !menuAbierto"
      >
        <span></span><span></span>
      </button>

      <nav :class="{ abierto: menuAbierto }">
        <div class="enlaces">
          <RouterLink to="/">Galería</RouterLink>
          <RouterLink v-if="auth.esAdmin" to="/usuarios">Usuarios</RouterLink>
        </div>

        <div class="acciones">
          <template v-if="auth.logueado">
            <RouterLink v-if="auth.puedeEditar" to="/obras/nueva" class="btn btn-primario btn-chico">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
              Subir obra
            </RouterLink>
            <span v-else class="pendiente" title="Contactá a un administrador">
              ● {{ auth.usuario?.habilitado ? 'Sin colegio asignado' : 'Cuenta desactivada' }}
            </span>
            <div class="perfil">
              <span class="avatar" :title="auth.usuario?.email">{{ iniciales }}</span>
              <span class="datos">
                <span class="nombre">{{ auth.usuario?.nombre }}</span>
                <span class="rol">{{ auth.esAdmin ? 'Administrador/a' : auth.usuario?.colegio || 'Invitado/a' }}</span>
              </span>
            </div>
            <button class="btn btn-borde btn-chico" @click="salir">Salir</button>
          </template>
          <RouterLink v-else to="/ingresar" class="btn btn-primario btn-chico">Ingresar</RouterLink>
        </div>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.cabecera {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(248, 247, 245, 0.78);
  backdrop-filter: saturate(180%) blur(14px);
  -webkit-backdrop-filter: saturate(180%) blur(14px);
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.cabecera.conSombra {
  border-bottom-color: var(--borde);
  box-shadow: 0 6px 24px -12px rgba(14, 31, 56, 0.18);
}
.barra {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  gap: 1.5rem;
}
.marca {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  text-decoration: none;
  color: var(--texto);
}
.marca img {
  height: 54px;
  width: auto;
  filter: drop-shadow(0 2px 4px rgba(14, 31, 56, 0.15));
}
.marca span {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}
.marca small {
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.66rem;
  font-weight: 600;
  color: var(--bordo);
}
.marca strong {
  font-family: var(--display);
  font-weight: 600;
  font-size: 1.25rem;
  color: var(--azul-oscuro);
  letter-spacing: -0.01em;
}
nav {
  display: flex;
  align-items: center;
  flex: 1;
  justify-content: space-between;
  gap: 1.5rem;
}
.enlaces {
  display: flex;
  gap: 0.25rem;
  margin-left: 1rem;
}
.enlaces a {
  color: var(--texto-suave);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.93rem;
  padding: 0.45rem 0.9rem;
  border-radius: 999px;
  transition: color 0.2s, background 0.2s;
}
.enlaces a:hover {
  color: var(--texto);
  background: rgba(14, 31, 56, 0.05);
}
.enlaces a.router-link-exact-active {
  color: var(--azul-oscuro);
  background: var(--azul-claro);
}
.acciones {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.perfil {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--azul);
  color: var(--blanco);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.datos {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.rol {
  font-size: 0.74rem;
  color: var(--texto-suave);
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.nombre {
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--texto);
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pendiente {
  background: var(--bordo-claro);
  color: var(--bordo);
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
}
.hamburguesa {
  display: none;
  background: none;
  border: 0;
  cursor: pointer;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  position: relative;
}
.hamburguesa span {
  position: absolute;
  left: 11px;
  width: 20px;
  height: 2px;
  border-radius: 2px;
  background: var(--azul-oscuro);
  transition: transform 0.25s var(--transicion), top 0.25s var(--transicion);
}
.hamburguesa span:first-child {
  top: 16px;
}
.hamburguesa span:last-child {
  top: 24px;
}
.hamburguesa.abierto span:first-child {
  top: 20px;
  transform: rotate(45deg);
}
.hamburguesa.abierto span:last-child {
  top: 20px;
  transform: rotate(-45deg);
}

@media (max-width: 820px) {
  .hamburguesa {
    display: block;
  }
  nav {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
    background: var(--superficie);
    padding: 1rem clamp(1rem, 4vw, 2.5rem) 1.5rem;
    border-bottom: 1px solid var(--borde);
    box-shadow: 0 18px 30px -18px rgba(14, 31, 56, 0.3);
    opacity: 0;
    transform: translateY(-8px);
    pointer-events: none;
    transition: opacity 0.2s, transform 0.25s var(--transicion);
  }
  nav.abierto {
    opacity: 1;
    transform: none;
    pointer-events: auto;
  }
  .enlaces {
    flex-direction: column;
    margin: 0;
  }
  .enlaces a {
    padding: 0.7rem 0.9rem;
    font-size: 1rem;
  }
  .acciones {
    flex-wrap: wrap;
    padding-top: 1rem;
    border-top: 1px solid var(--borde);
  }
  .perfil {
    order: -1;
    width: 100%;
  }
}
</style>
