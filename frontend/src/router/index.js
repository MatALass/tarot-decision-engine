import { createRouter, createWebHistory } from 'vue-router';
import AnalysisView from '@/views/AnalysisView.vue';
import GameStateView from '@/views/GameStateView.vue';
import RecommendationView from '@/views/RecommendationView.vue';
import SetupView from '@/views/SetupView.vue';
const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/', redirect: '/setup' },
        { path: '/setup', name: 'setup', component: SetupView },
        { path: '/game', name: 'game', component: GameStateView },
        { path: '/recommendation', name: 'recommendation', component: RecommendationView },
        { path: '/analysis', name: 'analysis', component: AnalysisView },
    ],
});
export default router;
