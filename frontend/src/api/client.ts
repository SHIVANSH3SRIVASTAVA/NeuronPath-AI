import axios from 'axios';

// Resolves API base URL:
// 1. If VITE_API_URL environment variable is provided (production), use it.
// 2. In local development with Vite dev server (port 5173/3000), route through Vite proxy '/api'.
// 3. Otherwise fall back to local backend on port 8000.
const getBaseUrl = () => {
  let url = import.meta.env.VITE_API_URL;
  if (url) {
    url = url.replace(/\/+$/, '');
    if (!url.endsWith('/api')) {
      url = `${url}/api`;
    }
    return url;
  }
  if (typeof window !== 'undefined') {
    if (window.location.port === '5173' || window.location.port === '3000') {
      return '/api';
    }
    return `http://${window.location.hostname}:8000/api`;
  }
  return 'http://127.0.0.1:8000/api';
};

export const apiClient = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 90000,
});

apiClient.interceptors.request.use((config) => {
  try {
    let token = localStorage.getItem('neuronpath-token');
    if (!token) {
      const stored = localStorage.getItem('neuronpath-storage');
      if (stored) {
        const parsed = JSON.parse(stored);
        token = parsed?.state?.token;
      }
    }
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (e) {}
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      const currentPath = window.location.pathname;
      if (currentPath !== '/login' && currentPath !== '/register' && currentPath !== '/') {
        try {
          localStorage.removeItem('neuronpath-token');
        } catch (e) {}
      }
    }
    console.error('API Request Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    return Promise.reject(error);
  }
);
