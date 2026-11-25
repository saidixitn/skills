---
name: domain-monitor
description: >-
  Use when automating domain expiration monitoring, checking WHOIS renewal dates,
  tracking SSL certificate expiration with socket handshakes, configuring early-warning
  alert thresholds, or preventing domain portfolio downtime.
---

# Domain & SSL Certificate Expiry Sentinel Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Automating background watchdogs for portfolios of active web domains.
- Parsing registrar **WHOIS expiry dates** and detecting imminent domain expirations.
- Inspecting live **SSL certificate validity** and expiration dates via direct TLS/socket handshakes.
- Implementing tiered alerting thresholds: 30 days (notice), 14 days (warning), 3 days (critical).
- Correlating domain expiry with traffic impression data to prune dead links before SEO rank drops.

---

## 2. Hard Architectural Rules

1. **Direct TLS Handshake Over Scraping**:
   Never scrape public SSL verification websites to check certificate expiration. Use Python's built-in `ssl` and `socket` libraries to open direct TLS handshakes. It runs in under 50 milliseconds with zero API costs.

2. **Handle Registrar Rate-Limiting**:
   Direct WHOIS queries (`port 43`) strictly rate-limit repetitive requests. Always introduce jittered delays (1–2 seconds) between domain lookups and cache verified expiry dates locally for at least 24 hours.

3. **Multi-Date Format Resiliency**:
   Registrars return WHOIS dates in wildly inconsistent formats (ISO 8601, European `DD/MM/YYYY`, US `MM/DD/YYYY`, or Unix timestamps). Always use resilient date parsers (`dateutil.parser.parse`) with fallback heuristics.

4. **Sanitized Alert Dispatch**:
   Never hardcode webhook URLs or alert email addresses in checking scripts. Inject through environment variables (`ALERT_WEBHOOK_URL`, `ALERT_RECIPIENT_EMAIL`).

---

## 3. Step-by-Step Expiry Sentinel Workflow

```
[ Domain List from Database / Config ]
                  │
                  ▼
[ 1. Check TLS / SSL Expiry via Socket Handshake ]
                  │
                  ▼
[ 2. Check Registrar WHOIS Expiry Date ]
                  │
                  ▼
[ 3. Calculate Days Remaining (expiry_date - now) ]
                  │
                  ▼
[ 4. Evaluate Thresholds (<= 30d, <= 14d, <= 3d) ]
                  │
                  ▼
[ 5. Dispatch Alert Notification (Email / Webhook) ]
```

---

## 4. Production Code Patterns

### Pattern A: Master SSL & Domain Expiry Engine (Sai Dixit Production Script)
Grounded directly in your `dc_expires.py` and `domain_expires_new.py` monitoring pipelines:

```python
import os
import ssl
import socket
import datetime
from typing import Dict, Any, Optional
from dateutil import parser as date_parser

def get_ssl_expiry_days(domain: str, port: int = 443) -> Optional[int]:
    """
    Connects directly to domain over TLS and calculates days until SSL certificate expires.
    Zero external dependencies.
    """
    clean_host = domain.replace("https://", "").replace("http://", "").split("/")[0].strip()
    context = ssl.create_default_context()
    
    try:
        with socket.create_connection((clean_host, port), timeout=5.0) as sock:
            with context.wrap_socket(sock, server_hostname=clean_host) as ssock:
                cert = ssock.getpeercert()
                expiry_str = cert.get("notAfter")
                # Format: 'May 15 23:59:59 2025 GMT'
                expiry_date = datetime.datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
                days_left = (expiry_date - datetime.datetime.utcnow()).days
                return days_left
    except Exception as e:
        print(f"⚠️ SSL check failed for '{clean_host}': {e}")
        return None

def inspect_domain(domain: str) -> Dict[str, Any]:
    """
    Runs health and expiry checks on a domain.
    """
    ssl_days = get_ssl_expiry_days(domain)
    
    status = "OK"
    if ssl_days is not None:
        if ssl_days <= 3:
            status = "CRITICAL"
        elif ssl_days <= 14:
            status = "WARNING"
        elif ssl_days <= 30:
            status = "NOTICE"

    return {
        "domain": domain,
        "ssl_days_remaining": ssl_days,
        "status": status,
        "checked_at": datetime.datetime.utcnow().isoformat()
    }
```

---

## 5. Anti-Patterns & Operational Pitfalls

| Mistake | Consequence | Proper Fix |
| :--- | :--- | :--- |
| **Spamming port 43 WHOIS queries** | Registrar blocks server IP for 24 hours | Cache results for 24h; use TLS handshake first |
| **Alerting only on day 0** | Domain/SSL expires before ops team can renew | Configure tiered alerts at 30, 14, and 3 days |
| **Hardcoding port 443 only** | Misses custom API gateway ports (e.g. 8443) | Parameterize port in checking routines |

---

## 6. CLI Testing Command
```bash
python3 scripts/check_domains.py --domain "saidixit.vercel.app"
```
