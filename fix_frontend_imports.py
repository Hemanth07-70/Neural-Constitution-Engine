with open("frontend/src/services/api.ts") as f:
    text = f.read()

text = text.replace("import { apiClient } from './client';", "import { apiClient } from '../api/client';")
text = text.replace(
    "import { DecisionRequest, AuditRecord, ExecutionPlan, PlanValidationResult } from './types';",
    "import { DecisionRequest, AuditRecord, ExecutionPlan, PlanValidationResult } from '../api/types';",
)

with open("frontend/src/services/api.ts", "w") as f:
    f.write(text)

with open("frontend/src/features/providers/providerApi.ts") as f:
    text = f.read()

text = text.replace("import api from '@/services/api';", "import { apiClient } from '@/api/client';")
text = text.replace("api.get", "apiClient.get")

with open("frontend/src/features/providers/providerApi.ts", "w") as f:
    f.write(text)
