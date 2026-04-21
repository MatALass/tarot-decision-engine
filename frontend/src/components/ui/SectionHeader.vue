<script setup lang="ts">
defineProps<{
  eyebrow?: string
  title: string
  description: string
}>()
</script>

<template>
  <div class="mb-8">
    <p v-if="eyebrow" class="text-xs uppercase tracking-[0.3em] text-slate-500">{{ eyebrow }}</p>
    <h2 class="mt-2 text-3xl font-semibold text-white">{{ title }}</h2>
    <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-400">{{ description }}</p>
  </div>
</template>
