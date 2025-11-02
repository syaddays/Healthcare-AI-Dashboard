import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Patient API functions
export const patientAPI = {
  // Create a new patient
  createPatient: async (patientData) => {
    const response = await api.post('/patients', patientData);
    return response.data;
  },

  // Get all patients with pagination
  getPatients: async (page = 1, perPage = 10) => {
    const response = await api.get('/patients', {
      params: { page, per_page: perPage }
    });
    return response.data;
  },

  // Get patient details with readings and predictions
  getPatientDetails: async (patientId) => {
    const response = await api.get(`/patients/${patientId}`);
    return response.data;
  },

  // Log vital signs for a patient
  logMetrics: async (patientId, metrics) => {
    const response = await api.post(`/patients/${patientId}/metrics`, metrics);
    return response.data;
  },

  // Get AI prediction for a patient
  getPrediction: async (patientId) => {
    const response = await api.post('/predictions', { patient_id: patientId });
    return response.data;
  },
};

// Health check function
export const healthCheck = async () => {
  try {
    const response = await axios.get(process.env.REACT_APP_API_URL?.replace('/api/v1', '') || 'http://localhost:8000');
    return response.data;
  } catch (error) {
    throw new Error('Backend server is not responding');
  }
};

export default api;