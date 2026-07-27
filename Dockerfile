# =========================================================
# Dockerfile — FatPai Resume-JD Semantic Matching Backend
# =========================================================
# Multi-stage build for production deployment.
# Stage 1: Install dependencies
# Stage 2: Copy application code
# =========================================================

FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# ── Stage 1: Install dependencies ───────────────────────
# Copy only dependency files first for better Docker layer caching
COPY pyproject.toml uv.lock* ./

# Install production dependencies only
RUN uv sync --no-dev --no-install-project

# ── Stage 2: Copy application code ──────────────────────
COPY . .

# Install the project itself
RUN uv sync --no-dev

# Expose the application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/')" || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
