<script setup>
defineProps({ obra: { type: Object, required: true } })
</script>

<template>
  <div class="epigrafe">
    <div class="autor">{{ obra.autor_nombre }} {{ obra.autor_apellido }}</div>
    <div v-if="obra.titulo" class="titulo">{{ obra.titulo }}</div>
    <div class="detalle">{{ obra.tecnica }}, {{ obra.anio }}</div>
    <div class="detalle">{{ obra.colegio }}</div>
  </div>
</template>
