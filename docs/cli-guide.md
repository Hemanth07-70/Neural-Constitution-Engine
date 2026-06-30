# CLI Guide

The Neural Constitution Engine offers a rich, interactive CLI tool powered by Click and Rich.

## Commands

### Validation
Validate a constitution file syntax:
```bash
nce validate path/to/constitution.yaml
```

### Evaluation
Evaluate a JSON payload request against a constitution:
```bash
nce evaluate --constitution path/to/constitution.yaml --request request.json
```

### Server
Start the local FastAPI instance:
```bash
nce serve --port 8000 --host 0.0.0.0
```
