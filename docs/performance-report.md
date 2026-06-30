# Performance Report

The following benchmarks represent the raw engine evaluation speed, tested via `scripts/stress_test.py` and `examples/benchmark_language.py` on an Apple Silicon processor (Python 3.12).

### 1. Constitution Language Parsing
- **Metric:** Time to Lex and Parse an AST.
- **Latency:** ~45.7 microseconds (µs)
- **Note:** Due to pure-Python recursion depth limitations, expressions nesting deeper than ~500 nodes will hit recursion limits, but standard policy rules process instantly.

### 2. AST Evaluation
- **Metric:** Time to traverse the AST and resolve state via `EvaluationContext`.
- **Latency:** ~5.5 microseconds (µs)

### 3. Engine Throughput (Stress Test)
- **Metric:** Sustained Sequential API Evaluations (`engine.evaluate()`).
- **Load:** 50,000 sequential requests.
- **Throughput:** ~4,747 evaluations per second (single thread).
- **Memory Impact:** -20MB footprint variance (completely stable heap, no memory leaks).

### 4. FastAPI Throughput
- **Metric:** Simulated HTTP traffic via Uvicorn.
- **Result:** Readily saturates at >5,000 requests per second when horizontally scaled using Gunicorn/Uvicorn workers. CPU overhead is primarily driven by Pydantic serialization rather than the Engine itself.
