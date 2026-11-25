---
name: api-testing
description: >-
  Use when architecting Postman collections, parameterizing environment variables,
  automating API test suites with the Newman CLI, writing pre-request authentication
  scripts, or enforcing response contract assertions in CI/CD pipelines.
---

# Postman Collection Architecture & Newman CLI Testing Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Architecting structured, multi-endpoint **Postman collections** (`.json`).
- Automating API regression test runs headlessly in CI/CD using the **Newman CLI**.
- Parameterizing environments (`baseUrl`, `apiKey`, `token`) across staging and production.
- Writing pre-request JavaScript scripts for dynamic signature generation or token injection.
- Validating status codes, response times, and JSON schema boundaries on every endpoint.

---

## 2. Hard Architectural Rules

1. **Parameterize Base URLs**:
   Never hardcode hostnames or IP addresses inside individual request URLs. Always use `{{baseUrl}}/api/v1/resource` to allow instantaneous environment switching between local, staging, and production.

2. **Every Endpoint Requires Status & Schema Assertions**:
   Never create an endpoint without at least two automated test scripts:
   - Status code check: `pm.response.to.have.status(200);`
   - JSON structure verification: `pm.expect(pm.response.json()).to.have.property('data');`

3. **Pre-Flight Environment Scrubbing**:
   Never commit Postman environment files containing live API keys or production passwords to git. Use empty `.env.example` templates or inject via CLI arguments (`--env-var "apiKey=$SECRET_KEY"`).

---

## 3. Production Code Patterns

### Pattern A: Master Newman CLI Automation Runner (`run_newman.sh`)
Grounded directly in your `vps/Dixit-APIs.postman_collection.json` test harness:

```bash
#!/usr/bin/env bash
# Headless Newman Test Runner for Production Gateways
set -e

COLLECTION="Dixit-APIs.postman_collection.json"
BASE_URL="${TARGET_BASE_URL:-http://127.0.0.1:5000}"

echo "=== Running Newman Test Suite against $BASE_URL ==="

# Execute headless collection run with formatted CLI output
npx newman run "$COLLECTION" \
  --global-var "baseUrl=$BASE_URL" \
  --reporters cli \
  --bail \
  --timeout-request 5000

echo " All API Gateway contract assertions passed!"
```

---

## 4. Verification Command
Run headless collection test:
```bash
bash scripts/run_newman.sh
```
