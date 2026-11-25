#!/usr/bin/env bash
# Headless Newman CLI Test Execution Helper
COLLECTION="${1:-postman_collection.json}"
BASE_URL="${2:-http://127.0.0.1:5000}"
echo "Running Newman tests on $COLLECTION against $BASE_URL..."
npx newman run "$COLLECTION" --global-var "baseUrl=$BASE_URL" --reporters cli || true
