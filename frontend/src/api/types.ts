import { z } from 'zod';

export const ActorSchema = z.object({
  id: z.string(),
  type: z.enum(['human', 'machine', 'agent']),
});

export const ActionSchema = z.object({
  type: z.string(),
  params: z.record(z.any()).default({}),
});

export const EnvironmentSchema = z.object({
  name: z.string(),
  timestamp: z.string().optional(),
});

export const DecisionContextSchema = z.object({
  constitution_id: z.string(),
  constitution_version: z.string(),
  correlation_id: z.string(),
  environment: EnvironmentSchema,
});

export const DecisionRequestSchema = z.object({
  id: z.string(),
  actor: ActorSchema,
  action: ActionSchema,
  context: DecisionContextSchema,
  submitted_at: z.string(),
});

export const VerdictActionSchema = z.enum(['allow', 'block', 'modify', 'escalate']);

export const EvaluationResultSchema = z.object({
  action: VerdictActionSchema,
  determining_rule_id: z.string().optional().nullable(),
  risk_level: z.enum(['low', 'medium', 'high', 'critical']),
  modified_action: ActionSchema.optional().nullable(),
  flags: z.array(z.string()).default([]),
});

export const AuditRecordSchema = z.object({
  id: z.string(),
  api_version: z.string(),
  request: DecisionRequestSchema,
  result: EvaluationResultSchema,
  explanation: z.object({
    summary: z.string(),
    details: z.array(z.string()),
  }),
  recorded_at: z.string(),
});

export const PlanNodeSchema = z.object({
  id: z.string(),
  action: ActionSchema,
});

export const EdgeSchema = z.object({
  source: z.string(),
  target: z.string(),
});

export const ExecutionPlanSchema = z.object({
  id: z.string(),
  nodes: z.array(PlanNodeSchema),
  edges: z.array(EdgeSchema),
});

export const PlanValidationResultSchema = z.object({
  plan_id: z.string(),
  is_valid: z.boolean(),
  failed_node_id: z.string().optional().nullable(),
  node_results: z.record(AuditRecordSchema).optional().nullable(),
  errors: z.array(z.string()).optional().nullable(),
});

export type Actor = z.infer<typeof ActorSchema>;
export type Action = z.infer<typeof ActionSchema>;
export type Environment = z.infer<typeof EnvironmentSchema>;
export type DecisionContext = z.infer<typeof DecisionContextSchema>;
export type DecisionRequest = z.infer<typeof DecisionRequestSchema>;
export type VerdictAction = z.infer<typeof VerdictActionSchema>;
export type EvaluationResult = z.infer<typeof EvaluationResultSchema>;
export type AuditRecord = z.infer<typeof AuditRecordSchema>;
export type PlanNode = z.infer<typeof PlanNodeSchema>;
export type Edge = z.infer<typeof EdgeSchema>;
export type ExecutionPlan = z.infer<typeof ExecutionPlanSchema>;
export type PlanValidationResult = z.infer<typeof PlanValidationResultSchema>;
