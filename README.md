# Sai Dixit Naidu — Production Agent Skills Hub

A modular, battle-tested collection of specialized skills designed for autonomous AI coding agents (**Antigravity**, **ClawHub**, **Claude Code**, **OpenClaw**, **Cursor**, and **Gemini CLI**).

Built directly from real production services, background automation fleets, and creative motion frontends. Zero AI slop, zero boilerplate, pure deterministic workflows.

---

## ⚡ Quick Install

### 1. Install a Single Skill (1-Second `degit`)
Grab only the skill you need without cloning the entire repository:
```bash
npx degit saidixitn/skills/skills/google-sheets ~/.gemini/config/skills/google-sheets
```

### 2. Install All Skills (Full Suite)
Clone the complete suite directly into your local agent's skills directory:
```bash
git clone https://github.com/saidixitn/skills.git ~/.gemini/config/skills/saidixit-skills
```

### 3. One-Line Terminal Installer (`curl`)
```bash
# Install an individual skill:
curl -fsSL https://raw.githubusercontent.com/saidixitn/skills/main/install.sh | bash -s google-sheets

# Install all skills:
curl -fsSL https://raw.githubusercontent.com/saidixitn/skills/main/install.sh | bash -s --all
```

---

## 📦 Skills Directory

| Skill | Category | Description | 1-Click Install Command |
| :--- | :--- | :--- | :--- |
| **`google-sheets`** | Data | Automated bi-directional DB sync, batch cell updates, token auto-refresh | `npx degit saidixitn/skills/skills/google-sheets ~/.gemini/config/skills/google-sheets` |
| **`mongodb`** | Data | Aggregation pipelines, 100MB spill guard, cursor chunk streaming | `npx degit saidixitn/skills/skills/mongodb ~/.gemini/config/skills/mongodb` |
| **`bigquery`** | Data | Ingestion pipelines, partitioned tables, streaming transforms | `npx degit saidixitn/skills/skills/bigquery ~/.gemini/config/skills/bigquery` |
| **`data-pipelines`** | Data | Vectorized Pandas/NumPy ETL, JSON normalization, multi-format export | `npx degit saidixitn/skills/skills/data-pipelines ~/.gemini/config/skills/data-pipelines` |
| **`automated-backups`** | Infra | Mongo dumps, tar compression, Google Drive upload & quota transfer | `npx degit saidixitn/skills/skills/automated-backups ~/.gemini/config/skills/automated-backups` |
| **`minimal-design`** | Creative | Obsidian Modernism dark design system, glassmorphic elevation tokens | `npx degit saidixitn/skills/skills/minimal-design ~/.gemini/config/skills/minimal-design` |
| **`animations`** | Creative | 60–120fps hardware-accelerated physics, GSAP, Lenis, anti-FOUC | `npx degit saidixitn/skills/skills/animations ~/.gemini/config/skills/animations` |
| **`website-builder`** | Creative | Sub-100ms TTI static site engine, speculative pre-warming, SW caching | `npx degit saidixitn/skills/skills/website-builder ~/.gemini/config/skills/website-builder` |
| **`server-handling`** | Infra | Linux VPS setup, PM2 process fleet management, log rotation | `npx degit saidixitn/skills/skills/server-handling ~/.gemini/config/skills/server-handling` |
| **`api-builder`** | Backend | FastAPI & Express unified REST gateway, dependency injection, CORS | `npx degit saidixitn/skills/skills/api-builder ~/.gemini/config/skills/api-builder` |
| **`cloudflare-proxy`** | Infra | Cloudflare Workers edge reverse proxy, IP masking, SSL termination | `npx degit saidixitn/skills/skills/cloudflare-proxy ~/.gemini/config/skills/cloudflare-proxy` |
| **`api-testing`** | Testing | Postman collections, environment variables, Newman CLI automation | `npx degit saidixitn/skills/skills/api-testing ~/.gemini/config/skills/api-testing` |
| **`web-scraper`** | Automation | Resilient Puppeteer/Requests scraping, user-agent rotation, proxy pools | `npx degit saidixitn/skills/skills/web-scraper ~/.gemini/config/skills/web-scraper` |
| **`domain-monitor`** | Monitoring | Automated WHOIS checking, domain & SSL certificate expiry watchdogs | `npx degit saidixitn/skills/skills/domain-monitor ~/.gemini/config/skills/domain-monitor` |
| **`email-reports`** | Automation | Scheduled HTML analytics performance digests via SMTP/SendGrid | `npx degit saidixitn/skills/skills/email-reports ~/.gemini/config/skills/email-reports` |
| **`analytics-tracker`** | Analytics | Lightweight 1.8KB first-party tracking beacon (`v.js`), real-time ingestion | `npx degit saidixitn/skills/skills/analytics-tracker ~/.gemini/config/skills/analytics-tracker` |
| **`seo-automation`** | Automation | Google Search Console indexing submission, SEMrush rank change scrapers | `npx degit saidixitn/skills/skills/seo-automation ~/.gemini/config/skills/seo-automation` |
| **`mobile-apps`** | Mobile | Scaffolding cross-platform Android/iOS PWA apps via Capacitor | `npx degit saidixitn/skills/skills/mobile-apps ~/.gemini/config/skills/mobile-apps` |
| **`macos-apps`** | Native | Native Swift/Xcode menu bar utility apps, background polling | `npx degit saidixitn/skills/skills/macos-apps ~/.gemini/config/skills/macos-apps` |
| **`agent-rules`** | Agentic | Strict autonomous agent execution standards, zero AI boilerplate | `npx degit saidixitn/skills/skills/agent-rules ~/.gemini/config/skills/agent-rules` |

---

| **`stripe-subscriptions`** | Payments | Use when architecting Stripe billing integrations, handling webhook signatures, managing customer checkout sessions, preventing duplicate charges with idempotency keys, or configuring portal redirects. | `npx degit saidixitn/skills/skills/stripe-subscriptions ~/.gemini/config/skills/stripe-subscriptions` |

## 🔒 Confidentiality & Zero-Leak Security

Every skill in this repository is scrubbed of private keys, hardcoded passwords, active database URIs, personal email addresses, and origin IP addresses. 
Before committing or publishing, run:
```bash
python3 scripts/audit_secrets.py
```

---

## 🤖 ClawHub (`clawhub.ai`) Integration

Install any skill using the ClawHub CLI:
```bash
clawhub install @saidixitn/google-sheets
```

---

## 📜 License
MIT © [Sai Dixit Naidu](https://saidixit.vercel.app/)
