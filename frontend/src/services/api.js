import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeScreenTime = async (userData) => {
  try {
    const response = await api.post('/analyze', userData);
    return response.data;
  } catch (error) {
    console.error('Error analyzing screen time:', error);
    throw error;
  }
};

export const getStatistics = async () => {
  try {
    const response = await api.get('/statistics');
    return response.data;
  } catch (error) {
    console.error('Error fetching statistics:', error);
    throw error;
  }
};

export default api;
