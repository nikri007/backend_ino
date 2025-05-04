import axios from 'axios';

// Base axios instance
const api = axios.create({
  baseURL: 'http://localhost:5000/api'
});

// Request interceptor to add auth token to all requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// Auth services
export const authService = {
  register: async (userData) => {
    // For multipart/form-data (when uploading profile picture)
    if (userData instanceof FormData) {
      return await api.post('/auth/register', userData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    }
    // For regular JSON data
    return await api.post('/auth/register', userData);
  },
  login: async (credentials) => {
    return await api.post('/auth/login', credentials);
  }
};

// Contact services
export const contactService = {
  create: async (contactData) => {
    return await api.post('/contacts/', contactData);
  },
  getAll: async (page = 1, perPage = 10, search = '') => {
    return await api.get(`/contacts/?page=${page}&per_page=${perPage}&search=${search}`);
  },
  getById: async (id) => {
    return await api.get(`/contacts/${id}`);
  },
  update: async (id, contactData) => {
    return await api.put(`/contacts/${id}`, contactData);
  },
  delete: async (id) => {
    return await api.delete(`/contacts/${id}`);
  }
};