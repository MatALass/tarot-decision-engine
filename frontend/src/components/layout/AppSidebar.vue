<script setup lang="ts">
const links = [
  { name: 'Setup', to: '/setup', description: 'Configure game context' },
  { name: 'Current state', to: '/game', description: 'Track tricks and observable state' },
  { name: 'Recommendation', to: '/recommendation', description: 'Compare legal actions' },
  { name: 'Analysis', to: '/analysis', description: 'Research and probability views' },
]
</script>

<template>
  <aside class="hidden w-80 shrink-0 xl:block">
    <div class="rounded-3xl border border-border bg-panel/80 p-4 shadow-soft">
      <p class="px-3 pb-3 text-xs uppercase tracking-[0.3em] text-slate-500">Navigation</p>
      <nav class="space-y-2">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="block rounded-2xl border border-transparent px-4 py-3 transition hover:border-border hover:bg-slate-900/40"
          active-class="border-accent/30 bg-accent/10"
        >
          <div class="text-sm font-medium text-white">{{ link.name }}</div>
          <div class="mt-1 text-sm text-slate-400">{{ link.description }}</div>
        </RouterLink>
      </nav>
    </div>
  </aside>
</template>
