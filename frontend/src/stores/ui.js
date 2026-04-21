import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
export const useUiStore = defineStore('ui', () => {
    const apiBaseUrl = ref(import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000');
    const appTitle = ref('Tarot Decision Engine');
    const appSubtitle = ref('Expert decision cockpit for 5-player French Tarot');
    const apiRoot = computed(() => `${apiBaseUrl.value}/api/v1`);
    return {
        apiBaseUrl,
        apiRoot,
        appTitle,
        appSubtitle,
    };
});
