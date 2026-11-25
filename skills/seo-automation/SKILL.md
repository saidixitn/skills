---
name: seo-automation
description: >-
  Use when automating Google Search Console API indexing submissions, pushing
  URL batches to Googlebot for instant crawling, tracking SEMrush rank positions,
  or automating technical SEO monitoring pipelines.
---

# Search Engine Indexing & SEO Automation Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Automating Google Search Console (GSC) **Indexing API** calls to crawl new URLs in under 60 seconds.
- Submitting bulk URL batches for immediate search engine indexing.
- Ingesting and tracking keyword ranking fluctuations via **SEMrush** or Serper APIs.
- Monitoring 404 crawl errors and redirect loops from search console reports.
- Enforcing technical SEO standards (canonical tags, structured JSON-LD schemas, sitemaps).

---

## 2. Hard Architectural Rules

1. **Google Indexing API Quota Boundary**:
   Google limits Indexing API publishing to **200 URL requests per day per project**. Always batch and prioritize high-value canonical pages (job listings, new blog posts) and skip pagination URLs.

2. **Required OAuth2 Scope**:
   Always authenticate with the specific indexing scope:
   `https://www.googleapis.com/auth/indexing`

3. **Verify Domain Property Access**:
   The Service Account's email must be added as an **Owner** in Google Search Console for the targeted domain property, otherwise all API calls fail with `403 Permission Denied`.

4. **Structured JSON-LD Verification**:
   Always validate structured schema markup against schema.org specifications (`JobPosting`, `Article`, `Organization`) before publishing URLs.

---

## 3. Production Code Patterns

### Pattern A: Master Google Indexing API Ingestion Script
Grounded directly in your `vps/search_console` automation tools:

```python
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

def get_indexing_service():
    """Initializes Google Indexing API client."""
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if creds_json:
        creds = service_account.Credentials.from_service_account_info(
            json.loads(creds_json), scopes=SCOPES
        )
    else:
        creds_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
        creds = service_account.Credentials.from_service_account_file(creds_file, scopes=SCOPES)
        
    return build("indexing", "v3", credentials=creds)

def notify_google_url(url: str, action: str = "URL_UPDATED"):
    """
    Submits a URL to Googlebot for immediate crawling.
    action: 'URL_UPDATED' or 'URL_DELETED'
    """
    service = get_indexing_service()
    body = {
        "url": url,
        "type": action
    }
    
    response = service.urlNotifications().publish(body=body).execute()
    print(f" Successfully notified Google. Response timestamp: {response.get('urlNotificationMetadata', {}).get('latestUpdate', {}).get('notifyTime')}")
    return response
```

---

## 4. Verification Command
Test indexing submission for a single URL:
```bash
python3 scripts/index_url.py --url "https://saidixit.vercel.app/"
```
