import axios from 'axios';

// FastAPI backend base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (window.location.hostname.includes('localhost') || window.location.hostname.includes('127.0.0.1')
    ? 'http://localhost:8000/api' 
    : '/api');


const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to automatically attach authorization header
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiry / unauthorized requests
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login if unauthorized
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Only redirect if not already on login/register pages
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  register: async (email, password) => {
    const response = await api.post('/auth/register', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
  getAllUsers: async () => {
    const response = await api.get('/auth/users');
    return response.data;
  },
  deleteUser: async (userId) => {
    const response = await api.delete(`/auth/users/${userId}`);
    return response.data;
  },
};

export const questionService = {
  generate: async (params) => {
    const response = await api.post('/questions/generate', params);
    return response.data;
  },
  getHistory: async () => {
    const response = await api.get('/history');
    return response.data;
  },
  getSetDetails: async (setId) => {
    const response = await api.get(`/history/set/${setId}`);
    return response.data;
  },
  deleteSet: async (setId) => {
    const response = await api.delete(`/history/set/${setId}`);
    return response.data;
  },
  evaluateAnswer: async (questionId, userAnswer) => {
    const response = await api.post('/answers/evaluate', {
      question_id: questionId,
      user_answer: userAnswer,
    });
    return response.data;
  },
  getPdfUrl: (setId) => {
    const token = localStorage.getItem('token');
    return `${API_BASE_URL}/history/set/${setId}/pdf?token=${token}`; // Token can be passed or handled by download file
  },
};

export default api;
