<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'

const usuarios = ref([])
const colegios = ref([])
const error = ref('')
const cargando = ref(true)
const aBorrar = ref(null)
const editandoColegio = ref(null) // id del usuario cuyo colegio se está editando
const nuevoColegio = ref('')

async function cargar() {
  cargando.value = true
  try {
    usuarios.value = await api('/api/usuarios')
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
  api('/api/auth/colegios')
    .then((lista) => (colegios.value = lista))
    .catch(() => {})
}

async function actualizar(usuario, cambios) {
  error.value = ''
  try {
    Object.assign(usuario, await api(`/api/usuarios/${usuario.id}`, { method: 'PATCH', body: cambios }))
    return true
  } catch (e) {
    error.value = e.message
    return false
  }
}

function empezarColegio(usuario) {
  editandoColegio.value = usuario.id
  nuevoColegio.value = usuario.colegio || ''
}

async function guardarColegio(usuario) {
  if (await actualizar(usuario, { colegio: nuevoColegio.value })) editandoColegio.value = null
}

async function borrar(usuario) {
  error.value = ''
  try {
    await api(`/api/usuarios/${usuario.id}`, { method: 'DELETE' })
    usuarios.value = usuarios.value.filter((u) => u.id !== usuario.id)
  } catch (e) {
    error.value = e.message
  } finally {
    aBorrar.value = null
  }
}

const fecha = (iso) => new Date(iso).toLocaleDateString('es-AR', { day: 'numeric', month: 'short', year: 'numeric' })
const iniciales = (nombre) =>
  nombre
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join('')
const invitados = computed(() => usuarios.value.filter((u) => !u.es_admin).length)
const sinPermiso = computed(() => usuarios.value.filter((u) => !u.puede_editar).length)

onMounted(cargar)
</script>

<template>
  <div class="contenedor">
    <header class="encabezado">
      <span class="sobretitulo">Administración</span>
      <h1>Usuarios</h1>
      <p>
        Los <strong>invitados</strong> crean su cuenta desde la web y solo pueden subir, editar y borrar obras de
        <strong>su colegio</strong>. Desde acá podés corregir su colegio o desactivar la cuenta. Los
        <strong>administradores</strong> se definen en el servidor (archivo <code>admins.json</code>).
      </p>
      <div class="resumen">
        <span class="pastilla">{{ invitados }} {{ invitados === 1 ? 'invitado' : 'invitados' }}</span>
        <span v-if="sinPermiso" class="pastilla pastilla-alerta">
          {{ sinPermiso }} {{ sinPermiso === 1 ? 'cuenta sin permisos' : 'cuentas sin permisos' }}
        </span>
      </div>
    </header>

    <div v-if="error" class="alerta alerta-error">{{ error }}</div>
    <div v-if="cargando" class="vacio">Cargando…</div>

    <div v-else class="tabla-envoltura tarjeta">
      <datalist id="colegios-admin">
        <option v-for="c in colegios" :key="c" :value="c" />
      </datalist>
      <table>
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Rol</th>
            <th>Colegio</th>
            <th>Alta</th>
            <th>Activo</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in usuarios" :key="u.id" :class="{ pendiente: !u.puede_editar }">
            <td class="persona">
              <span class="avatar" :class="{ admin: u.es_admin }">{{ iniciales(u.nombre) }}</span>
              <span>
                <strong>{{ u.nombre }}</strong>
                <small>{{ u.email }}</small>
              </span>
            </td>
            <td data-label="Rol">
              <span class="rol" :class="u.es_admin ? 'rol-admin' : 'rol-invitado'">
                {{ u.es_admin ? 'Administrador' : 'Invitado' }}
              </span>
            </td>
            <td data-label="Colegio">
              <span v-if="u.es_admin" class="neutro">Todos</span>
              <form v-else-if="editandoColegio === u.id" class="editar-colegio" @submit.prevent="guardarColegio(u)">
                <input v-model="nuevoColegio" type="text" list="colegios-admin" required minlength="2" maxlength="150" />
                <button class="btn btn-azul btn-chico">Guardar</button>
                <button type="button" class="btn btn-borde btn-chico" aria-label="Cancelar" @click="editandoColegio = null">
                  ×
                </button>
              </form>
              <button v-else class="valor-colegio" title="Cambiar colegio" @click="empezarColegio(u)">
                {{ u.colegio || 'Sin asignar' }}
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" /></svg>
              </button>
            </td>
            <td data-label="Alta">{{ fecha(u.creado) }}</td>
            <td data-label="Activo">
              <span v-if="u.es_admin" class="neutro">—</span>
              <button
                v-else
                class="interruptor"
                role="switch"
                :aria-checked="u.habilitado"
                :class="{ activo: u.habilitado }"
                :aria-label="`${u.habilitado ? 'Desactivar' : 'Activar'} a ${u.nombre}`"
                @click="actualizar(u, { habilitado: !u.habilitado })"
              ></button>
            </td>
            <td class="acciones">
              <template v-if="!u.es_admin">
                <button v-if="aBorrar !== u.id" class="btn btn-peligro btn-chico" @click="aBorrar = u.id">
                  Eliminar
                </button>
                <template v-else>
                  <button class="btn btn-borde btn-chico" @click="aBorrar = null">Cancelar</button>
                  <button class="btn btn-primario btn-chico" @click="borrar(u)">Confirmar</button>
                </template>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.encabezado {
  margin: 2.25rem 0 1.75rem;
}
.encabezado h1 {
  font-size: clamp(2rem, 4vw, 2.8rem);
  margin: 0.5rem 0 0.4rem;
}
.encabezado p {
  margin: 0;
  color: var(--texto-suave);
  max-width: 48rem;
}
code {
  font-size: 0.85em;
  background: var(--azul-claro);
  color: var(--azul-oscuro);
  padding: 0.1rem 0.4rem;
  border-radius: 5px;
}
.resumen {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}
.pastilla {
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  background: var(--azul-claro);
  color: var(--azul);
  font-size: 0.82rem;
  font-weight: 600;
}
.pastilla-alerta {
  background: var(--bordo-claro);
  color: var(--bordo);
}
.tabla-envoltura {
  padding: 0;
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  padding: 1rem 1.25rem;
  text-align: left;
  border-bottom: 1px solid var(--borde);
  vertical-align: middle;
}
tbody tr:last-child td {
  border-bottom: 0;
}
th {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--texto-suave);
  background: var(--fondo);
}
tbody tr {
  transition: background 0.2s;
}
tbody tr:hover {
  background: #fbfaf9;
}
.persona {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}
.persona > span:nth-child(2) {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}
.persona strong {
  font-weight: 600;
}
.persona small {
  color: var(--texto-suave);
  font-size: 0.83rem;
}
.avatar {
  flex-shrink: 0;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--azul-claro);
  color: var(--azul);
  font-size: 0.8rem;
  font-weight: 700;
}
.avatar.admin {
  background: var(--azul);
  color: var(--blanco);
}
tr.pendiente .avatar {
  background: var(--bordo-claro);
  color: var(--bordo);
}
.rol {
  display: inline-block;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 600;
}
.rol-admin {
  background: var(--azul);
  color: var(--blanco);
}
.rol-invitado {
  background: var(--fondo);
  color: var(--texto-suave);
  border: 1px solid var(--borde);
}
.neutro {
  color: var(--texto-suave);
  font-size: 0.88rem;
}
.valor-colegio {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: none;
  border: 1px dashed transparent;
  border-radius: 8px;
  padding: 0.3rem 0.5rem;
  margin-left: -0.5rem;
  font: 500 0.9rem var(--sans);
  color: var(--texto);
  cursor: pointer;
  text-align: left;
}
.valor-colegio svg {
  flex-shrink: 0;
  color: var(--texto-suave);
  opacity: 0;
  transition: opacity 0.2s;
}
.valor-colegio:hover {
  border-color: var(--borde);
}
.valor-colegio:hover svg,
.valor-colegio:focus-visible svg {
  opacity: 1;
}
tr.pendiente .valor-colegio {
  color: var(--bordo);
}
.editar-colegio {
  display: flex;
  gap: 0.4rem;
  min-width: 300px;
}
.editar-colegio input {
  padding: 0.4rem 0.65rem;
  font-size: 0.88rem;
}
.interruptor {
  position: relative;
  width: 44px;
  height: 26px;
  border-radius: 999px;
  border: 0;
  background: #d9d6d0;
  cursor: pointer;
  transition: background 0.25s;
}
.interruptor::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--blanco);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25);
  transition: transform 0.25s var(--transicion);
}
.interruptor.activo {
  background: var(--azul);
}
.interruptor.activo::after {
  transform: translateX(18px);
}
.interruptor:focus-visible {
  outline: 3px solid rgba(27, 54, 93, 0.3);
  outline-offset: 2px;
}
.acciones {
  white-space: nowrap;
  text-align: right;
}
.acciones .btn + .btn {
  margin-left: 0.4rem;
}
@media (max-width: 720px) {
  thead {
    display: none;
  }
  tr {
    display: block;
    padding: 1rem 0;
    border-bottom: 1px solid var(--borde);
  }
  td {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 0;
    padding: 0.4rem 1.25rem;
  }
  td.persona {
    justify-content: flex-start;
    padding-bottom: 0.75rem;
  }
  td[data-label]::before {
    content: attr(data-label);
    font-size: 0.85rem;
    color: var(--texto-suave);
  }
  .valor-colegio svg {
    opacity: 1;
  }
  .editar-colegio {
    min-width: 0;
    flex: 1;
    margin-left: 1rem;
  }
  .acciones {
    justify-content: flex-end;
    padding-top: 0.75rem;
  }
}
</style>
