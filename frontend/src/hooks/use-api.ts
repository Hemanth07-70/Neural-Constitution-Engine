import { useQuery, useMutation } from '@tanstack/react-query';
import { apiService } from '@/services/api';
import { DecisionRequest, ExecutionPlan } from '@/api/types';

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const [health, version] = await Promise.all([
        apiService.getHealth(),
        apiService.getVersion()
      ]);
      return { health, version };
    },
    refetchInterval: 10000, // Poll every 10s
    retry: 3,
  });
}

export function useEvaluate() {
  return useMutation({
    mutationFn: (request: DecisionRequest) => apiService.evaluate(request),
  });
}

export function useEvaluatePlan() {
  return useMutation({
    mutationFn: (plan: ExecutionPlan) => apiService.evaluatePlan(plan),
  });
}

export function useValidateConstitution() {
  return useMutation({
    mutationFn: (yamlContent: string) => apiService.validateConstitution(yamlContent),
  });
}

export function usePublishConstitution() {
  return useMutation({
    mutationFn: (payload: { version: string; yaml_content: string; organization_id: string }) =>
      apiService.publishConstitution(payload),
  });
}
