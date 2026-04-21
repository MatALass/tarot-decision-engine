<script setup lang="ts">
import AppTopbar from '@/components/layout/AppTopbar.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
</script>

<template>
  <div class="min-h-screen bg-surface font-body text-text" style="background: radial-gradient(ellipse at 25% 0%, #13172a 0%, #08090d 65%);">
    <AppTopbar />
    <div class="mx-auto flex max-w-[1440px] gap-5 px-5 py-5">
      <AppSidebar />
      <main class="min-h-[calc(100vh-5rem)] flex-1 overflow-hidden rounded-2xl panel-base p-7 animate-fade-in">
        <slot />
      </main>
    </div>
  </div>
</template>
