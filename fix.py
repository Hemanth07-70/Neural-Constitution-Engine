with open("backend/tests/integrations/langgraph/test_governed_graph.py") as f:
    text = f.read()

text = text.replace('assert "audit-123" in state["audit_ids"]', 'assert "audit-123" in state.get("audit_ids", [])')
with open("backend/tests/integrations/langgraph/test_governed_graph.py", "w") as f:
    f.write(text)
