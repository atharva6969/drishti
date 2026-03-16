import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Missing Persons
export const missingPersonsAPI = {
  list: (params = {}) => api.get('/api/v1/missing-persons/', { params }),
  get: (id) => api.get(`/api/v1/missing-persons/${id}`),
  create: (data) => api.post('/api/v1/missing-persons/', data),
  updateStatus: (id, data) => api.patch(`/api/v1/missing-persons/${id}/status`, data),
  uploadPhoto: (id, formData) =>
    api.post(`/api/v1/missing-persons/${id}/photo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

// Alerts
export const alertsAPI = {
  list: (params = {}) => api.get('/api/v1/alerts/', { params }),
  create: (data) => api.post('/api/v1/alerts/', data),
  verify: (id, data) => api.post(`/api/v1/alerts/${id}/verify`, data),
};

// Search
export const searchAPI = {
  byFace: (officerId, imageFile) => {
    const formData = new FormData();
    formData.append('file', imageFile);
    return api.post('/api/v1/search/face', formData, {
      params: { officer_id: officerId },
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  multimodal: (officerId, imageFile) => {
    const formData = new FormData();
    formData.append('file', imageFile);
    return api.post('/api/v1/search/multimodal', formData, {
      params: { officer_id: officerId },
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getRoutes: (caseId) => api.get(`/api/v1/search/route/${caseId}`),
};

// Reports
export const reportsAPI = {
  submitSighting: (data) => api.post('/api/v1/reports/sighting', data),
  getAudit: (params = {}) => api.get('/api/v1/reports/audit', { params }),
};

// Health check
export const healthCheck = () => api.get('/health');

export default api;
