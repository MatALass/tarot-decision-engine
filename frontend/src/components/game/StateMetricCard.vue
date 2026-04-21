<script setup lang="ts">
defineProps<{
  label: string
  value: string
  hint?: string
}>()
</script>

<template>
  <div class="rounded-3xl border border-border bg-slate-950/40 p-5">
    <div class="text-xs uppercase tracking-[0.22em] text-slate-500">{{ label }}</div>
    <div class="mt-2 text-2xl font-semibold text-white">{{ value }}</div>
    <div v-if="hint" class="mt-2 text-sm text-slate-400">{{ hint }}</div>
  </div>
</template>
