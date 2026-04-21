<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const pageLabel = computed(() => {
  const map: Record<string, string> = {
    '/setup': 'Configuration',
    '/game': 'État de partie',
    '/recommendation': 'Recommandation',
    '/analysis': 'Analyse',
  }
  return map[route.path] ?? ''
})
</script>

<template>
  <header class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid rgba(201,150,58,0.12);">
    <div class="flex items-center gap-3">
      <!-- Tarot card icon -->
      <div class="flex h-9 w-9 items-center justify-center rounded-lg" style="background: linear-gradient(135deg, #c9963a 0%, #e8b55a 100%); box-shadow: 0 0 16px rgba(201,150,58,0.3);">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <rect x="4" y="2" width="16" height="20" rx="2" fill="#08090d" opacity="0.9"/>
          <path d="M12 6L13.5 10H17.5L14.5 12.5L15.5 16.5L12 14L8.5 16.5L9.5 12.5L6.5 10H10.5L12 6Z" fill="#c9963a"/>
        </svg>
      </div>
      <div>
        <div class="font-display text-sm font-semibold tracking-wider text-gold">TAROT ENGINE</div>
        <div class="text-xs text-subtle tracking-widest uppercase">Decision Oracle</div>
      </div>
    </div>

    <div v-if="pageLabel" class="hidden items-center gap-2 rounded-full border border-border px-4 py-1.5 sm:flex" style="background: rgba(30,37,56,0.6);">
      <div class="h-1.5 w-1.5 rounded-full bg-gold animate-pulse"></div>
      <span class="text-xs font-medium tracking-widest text-subtle uppercase">{{ pageLabel }}</span>
    </div>

    <div class="flex items-center gap-3">
      <div class="h-2 w-2 rounded-full bg-emerald" style="box-shadow: 0 0 8px rgba(42,171,111,0.6);"></div>
      <span class="text-xs text-subtle">Engine connecté</span>
    </div>
  </header>
</template>
