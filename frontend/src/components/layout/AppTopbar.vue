<script setup lang="ts">
defineProps<{
  title: string
  subtitle: string
}>()
</script>

<template>
  <header class="border-b border-border bg-surface/80 backdrop-blur">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
      <div>
        <p class="text-xs uppercase tracking-[0.3em] text-slate-400">Decision platform</p>
        <h1 class="mt-1 text-2xl font-semibold text-white">{{ title }}</h1>
        <p class="mt-1 text-sm text-slate-400">{{ subtitle }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-panel px-4 py-2 text-sm text-slate-300">
        Phase 3 synced state workspace
      </div>
    </div>
  </header>
</template>
