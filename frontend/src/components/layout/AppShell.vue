<script setup lang="ts">
import { storeToRefs } from 'pinia'

import AppTopbar from '@/components/layout/AppTopbar.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()
const { appTitle, appSubtitle } = storeToRefs(uiStore)
</script>

<template>
  <div class="min-h-screen bg-surface text-slate-100">
    <AppTopbar :title="appTitle" :subtitle="appSubtitle" />
    <div class="mx-auto flex max-w-7xl gap-6 px-6 py-6">
      <AppSidebar />
      <main class="min-h-[calc(100vh-8rem)] flex-1 rounded-3xl border border-border bg-panel/80 p-6 shadow-soft backdrop-blur">
        <slot />
      </main>
    </div>
  </div>
</template>
