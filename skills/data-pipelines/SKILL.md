---
name: data-pipelines
description: >-
  Use when architecting automated Python ETL pipelines, performing vectorized
  data transformations with Pandas and NumPy, sanitizing messy JSON feeds,
  deduplicating high-volume partner datasets, or converting between MongoDB, CSV, and Excel.
---

# Vectorized Python ETL & Data Pipeline Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Designing automated, unattended data extraction, transformation, and loading (ETL) routines.
- Cleaning messy partner data feeds (corrupted dates, inconsistent domain URLs, null floats).
- Performing high-speed vectorized data manipulations using **Pandas** and **NumPy**.
- Exporting cleaned database records into formatted Excel spreadsheets (`openpyxl`) or CSV archives.
- Preventing memory exhaustion when processing multi-gigabyte data feeds.

---

## 2. Hard Architectural Rules

1. **Vectorization Over Python Loops**:
   Never iterate over DataFrame rows using `for index, row in df.iterrows():`. Row iteration in Python is 50x–100x slower than vectorized column operations (`df["clean_url"] = df["url"].str.replace(...)`). Always use vectorized methods or `np.select()`.

2. **Chunked Processing for Large Files**:
   Never call `pd.read_csv("large_file.csv")` or `pd.read_json()` on files larger than 500MB without chunking. Always pass `chunksize=10000` to process streams in manageable batches without crashing server RAM.

3. **Explicit Data Type Casting**:
   Never leave numeric columns typed as generic Python `object`. Always cast numbers explicitly (`pd.to_numeric()`, `int32`, `float32`) to save memory and avoid formatting bugs in downstream spreadsheets.

4. **Sanitized Null Representation**:
   Always normalize missing values (`np.nan`, `None`, `"N/A"`) into consistent representations before database insertion or spreadsheet exports.

---

## 3. Production Code Patterns

### Pattern A: Master Data Cleaning & Normalization Pipeline (Python)
Grounded directly in your `vps/updates.py` and `pm2-vps/semrush_job_stats.py` scripts:

```python
import pandas as pd
import numpy as np

def clean_and_normalize_records(raw_records: list[dict]) -> pd.DataFrame:
    """
    Transforms raw scraped records into normalized analytics DataFrame.
    Applies high-speed vectorized cleaning routines.
    """
    if not raw_records:
        return pd.DataFrame()

    df = pd.DataFrame(raw_records)

    # 1. Vectorized URL Cleaning
    if "domain" in df.columns:
        df["domain"] = (
            df["domain"]
            .astype(str)
            .str.replace("https://", "", regex=False)
            .str.replace("http://", "", regex=False)
            .str.split("/")
            .str[0]
            .str.strip()
            .str.lower()
        )

    # 2. Vectorized Numeric Casting & NaN Sanitization
    numeric_cols = ["clicks", "impressions", "views"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 3. Vectorized Date Normalization
    if "created_at" in df.columns:
        df["date"] = pd.to_datetime(df["created_at"], errors="coerce").dt.strftime("%Y-%m-%d")

    # 4. Deduplication
    df = df.drop_duplicates(subset=["domain", "date"] if "date" in df.columns else ["domain"])

    return df
```

---

## 4. Verification Command
Test data cleaning and normalization on sample records:
```bash
python3 scripts/etl_cleaner.py --test-run
```
