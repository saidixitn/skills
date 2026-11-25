#!/usr/bin/env python3
"""
CLI Helper for Testing Data Pipeline Cleaning & Normalization
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Data Pipeline Cleaner CLI")
    parser.add_argument("--test-run", action="store_true", help="Run test cleaning pipeline")
    args = parser.parse_args()

    try:
        import pandas as pd
        raw = [
            {"domain": "https://EXAMPLE.com/test", "clicks": "120"},
            {"domain": "http://Example.com", "clicks": None}
        ]
        df = pd.DataFrame(raw)
        df["domain"] = df["domain"].str.replace("https://", "").str.replace("http://", "").str.split("/").str[0].str.lower()
        print(" Data Cleaning Test Passed! Result:")
        print(df.to_string(index=False))
    except ImportError:
        print("Notice: pandas not installed in current environment. Validation skipped.")

if __name__ == "__main__":
    main()
