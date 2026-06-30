FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy application source code
COPY pyproject.toml README.md ./
COPY backend/ ./backend/
COPY examples/ ./examples/

# Install the application and dependencies
RUN pip install --no-cache-dir build && pip install --no-cache-dir .

FROM python:3.12-slim

WORKDIR /app

# Copy installed site-packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app code
COPY backend/ ./backend/
COPY examples/ ./examples/

# Set environment variables
ENV NCE_CONSTITUTION_PATH=/app/examples/constitution.yaml
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "backend.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
