# ── Stage 1: Build the Vue.js frontend ───────────
FROM node:22-alpine AS frontend-builder

WORKDIR /build
COPY src/frontend/package.json src/frontend/package-lock.json* ./
RUN npm ci
COPY src/frontend/ ./
RUN npm run build

# ── Stage 2: Production image ────────────────────
FROM python:3.12-slim AS runtime

LABEL maintainer="Nicolas Hennion <nicolas@nicolargo.com>"
LABEL description="Klances — Kubernetes read-only dashboard"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy source and project metadata
COPY pyproject.toml ./
COPY src/ ./src/

# Copy the pre-built frontend into the expected location
COPY --from=frontend-builder /build/dist/ ./src/frontend/dist/

# Install the application
RUN pip install --no-cache-dir .

EXPOSE 8000

ENTRYPOINT ["klances"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
