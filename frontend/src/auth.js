import { reactive } from 'vue'
import { api } from './api'

const CLAVE = 'galeria-sesion'
const guardado = JSON.parse(localStorage.getItem(CLAVE) || 'null')

export const auth = reactive({
  token: guardado?.token ?? null,
  usuario: guardado?.usuario ?? null,

  get logueado() {
    return !!this.token
  },
  get puedeEditar() {
    return !!this.usuario?.puede_editar
  },
  get esAdmin() {
    return !!this.usuario?.es_admin
  }
})

const normalizar = (s) => (s || '').trim().replace(/\s+/g, ' ').toLocaleLowerCase('es')

// Admin: cualquier obra. Invitado: solo las obras de su colegio.
export function puedeGestionar(obra) {
  if (auth.esAdmin) return true
  return auth.puedeEditar && !!obra && normalizar(obra.colegio) === normalizar(auth.usuario.colegio)
}

function persistir() {
  if (auth.token) localStorage.setItem(CLAVE, JSON.stringify({ token: auth.token, usuario: auth.usuario }))
  else localStorage.removeItem(CLAVE)
}

export async function login(email, password) {
  const datos = await api('/api/auth/login', { method: 'POST', body: { email, password } })
  auth.token = datos.access_token
  auth.usuario = datos.usuario
  persistir()
}

export function logout() {
  auth.token = null
  auth.usuario = null
  persistir()
}

// Actualiza permisos por si un administrador habilitó/deshabilitó el perfil.
export async function refrescarUsuario() {
  if (!auth.token) return
  try {
    auth.usuario = await api('/api/auth/yo')
    persistir()
  } catch {
    /* si la sesión venció, api() ya cerró la sesión */
  }
}
