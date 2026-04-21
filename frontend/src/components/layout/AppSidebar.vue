<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const links = [
  {
    name: 'Configuration',
    to: '/setup',
    icon: '⬡',
    description: 'Saisie de l\'état initial',
  },
  {
    name: 'État de partie',
    to: '/game',
    icon: '◈',
    description: 'Plis et joueurs actifs',
  },
  {
    name: 'Recommandation',
    to: '/recommendation',
    icon: '◆',
    description: 'Actions classées par EV',
  },
  {
    name: 'Analyse',
    to: '/analysis',
    icon: '◉',
    description: 'Métriques avancées',
  },
]
</script>

<template>
  <aside class="hidden w-72 shrink-0 xl:block">
    <div class="rounded-2xl panel-base p-3">
      <div class="px-3 py-2 mb-1">
        <span class="text-xs tracking-[0.25em] text-subtle uppercase font-medium">Navigation</span>
      </div>
      <nav class="space-y-1">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="group flex items-center gap-3 rounded-xl px-3 py-3 transition-all duration-200"
          :class="route.path === link.to
            ? 'bg-gold/10 border border-gold/25 shadow-glow-gold'
            : 'border border-transparent hover:bg-card hover:border-border'"
        >
          <div
            class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm transition-all duration-200"
            :class="route.path === link.to
              ? 'bg-gold/20 text-gold'
              : 'bg-card text-subtle group-hover:text-gold group-hover:bg-gold/10'"
          >
            {{ link.icon }}
          </div>
          <div class="min-w-0">
            <div
              class="text-sm font-medium transition-colors"
              :class="route.path === link.to ? 'text-gold' : 'text-text group-hover:text-gold-light'"
            >
              {{ link.name }}
            </div>
            <div class="text-xs text-subtle mt-0.5 truncate">{{ link.description }}</div>
          </div>
          <div
            v-if="route.path === link.to"
            class="ml-auto h-1.5 w-1.5 shrink-0 rounded-full bg-gold"
            style="box-shadow: 0 0 6px rgba(201,150,58,0.6);"
          ></div>
        </RouterLink>
      </nav>

      <!-- Footer info -->
      <div class="mt-4 rounded-xl border border-border bg-deep p-3">
        <div class="text-xs text-subtle mb-1 tracking-wider uppercase">Monte Carlo</div>
        <div class="text-xs text-text font-mono">Policy: expected_score</div>
      </div>
    </div>
  </aside>
</template>
