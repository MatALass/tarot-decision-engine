<script setup lang="ts">
defineProps<{
  eyebrow?: string
  title: string
  description?: string
}>()
</script>

<template>
  <div class="mb-7">
    <div v-if="eyebrow" class="mb-2 flex items-center gap-2">
      <div class="h-px w-6 bg-gold/50"></div>
      <span class="text-xs font-medium tracking-[0.3em] text-gold uppercase">{{ eyebrow }}</span>
    </div>
    <h2 class="font-display text-2xl font-semibold tracking-wide text-text">{{ title }}</h2>
    <p v-if="description" class="mt-2 text-sm text-subtle leading-relaxed max-w-2xl">{{ description }}</p>
  </div>
</template>
