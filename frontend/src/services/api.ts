import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
});

// Attach token on every request
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 — attempt token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', data.access_token);
          originalRequest.headers['Authorization'] = `Bearer ${data.access_token}`;
          return apiClient(originalRequest);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (badge_number: string, password: string) =>
    apiClient.post('/auth/login', { badge_number, password }),
  me: () => apiClient.get('/auth/me'),
  refresh: (refresh_token: string) =>
    apiClient.post('/auth/refresh', { refresh_token }),
};

// ── Cases ─────────────────────────────────────────────────────────────────────
export const casesApi = {
  list: (params?: Record<string, any>) => apiClient.get('/cases', { params }),
  get: (id: number) => apiClient.get(`/cases/${id}`),
  create: (data: any) => apiClient.post('/cases', data),
  update: (id: number, data: any) => apiClient.patch(`/cases/${id}`, data),
};

// ── Sightings ─────────────────────────────────────────────────────────────────
export const sightingsApi = {
  list: (params?: Record<string, any>) => apiClient.get('/sightings', { params }),
  create: (data: any) => apiClient.post('/sightings', data),
  verify: (id: number, data: any) => apiClient.post(`/sightings/${id}/verify`, data),
};

// ── Alerts ────────────────────────────────────────────────────────────────────
export const alertsApi = {
  list: (params?: Record<string, any>) => apiClient.get('/alerts', { params }),
  create: (data: any) => apiClient.post('/alerts', data),
  acknowledge: (id: number) => apiClient.post(`/alerts/${id}/acknowledge`),
};

// ── Search ────────────────────────────────────────────────────────────────────
export const searchApi = {
  byFace: (formData: FormData) =>
    apiClient.post('/search/face', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  multimodal: (formData: FormData) =>
    apiClient.post('/search/multimodal', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  predictRoute: (caseId: number) =>
    apiClient.post(`/search/route-predict/${caseId}`),
};

// ── Community ─────────────────────────────────────────────────────────────────
export const communityApi = {
  reporters: (params?: Record<string, any>) => apiClient.get('/community/reporters', { params }),
  broadcast: (caseId: number, radiusKm: number) =>
    apiClient.post(`/community/broadcast/${caseId}`, null, { params: { radius_km: radiusKm } }),
};

export default apiClient;
