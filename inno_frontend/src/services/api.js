import axios from 'axios';
import { getToken } from '../utils/auth';

// Base axios instance
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true  // Important for CORS with credentials
});

// Request interceptor to add auth token to all requests
api.interceptors.request.use(config => {
  const token = getToken();
  if (token) {
    // Use explicit Bearer prefix for Authorization header
    config.headers.Authorization = `Bearer ${token}`;
    console.log(`Adding token to ${config.method ? config.method.toUpperCase() : 'GET'} request: ${config.url}`);
  } else {
    console.warn(`No token available for request: ${config.url}`);
  }
  return config;
}, error => {
  console.error('Request interceptor error:', error);
  return Promise.reject(error);
});

// Response interceptor with more detailed logging
api.interceptors.response.use(
  response => {
    console.log(`Response from ${response.config.url}: Status ${response.status}`);
    return response;
  },
  error => {
    if (error.response) {
      console.error(`API Error ${error.response.status} for ${error.config.url}:`, 
                    error.response.data);
      
      // Handle authentication errors
      if (error.response.status === 401 || error.response.status === 403) {
        console.error('Authentication error details:', error.response.data);
        
        // If this wasn't an auth endpoint request, token might be invalid
        if (!error.config.url.includes('/simple_auth/')) {
          console.warn('Token might be invalid or expired');
        }
      }
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Error setting up request:', error.message);
    }
    return Promise.reject(error);
  }
);

// Auth services - using ONLY simple_auth endpoints
export const authService = {
  register: async (userData) => {
    // Check if userData is FormData (for profile picture uploads)
    if (userData instanceof FormData) {
      console.log('Sending FormData to /simple_auth/register for file upload');
      return await api.post('/simple_auth/register', userData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
    }
    // For regular JSON data (fallback)
    console.log('Sending JSON data to /simple_auth/register');
    return await api.post('/simple_auth/register', userData);
  },
  login: async (credentials) => {
    return await api.post('/simple_auth/login', credentials);
  },
  testToken: async () => {
    return await api.get('/simple_auth/test-token');
  }
};

// Contact services - using ONLY simple_contacts endpoints
export const contactService = {
  create: async (contactData) => {
    return await api.post('/simple_contacts/', contactData);
  },
  getAll: async (page = 1, perPage = 10, search = '') => {
    const params = new URLSearchParams({
      page,
      per_page: perPage,
      search
    });
    return await api.get(`/simple_contacts/?${params.toString()}`);
  },
  getById: async (id) => {
    return await api.get(`/simple_contacts/${id}`);
  },
  update: async (id, contactData) => {
    return await api.put(`/simple_contacts/${id}`, contactData);
  },
  delete: async (id) => {
    return await api.delete(`/simple_contacts/${id}`);
  }
};