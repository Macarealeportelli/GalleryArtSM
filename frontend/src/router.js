import { createRouter, createWebHistory } from 'vue-router'
import { auth } from './auth'
import GaleriaView from './views/GaleriaView.vue'

const routes = [
  { path: '/', name: 'galeria', component: GaleriaView },
  { path: '/ingresar', name: 'login', component: () => import('./views/LoginView.vue') },
  { path: '/registro', name: 'registro', component: () => import('./views/RegistroView.vue') },
  {
    path: '/obras/nueva',
    name: 'nueva',
    component: () => import('./views/ObraFormView.vue'),
    meta: { requiereHabilitado: true }
  },
  {
    path: '/obras/:id/editar',
    name: 'editar',
    component: () => import('./views/ObraFormView.vue'),
    props: true,
    meta: { requiereHabilitado: true }
  },
  {
    path: '/usuarios',
    name: 'usuarios',
    component: () => import('./views/UsuariosView.vue'),
    meta: { requiereAdmin: true }
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach((to) => {
  if ((to.meta.requiereHabilitado || to.meta.requiereAdmin) && !auth.logueado) {
    return { name: 'login', query: { volver: to.fullPath } }
  }
  if (to.meta.requiereHabilitado && !auth.puedeEditar) return { name: 'galeria' }
  if (to.meta.requiereAdmin && !auth.esAdmin) return { name: 'galeria' }
})

export default router
