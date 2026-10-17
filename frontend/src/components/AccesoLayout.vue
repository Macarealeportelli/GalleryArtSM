<script setup>
defineProps({
  titulo: { type: String, required: true },
  subtitulo: { type: String, default: '' }
})
</script>

<template>
  <div class="contenedor">
    <div class="acceso">
      <aside class="arte" aria-hidden="true">
        <div class="formas">
          <span class="c1"></span>
          <span class="c2"></span>
          <span class="c3"></span>
        </div>
        <div class="cita">
          <span class="sobretitulo">Galería de Arte</span>
          <p>“Todo niño es un artista. El problema es cómo seguir siendo artista una vez que crecemos.”</p>
          <small>— Pablo Picasso</small>
        </div>
      </aside>

      <section class="formulario">
        <h1>{{ titulo }}</h1>
        <p v-if="subtitulo" class="subtitulo">{{ subtitulo }}</p>
        <slot />
      </section>
    </div>
  </div>
</template>

<style scoped>
.acceso {
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin-top: 2rem;
  min-height: 600px;
  background: var(--superficie);
  border: 1px solid var(--borde);
  border-radius: 28px;
  overflow: hidden;
  box-shadow: var(--sombra);
}
.arte {
  position: relative;
  overflow: hidden;
  background: linear-gradient(150deg, var(--azul) 0%, var(--azul-oscuro) 70%);
  color: var(--blanco);
  display: flex;
  align-items: flex-end;
  padding: 2.5rem;
}
.formas span {
  position: absolute;
  border-radius: 50%;
}
.c1 {
  width: 360px;
  height: 360px;
  background: var(--bordo);
  top: -90px;
  right: -110px;
  opacity: 0.9;
}
.c2 {
  width: 180px;
  height: 180px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  top: 150px;
  left: 40px;
}
.c3 {
  width: 70px;
  height: 70px;
  background: var(--blanco);
  top: 90px;
  left: 210px;
}
.cita {
  position: relative;
  max-width: 26rem;
}
.cita .sobretitulo {
  color: rgba(255, 255, 255, 0.7);
}
.cita p {
  font-family: var(--display);
  font-style: italic;
  font-size: 1.55rem;
  line-height: 1.3;
  margin: 0.75rem 0;
}
.cita small {
  color: rgba(255, 255, 255, 0.7);
}
.formulario {
  padding: clamp(2rem, 5vw, 4rem);
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-width: 520px;
  width: 100%;
  margin: 0 auto;
}
h1 {
  font-size: 2.3rem;
  margin: 0 0 0.5rem;
}
.subtitulo {
  color: var(--texto-suave);
  margin: 0 0 2rem;
}
@media (max-width: 820px) {
  .acceso {
    grid-template-columns: 1fr;
    min-height: 0;
    margin-top: 1rem;
  }
  .arte {
    display: none;
  }
}
</style>
