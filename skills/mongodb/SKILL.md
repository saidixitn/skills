---
name: mongodb
description: >-
  Use when designing high-performance MongoDB queries, aggregation pipelines,
  compound indexing strategies, preventing the 100MB RAM aggregation spill
  limit with allowDiskUse, streaming large cursors without Node/Python OOM
  crashes, or configuring multi-tenant connection pools.
---

# High-Performance MongoDB Engine Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Architecting MongoDB aggregation pipelines (`$match`, `$sort`, `$group`, `$facet`, `$lookup`).
- Overcoming MongoDB's strict **100MB RAM limit** on aggregation stages.
- Building compound indexes that eliminate in-memory sorting (`Sort operation used more than maximum 33554432 bytes of RAM`).
- Chunked streaming of high-volume collections into HTTP responses or ETL files without buffering in server memory.
- Configuring dual-mode connection pools (local development vs production multi-tenant cloud/VPS clusters).

---

## 2. Hard Architectural Rules

1. **Equality-Sort-Range (ESR) Indexing Rule**:
   Always index compound fields in this exact order:
   - **E**quality matches (`status: "active"`) first.
   - **S**ort fields (`created_at: -1`) second.
   - **R**ange filters (`date: { $gte: start, $lte: end }`) last.
   *Violating ESR forces unindexed in-memory B-tree sorts that crash the server when document counts grow.*

2. **The 100MB RAM Spill Guard**:
   Always pass `{ allowDiskUse: true }` in any aggregation pipeline that contains `$sort` or `$group` across un-indexed collections.

3. **Zero Full-Collection Buffering**:
   Never call `await collection.find().toArray()` or `list(collection.find())` on collections exceeding 1,000 documents. Always consume via asynchronous cursor streaming (`cursor.on('data')` in Node.js or `cursor.batch_size(1000)` in Python).

4. **Strict Field Projection**:
   Always project `{ _id: 0, field_a: 1, field_b: 1 }`. Never transfer heavy metadata or internal arrays over the wire if the consumer only needs 2 columns.

5. **Sanitized Connection URIs**:
   Never hardcode usernames, passwords, or cluster hosts in source files. Inject via `MONGO_URI` environment variable.

---

## 3. Step-by-Step Execution Workflow

```
[ Step 1: Analyze Filter & Sort Fields ]
       │ 
       ▼
[ Step 2: Create ESR Compound Index ]
       │ 
       ▼
[ Step 3: Structure Pipeline ($match early -> $project -> $sort -> $limit) ]
       │ 
       ▼
[ Step 4: Apply allowDiskUse: true ]
       │ 
       ▼
[ Step 5: Pipe Cursor as Stream to HTTP / Disk ]
```

---

## 4. Production Code Patterns

### Pattern A: Dual-Mode Connection Pool Manager (Python)
Safely handles connection pooling, SSL timeouts, and local-versus-cloud cluster switching:

```python
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

_client_instance = None

def get_mongo_db(db_name: str = None):
    """
    Returns a singleton MongoClient with hardened connection pooling.
    Pulls URI from MONGO_URI environment variable.
    """
    global _client_instance
    if _client_instance is None:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        _client_instance = MongoClient(
            mongo_uri,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=45000,
            retryWrites=True
        )
        try:
            # Force verification ping
            _client_instance.admin.command('ping')
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise RuntimeError(f"Failed to connect to MongoDB cluster: {e}")

    target_db = db_name or os.getenv("MONGO_DEFAULT_DB", "production")
    return _client_instance[target_db]
```

---

### Pattern B: Aggregation Pipeline with Disk Spill & Projection (Python)
```python
def run_job_aggregation(db, start_date, end_date, team_filter: str = None):
    """
    Executes a high-performance aggregation across millions of records.
    Applies early $match filtering and allowDiskUse guard.
    """
    match_stage = {
        "created_at": {"$gte": start_date, "$lte": end_date}
    }
    if team_filter:
        match_stage["team"] = team_filter

    pipeline = [
        {"$match": match_stage},
        {"$project": {
            "_id": 0,
            "team": 1,
            "clicks": 1,
            "domain": 1,
            "created_at": 1
        }},
        {"$group": {
            "_id": "$domain",
            "total_clicks": {"$sum": "$clicks"},
            "record_count": {"$sum": 1}
        }},
        {"$sort": {"total_clicks": -1}},
        {"$limit": 100}
    ]

    # allowDiskUse enables temporary B-tree files if memory exceeds 100MB
    return list(db["clicks"].aggregate(pipeline, allowDiskUse=True))
```

---

### Pattern C: Chunked Cursor Streaming API (Node.js / Express)
Directly streams millions of MongoDB documents into the HTTP response without RAM memory leaks:

```javascript
const { MongoClient } = require('mongodb');

let client;
async function getClient() {
  if (!client) {
    client = new MongoClient(process.env.MONGO_URI, {
      maxPoolSize: 50,
      minPoolSize: 10
    });
    await client.connect();
  }
  return client;
}

// Streaming endpoint
async function streamLargeCollection(req, res) {
  const mongoClient = await getClient();
  const collection = mongoClient.db(process.env.MONGO_DB || 'production').collection('postings');

  // Set streaming NDJSON headers
  res.setHeader('Content-Type', 'application/x-ndjson');
  res.setHeader('Transfer-Encoding', 'chunked');

  const cursor = collection
    .find({}, { projection: { _id: 0, title: 1, company: 1, url: 1 } })
    .batchSize(1000);

  for await (const doc of cursor) {
    const shouldContinue = res.write(JSON.stringify(doc) + '\n');
    // Handle backpressure if consumer is slower than database read
    if (!shouldContinue) {
      await new Promise(resolve => res.once('drain', resolve));
    }
  }

  res.end();
}

module.exports = { streamLargeCollection };
```

---

## 5. Anti-Patterns & Common Pitfalls

| Anti-Pattern | Fatal Symptom | Correct Architecture |
| :--- | :--- | :--- |
| **Sorting on unindexed fields** | `Executor error during find: Sort exceeded memory limit of 33554432 bytes` | Create compound index matching the sort key order (e.g. `db.coll.createIndex({ team: 1, created_at: -1 })`) |
| **Unbounded `$lookup`** | Document size blows past the 16MB BSON hard limit | Avoid embedding arrays inside `$lookup`. Use pipeline-based `$lookup` with `$limit` or query via foreign keys. |
| **Buffering cursor with `.toArray()`** | Node.js / Python process killed with OOM | Consume cursor incrementally using `for await` or `batch_size()`. |
| **Missing connection timeouts** | Server hangs indefinitely when cloud cluster reboots | Always specify `serverSelectionTimeoutMS: 5000` so operations fail fast. |

---

## 6. CLI Testing Command
Test connectivity, index efficiency, and explain plans:
```bash
python3 scripts/mongo_client.py --collection "postings" --explain
```
