import { auth, logout } from './auth'

const BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export const urlArchivo = (ruta) => BASE + ruta

export async function api(ruta, { method = 'GET', body, form } = {}) {
  const headers = {}
  if (auth.token) headers.Authorization = `Bearer ${auth.token}`

  let payload
  if (form) {
    payload = form
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    payload = JSON.stringify(body)
  }

  const res = await fetch(BASE + ruta, { method, headers, body: payload })

  if (res.status === 401 && auth.token) logout()

  if (!res.ok) {
    let mensaje = `Error ${res.status}`
    try {
      const datos = await res.json()
      if (typeof datos.detail === 'string') mensaje = datos.detail
      else if (Array.isArray(datos.detail)) mensaje = datos.detail.map((e) => e.msg).join('. ')
    } catch {
      /* respuesta sin JSON */
    }
    throw new Error(mensaje)
  }
  return res.status === 204 ? null : res.json()
}
