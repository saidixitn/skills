---
name: bigquery
description: >-
  Use when architecting Google BigQuery streaming data ingestion pipelines,
  designing partitioned and clustered table schemas, optimizing SQL query costs,
  or transforming high-volume operational event logs into analytics warehouses.
---

# Google BigQuery Analytics & Data Lakehouse Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Streaming real-time records from Python backends into **Google BigQuery**.
- Designing partitioned (`PARTITION BY DATE(timestamp)`) and clustered table schemas.
- Minimizing BigQuery query scan costs using column pruning and partition filters.
- Ingesting MongoDB dumps and newline-delimited JSON (NDJSON) files into cloud datasets.
- Executing cost-efficient SQL batch transformations and window aggregations.

---

## 2. Hard Architectural Rules

1. **Always Partition by Ingestion Date**:
   Never create flat, unpartitioned BigQuery tables for event logs or time-series data. Unpartitioned tables force full-table scans for every query, multiplying cloud query costs. Always declare:
   `PARTITION BY DATE(_PARTITIONDATE)` or `PARTITION BY DATE(created_at)`.

2. **Select Only Needed Columns (No `SELECT *`)**:
   BigQuery charges per byte scanned across columns. Never run `SELECT *` on production datasets. Always project explicit column names (`SELECT domain, clicks, timestamp`).

3. **Use Streaming Inserts (`insert_rows_json`) for Realtime**:
   For low-latency event ingestion (under 5 seconds), use BigQuery's Streaming API (`insert_rows_json`). For batch uploads exceeding 100,000 rows, use load jobs (`load_table_from_file`) which are free of streaming ingestion fees.

4. **Sanitized Service Account Credentials**:
   Authenticate using `GOOGLE_APPLICATION_CREDENTIALS` or `GOOGLE_SERVICE_ACCOUNT_JSON`. Never hardcode GCP project IDs or private keys in source code.

---

## 3. Production Code Patterns

### Pattern A: Streaming Ingestion Client with Error Buffer (Python)
Grounded directly in your `vps/bigquery` pipelines:

```python
import os
import json
from google.cloud import bigquery
from google.oauth2 import service_account

def get_bigquery_client() -> bigquery.Client:
    """Initializes BigQuery client from environment credentials."""
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    project_id = os.getenv("GCP_PROJECT_ID")
    
    if creds_json:
        creds = service_account.Credentials.from_service_account_info(json.loads(creds_json))
        return bigquery.Client(project=project_id, credentials=creds)
    
    return bigquery.Client(project=project_id)

def stream_events_to_bigquery(
    client: bigquery.Client,
    dataset_id: str,
    table_id: str,
    rows: list[dict]
):
    """
    Streams a batch of JSON records into BigQuery table.
    Captures and reports schema mismatch or insertion errors.
    """
    table_ref = f"{client.project}.{dataset_id}.{table_id}"
    
    # insert_rows_json provides instant streaming with zero load job delay
    errors = client.insert_rows_json(table_ref, rows)
    
    if errors:
        print(f"⚠️ BigQuery insertion errors encountered ({len(errors)} rows failed): {errors[:3]}")
    else:
        print(f" Successfully streamed {len(rows)} records into BigQuery table '{table_id}'.")
```

---

## 4. Anti-Patterns & Operational Pitfalls

| Mistake | Consequence | Proper Fix |
| :--- | :--- | :--- |
| **`SELECT *` on analytics tables** | Massive monthly cloud bill | Select explicit columns only |
| **Unpartitioned tables** | Scans multi-terabyte dataset on simple date queries | Add `PARTITION BY DATE(created_at)` |
| **Streaming tiny 1-row batches** | Hits BigQuery streaming quota limits | Buffer rows and flush in batches of 500–1,000 |

---

## 5. Verification Command
Test BigQuery dataset accessibility:
```bash
python3 scripts/bigquery_loader.py --test-connection
```
