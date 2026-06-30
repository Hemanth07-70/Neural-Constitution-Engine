import axios from 'axios';
import { useAppStore } from '@/store/useAppStore';

// Ensure this matches the FastAPI default host and port
export const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10s timeout
});

apiClient.interceptors.request.use((config) => {
  const token = useAppStore.getState().accessToken;
  const orgId = useAppStore.getState().activeOrganization?.id;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Ensure we append organization_id as query param for GET requests that need it
  if (orgId && config.method?.toLowerCase() === 'get') {
      config.params = { ...config.params, organization_id: orgId };
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    // We could handle refresh token logic here if 401 is returned
    // For now, if we get a 401, we just clear auth state
    if (error.response?.status === 401) {
      useAppStore.getState().logout();
    }
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
