---
name: web-scraper
description: >-
  Use when architecting resilient web scrapers with Puppeteer or Requests,
  configuring user-agent rotation, managing rotating proxy pools, mitigating
  anti-bot rate limits, or extracting structured data from dynamic DOM trees.
---

# Resilient Web Scraping & Headless Automation Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Extracting structured records from modern JavaScript-rendered websites.
- Configuring **Puppeteer** or **Playwright** headless browser automation sessions.
- Implementing rotating proxy pools (`http://user:pass@proxy_host:port`) with round-robin failover.
- Masking headless browser fingerprints (disabling `navigator.webdriver`, randomized viewports).
- Applying exponential backoff retry algorithms to handle HTTP 429 and Cloudflare Turnstile blocks.

---

## 2. Hard Architectural Rules

1. **Randomized User-Agent & Viewport Rotation**:
   Never use default Puppeteer or Python Requests headers. Browsers without standard `Accept-Language`, `Sec-Ch-Ua`, and realistic desktop viewports (`1920x1080`, `1440x900`) get flagged and blocked immediately.

2. **Always Close Browser Contexts**:
   Never leave dangling headless Chrome instances running. Every page extraction must be wrapped in `try...finally` with `await browser.close()` to prevent memory leaks on VPS servers.

3. **Polite Request Throttling**:
   Never fire parallel requests without delay against target domains. Implement randomized inter-request sleep intervals (0.8s–2.5s) to mimic human browsing behavior and prevent IP bans.

4. **Resource Blocking for 5x Speed**:
   When scraping text/data with Puppeteer, always block heavy third-party media (images, fonts, stylesheets, ads) via `page.setRequestInterception(true)`. This slashes page load times by 80% and saves proxy bandwidth.

---

## 3. Production Code Patterns

### Pattern A: High-Speed Puppeteer Scraper with Request Interception (Node.js)
Grounded directly in your `Poulo/scrape.js` engine:

```javascript
const puppeteer = require('puppeteer-core');

async function scrapeDynamicPage(targetUrl, proxyUrl = null) {
  const args = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-blink-features=AutomationControlled',
    '--window-size=1920,1080'
  ];

  if (proxyUrl) {
    args.push(`--proxy-server=${proxyUrl}`);
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args
  });

  const page = await browser.newPage();

  try {
    // 1. Optimize Speed: Block images, fonts, and stylesheets
    await page.setRequestInterception(true);
    page.on('request', (req) => {
      const type = req.resourceType();
      if (['image', 'font', 'media', 'stylesheet'].includes(type)) {
        req.abort();
      } else {
        req.continue();
      }
    });

    // 2. Set Realistic Headers
    await page.setExtraHTTPHeaders({
      'Accept-Language': 'en-US,en;q=0.9',
      'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24"'
    });

    // 3. Navigate with Network Idle Guard
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });

    // 4. Extract Structured Data
    const data = await page.evaluate(() => {
      const items = [];
      document.querySelectorAll('.job-card, .listing-item').forEach((el) => {
        const title = el.querySelector('h2, .title')?.innerText?.trim();
        const link = el.querySelector('a')?.href;
        if (title && link) items.push({ title, link });
      });
      return items;
    });

    return data;
  } finally {
    await browser.close();
  }
}
```

---

### Pattern B: Resilient Python Requests Session with Proxy Rotation
```python
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_scraping_session(proxies: dict = None) -> requests.Session:
    """Configures resilient requests session with automatic retry backoff."""
    session = requests.Session()
    
    retries = Retry(
        total=5,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    })
    
    if proxies:
        session.proxies.update(proxies)
        
    return session
```

---

## 4. Verification Command
Test scraper session and IP rotation:
```bash
python3 scripts/scraper_helper.py --test-ip
```
