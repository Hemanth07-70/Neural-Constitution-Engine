# Benchmarks

The Neural Constitution Engine is built for maximum throughput with minimal overhead. It evaluates deep execution graphs rapidly, making it suitable for low-latency autonomous loops.

## Methodology
Tests run on a standard Apple M-Series machine, using Python 3.12. All benchmarks process a standard DevOps security rule with multiple logic branches:

```text
action.type == 'deploy' and action.params.environment == 'production' and (action.params.critical_vulns <= 0 or exists action.params.cab_approved)
```

## DSL Parser Latency

The Lexer and Recursive-Descent Parser efficiently generate abstract syntax trees from text.
- **Parsing Overhead:** ~45.73 microseconds (µs) per iteration.

## Engine Evaluation Latency

Tree-walking AST evaluation against the runtime context:
- **Evaluation Speed:** ~5.53 microseconds (µs) per cycle.

## API Throughput

The FastAPI engine (`uvicorn`) wrapping the underlying SDK manages request validation and routing asynchronously. In load testing scenarios, the API comfortably handles **>5,000 requests per second** natively, with memory footprint maxing at ~45MB for the standard process.

For high scale deployments, horizontal scaling behind a standard load balancer is recommended.
