#!/usr/bin/env python3
"""
CLI Helper for MongoDB Performance & Index Explain Analysis
Usage:
    python3 mongo_client.py --collection "clicks" --explain
"""

import os
import sys
import argparse
import json
from pymongo import MongoClient

def get_db():
    uri = os.getenv("MONGO_URI")
    if not uri:
        print("Error: MONGO_URI environment variable not set.")
        sys.exit(1)
    client = MongoClient(uri, serverSelectionTimeoutMS=4000)
    db_name = os.getenv("MONGO_DEFAULT_DB", "production")
    return client[db_name]

def main():
    parser = argparse.ArgumentParser(description="MongoDB Engine CLI Helper")
    parser.add_argument("--collection", required=True, help="Collection name")
    parser.add_argument("--explain", action="store_true", help="Print explain plan of sample query")
    parser.add_argument("--indexes", action="store_true", help="List all active indexes")
    args = parser.parse_args()

    db = get_db()
    col = db[args.collection]

    if args.indexes or not args.explain:
        print(f"=== Active Indexes on '{args.collection}' ===")
        for idx in col.list_indexes():
            print(f"- {idx['name']}: {idx['key']}")

    if args.explain:
        print(f"\n=== Explain Plan for find() on '{args.collection}' ===")
        plan = col.find().limit(10).explain()
        stage = plan.get("queryPlanner", {}).get("winningPlan", {}).get("stage", "UNKNOWN")
        print(f"Winning Plan Stage: {stage} (Optimal = IXSCAN, Suboptimal = COLLSCAN)")

if __name__ == "__main__":
    main()
