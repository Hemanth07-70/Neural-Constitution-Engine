import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';

export interface HealthResponse {
  status: string;
  providers: Record<string, boolean>;
}

export const useProvidersList = () => {
  return useQuery<string[]>({
    queryKey: ['providers'],
    queryFn: async () => {
      const { data } = await apiClient.get('/providers');
      return data;
    },
  });
};

export const useProvidersHealth = () => {
  return useQuery<HealthResponse>({
    queryKey: ['providers', 'health'],
    queryFn: async () => {
      const { data } = await apiClient.get('/providers/health');
      return data;
    },
    refetchInterval: 30000, // Auto refresh every 30s
  });
};

export const useProviderModels = () => {
  return useQuery<Record<string, string[]>>({
    queryKey: ['providers', 'models'],
    queryFn: async () => {
      const { data } = await apiClient.get('/providers/models');
      return data;
    },
  });
};
