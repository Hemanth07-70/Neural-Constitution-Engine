with open("backend/integrations/langgraph/middleware.py") as f:
    content = f.read()

content = content.replace(
    "return self._inject_governance_state(node_result, audit.id, verdict)",
    "res = self._inject_governance_state(node_result, audit.id, verdict)\n            print('DEBUG MIDDLEWARE RETURN:', res)\n            return res",
)

with open("backend/integrations/langgraph/middleware.py", "w") as f:
    f.write(content)
