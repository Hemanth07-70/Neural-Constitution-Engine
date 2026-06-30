with open("/Users/hemanthchowdary/.gemini/antigravity-ide/brain/4cd45cb1-b0d2-40f0-a083-bb9aaf4269ae/task.md") as f:
    text = f.read()

# I'll just write the correct markdown
correct_text = """# Milestone 18: LangGraph Integration

## 1. Adapter Implementation
- [x] Implement `models.py` (SQLAlchemy models for run persistence).
- [x] Implement `config.py` and `exceptions.py`.
- [x] Implement `state.py` and `callbacks.py`.
- [x] Implement `adapters.py` (translation between LangGraph and NCE schemas).
- [x] Implement `middleware.py` (Evaluation service integration and verdict handling).
- [x] Implement `governed_graph.py` (wrapper around `StateGraph`).

## 2. Fixes & Testing
- [x] Fix LangGraph integration test failures
- [x] Ensure GovernanceMiddleware correctly injects state dict with audit_ids and rewrite_history
- [x] Correctly wrap LangGraph NodeSpec.runnable with RunnableLambda
- [x] Format DecisionRequestSchema correctly to pass Pydantic validation
- [x] Verify ALLOW, BLOCK, and REWRITE test cases pass

## 3. Backend API
- [x] Implement `backend/api/routes/langgraph_routes.py`.
- [x] Register router in `backend/api/app.py`.

## 4. Tests
- [x] Author `backend/tests/integrations/langgraph/test_governed_graph.py` integration tests.
- [x] Refactor implementation until tests pass.
"""

with open(
    "/Users/hemanthchowdary/.gemini/antigravity-ide/brain/4cd45cb1-b0d2-40f0-a083-bb9aaf4269ae/task.md", "w"
) as f:
    f.write(correct_text)
