import axios from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      Cookies.remove('access_token');
      Cookies.remove('user_id');
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (email: string, password: string) =>
    api.post('/auth/register', { email, password }),
  
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
};

// Upload API
export const uploadAPI = {
  uploadFile: (formData: FormData) =>
    api.post('/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  deleteFile: (fileId: string) =>
    api.delete(`/upload/${fileId}`),
};

// Sessions API
export const sessionsAPI = {
  list: () => api.get('/sessions/'),
  
  create: (data: { file_id?: string; title?: string }) =>
    api.post('/sessions/', data),
  
  get: (sessionId: string) => api.get(`/sessions/${sessionId}`),
  
  delete: (sessionId: string) => api.delete(`/sessions/${sessionId}`),
  
  updateTitle: (sessionId: string, title: string) =>
    api.patch(`/sessions/${sessionId}/title`, { title }),
};

// Ask API
export const askAPI = {
  ask: (sessionId: string, message: string) =>
    api.post('/ask/', { session_id: sessionId, message }),
  
  askStream: (sessionId: string, message: string) =>
    api.post('/ask/stream', { session_id: sessionId, message }, {
      responseType: 'stream',
    }),
};

export default api;