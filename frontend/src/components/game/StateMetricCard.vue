<script setup lang="ts">
defineProps<{
  label: string
  value: string
  hint?: string
}>()
</script>

<template>
  <div class="rounded-xl border border-border bg-panel p-4" style="box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);">
    <div class="text-[10px] tracking-[0.25em] text-subtle uppercase mb-2">{{ label }}</div>
    <div class="font-display text-xl font-semibold text-text">{{ value }}</div>
    <div v-if="hint" class="mt-1.5 text-xs text-muted leading-snug">{{ hint }}</div>
  </div>
</template>
