---
name: docker-microservices
description: >-
  Use when architecting multi-stage Docker container builds, composing
  multi-service stacks (FastAPI, Node, Mongo, Redis), configuring healthchecks,
  and managing non-root security.
---

# Docker Multi-Stage Microservices & Compose Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Writing optimized multi-stage `Dockerfile` definitions for Python, Node.js, or Go.
- Orchestrating full-stack services with `docker-compose.yml` (API, Database, Cache).
- Reducing image sizes by 80% using slim base images (`python:3.11-slim`, `node:20-alpine`).
- Enforcing non-root container security (`USER appuser`).
- Adding automated healthcheck probes (`HEALTHCHECK CMD curl -f http://localhost:PORT/health`).

---

## 2. Hard Architectural Rules

1. **Never Run Containers as Root**:
   Always declare a dedicated non-root user (`RUN useradd -m appuser && USER appuser`) before runtime execution. Running as root allows container-escape vulnerabilities to compromise the host kernel.

2. **Multi-Stage Builds for Minimal Image Size**:
   Compile dependencies, dev packages, and build tools in a temporary builder stage. Copy **only** built artifacts and production dependencies into the final slim runtime image.

3. **Explicit Volume Mounts for Persistence**:
   Never store production database files (MongoDB `/data/db`, PostgreSQL `/var/lib/postgresql/data`) inside container layers. Always attach named Docker volumes.

---

## 3. Production Code Patterns

### Pattern A: Multi-Stage Python FastAPI Dockerfile
```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Minimal Runtime
FROM python:3.11-slim
WORKDIR /app
RUN useradd -m -u 1001 appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:5000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
```
