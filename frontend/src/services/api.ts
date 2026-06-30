import { apiClient } from '../api/client';
import { DecisionRequest, AuditRecord, ExecutionPlan, PlanValidationResult } from '../api/types';

export const apiService = {
  getHealth: async (): Promise<{ status: string }> => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  getVersion: async (): Promise<{ version: string; api_version: string }> => {
    const response = await apiClient.get('/version');
    return response.data;
  },

  evaluate: async (request: DecisionRequest): Promise<AuditRecord> => {
    const response = await apiClient.post('/evaluate', request);
    return response.data;
  },

  evaluatePlan: async (plan: ExecutionPlan): Promise<PlanValidationResult> => {
    const now = new Date().toISOString();

    // Convert frontend plan to backend ExecutionPlanSchema compliant payload
    const backendPayload = {
      metadata: {
        id: plan.id || 'demo-plan',
        creator: 'urn:agent:ui-builder',
        created_at: now,
        goal_description: 'Execution plan validation from UI',
      },
      nodes: plan.nodes.map((node) => ({
        id: node.id,
        request: {
          api_version: 'nce/v1',
          id: '00000000-0000-0000-0000-' + node.id.padStart(12, '0'),
          actor: { id: 'urn:agent:ui-agent', type: 'agent' },
          action: node.action || { type: 'build', params: {} },
          context: {
            constitution_id: 'default',
            constitution_version: '1.0',
            environment: { name: 'production', timestamp: now },
            correlation_id: '00000000-0000-0000-0000-' + node.id.padStart(12, '0'),
          },
          submitted_at: now,
        },
      })),
      edges: plan.edges.map((edge) => ({
        source_id: edge.source,
        target_id: edge.target,
      })),
    };

    const response = await apiClient.post('/plans/evaluate', backendPayload);
    const data = response.data;

    return {
      plan_id: plan.id,
      is_valid: data.is_valid,
      failed_node_id: data.failed_node_id || (data.errors && data.errors.length > 0 ? data.errors[0] : null),
      node_results: data.node_results || {},
      errors: data.errors || [],
    };
  },

  validateConstitution: async (yamlContent: string): Promise<any> => {
    const response = await apiClient.post('/validate', yamlContent, {
      headers: {
        'Content-Type': 'application/x-yaml',
      },
    });
    return response.data;
  },

  publishConstitution: async (payload: { version: string; yaml_content: string; organization_id: string }): Promise<any> => {
    const response = await apiClient.post('/constitutions/', payload);
    return response.data;
  },
};
