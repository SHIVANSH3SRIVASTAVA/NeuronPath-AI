import axios from 'axios';

// In development with Vite proxy, '/api' routes directly through the Vite dev server to FastAPI backend on 127.0.0.1:8000.
// If accessing directly or in standalone mode, it falls back to 127.0.0.1:8000/api.
const getBaseUrl = () => {
  if (typeof window !== 'undefined') {
    // If running on Vite dev server (port 5173 or 3000), use proxy path '/api'
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
  timeout: 30000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
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
