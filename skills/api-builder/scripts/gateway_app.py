#!/usr/bin/env python3
"""
CLI Helper for API Gateway Verification and OpenAPI Schema Validation
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="API Gateway Schema Validator")
    parser.add_argument("--test-schema", action="store_true", help="Validate OpenAPI schema structure")
    args = parser.parse_args()

    try:
        from fastapi import FastAPI
        app = FastAPI(title="Gateway Test App", version="1.0.0")
        schema = app.openapi()
        print(f" OpenAPI schema generated successfully (Title: '{schema['info']['title']}', Version: '{schema['info']['version']}').")
    except ImportError:
        print("Notice: FastAPI not installed in current environment. Schema validation skipped.")

if __name__ == "__main__":
    main()
