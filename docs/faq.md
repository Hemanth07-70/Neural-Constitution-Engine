# Frequently Asked Questions

### Can I evaluate rules using an LLM?
No. Neural Constitution Engine is intentionally designed to be **deterministic**. The goal is to constrain LLMs and autonomous agents using deterministic rule policies. If the policy itself was non-deterministic, we could not guarantee safety.

### What is the performance penalty for running NCE?
Very low. NCE parsing and evaluation executes in microseconds (~5-50µs per rule). The FastAPI server can handle thousands of requests per second.

### Do I have to write constitutions in YAML?
YAML is the default recommended format, but JSON is also fully supported.

### Is there support for variables in the Constitution Language?
No. The Constitution Language is designed specifically without variables, loops, or complex state mutations to guarantee safe evaluations and eliminate infinite loops.
