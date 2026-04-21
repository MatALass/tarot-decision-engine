import axios from 'axios';
const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
    timeout: 30000,
});
export async function fetchHealth() {
    const { data } = await apiClient.get('/api/v1/health');
    return data;
}
export async function recommendMove(payload) {
    const { data } = await apiClient.post('/api/v1/moves/recommend', payload);
    return data;
}
