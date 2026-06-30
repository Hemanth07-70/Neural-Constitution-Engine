# FastAPI Guide

The Neural Constitution Engine includes a fully-functional, asynchronous FastAPI wrapper.

## Running the Server

Start the API service via Docker or Uvicorn:

```bash
uvicorn backend.api.app:app --host 0.0.0.0 --port 8000
```

## Endpoints

### `POST /evaluate`
Evaluates a single Action.

### `POST /plans/evaluate`
Validates and executes an entire Execution Plan DAG.

### `POST /validate`
Upload a `.yaml` constitution to check for schema or syntax errors.

### `GET /health`
Verify the engine is loaded and responsive.

For comprehensive schema definitions, view the automatically generated Swagger UI at `http://localhost:8000/docs`.
