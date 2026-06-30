with open("backend/integrations/langgraph/adapters.py") as f:
    text = f.read()

text = text.replace("    def state_to_decision", "def state_to_decision")
with open("backend/integrations/langgraph/adapters.py", "w") as f:
    f.write(text)
