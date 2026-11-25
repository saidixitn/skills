---
name: email-reports
description: >-
  Use when designing automated daily HTML email digests, building responsive
  KPI metric summary tables, configuring multi-SMTP fallback delivery, or
  dispatching scheduled background performance reports.
---

# Automated HTML Analytics & Email Reports Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Generating responsive, dark-mode compatible HTML email performance reports.
- Dispatching scheduled daily/weekly metric digests to stakeholders via SMTP or Resend API.
- Formatting KPI comparison cards (clicks, conversions, server health, active domains).
- Implementing multi-SMTP server fallback delivery to prevent notification failures.
- Automating morning cron jobs that aggregate MongoDB data into executive email summaries.

---

## 2. Hard Architectural Rules

1. **Inline CSS Styles Only**:
   Email clients (Gmail, Outlook, Apple Mail) strip `<style>` blocks in the `<head>` or ignore external stylesheets. Always use **inline CSS styles** (`style="..."`) on table cells, rows, and typography.

2. **Table-Based Layout Architecture**:
   Never use modern CSS Flexbox (`display: flex`) or CSS Grid (`display: grid`) for email bodies. Outlook's rendering engine (Microsoft Word) completely breaks flex layouts. Always use classic HTML `<table>` elements with explicit widths.

3. **Multi-SMTP Failover**:
   Never rely on a single SMTP server for mission-critical daily reports. If your primary SMTP server times out or hits daily relay limits, catch the exception and immediately retry through a secondary fallback relay.

4. **Sanitized SMTP Credentials**:
   Never store SMTP passwords or server IPs in report scripts. Load credentials from environment variables (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`).

---

## 3. Production Code Patterns

### Pattern A: Master Daily Performance Digest Engine (Sai Dixit Production Script)
Grounded directly in your `vps/stats_email.py` reporting engine:

```python
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any

def generate_report_html(report_date: str, metrics: List[Dict[str, Any]], total_clicks: int) -> str:
    """Generates email-client compatible responsive HTML table."""
    rows_html = ""
    for idx, row in enumerate(metrics):
        bg = "#16181b" if idx % 2 == 0 else "#121314"
        rows_html += f"""
        <tr style="background-color: {bg};">
          <td style="padding: 12px; color: #ffffff; font-size: 13px; font-family: sans-serif; border-bottom: 1px solid #222;">{row.get('domain')}</td>
          <td style="padding: 12px; color: #10b981; font-size: 13px; font-family: sans-serif; font-weight: bold; text-align: right; border-bottom: 1px solid #222;">{row.get('clicks', 0):,}</td>
          <td style="padding: 12px; color: #9ea0a6; font-size: 13px; font-family: sans-serif; text-align: center; border-bottom: 1px solid #222;">{row.get('status', 'OK')}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
      <body style="margin: 0; padding: 20px; background-color: #0a0a0a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #121314; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; overflow: hidden;">
          <tr>
            <td style="padding: 24px; background: #16181b; border-bottom: 1px solid rgba(255,255,255,0.08);">
              <h2 style="margin: 0; color: #ffffff; font-size: 20px;">Daily Performance Digest</h2>
              <p style="margin: 4px 0 0; color: #9ea0a6; font-size: 13px;">Date: {report_date}</p>
            </td>
          </tr>
          <tr>
            <td style="padding: 20px;">
              <div style="background-color: #1a1d21; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
                <span style="color: #9ea0a6; font-size: 12px; text-transform: uppercase;">Total Network Clicks</span>
                <div style="color: #ffffff; font-size: 28px; font-weight: bold; margin-top: 4px;">{total_clicks:,}</div>
              </div>
              <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;">
                <thead>
                  <tr style="background-color: #1a1d21;">
                    <th align="left" style="padding: 10px; color: #9ea0a6; font-size: 11px; text-transform: uppercase;">Domain</th>
                    <th align="right" style="padding: 10px; color: #9ea0a6; font-size: 11px; text-transform: uppercase;">Clicks</th>
                    <th align="center" style="padding: 10px; color: #9ea0a6; font-size: 11px; text-transform: uppercase;">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {rows_html}
                </tbody>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

def send_email_digest(subject: str, html_body: str, recipient: str):
    """Sends HTML email with SMTP server fallback."""
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", 587))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(host, port, timeout=15) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
```

---

## 4. Verification Command
Test SMTP connection and send preview email:
```bash
python3 scripts/email_dispatcher.py --test-connection
```
