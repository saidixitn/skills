---
name: server-handling
description: >-
  Use when provisioning Linux VPS servers (Ubuntu/Debian), configuring PM2 process
  daemons for continuous Python and Node background services, setting up automated
  reboot resurrection, log rotation, UFW firewall security, and zero-downtime reloads.
---

# Linux VPS Fleet & PM2 Process Management Skill

## 1. Capabilities & Trigger Conditions
Activate this skill whenever a task involves:
- Deploying and managing 24/7 background worker daemons on a Linux VPS (Ubuntu/Debian).
- Orchestrating multi-process fleets with **PM2** (`ecosystem.config.js`).
- Configuring zero-downtime process restarts, auto-restart on memory thresholds, and exponential backoff retry.
- Ensuring background scripts survive server reboots (`pm2 startup` and systemd integration).
- Securing production servers with UFW firewall rules, non-root users, and SSH key authentication.

---

## 2. Hard Architectural Rules

1. **Zero Raw Background Execution**:
   Never run production scripts using `nohup python script.py &` or detached `screen`/`tmux` sessions. These lack process supervision, memory limit guards, crash recovery, and centralized logging. Always register services under PM2 or systemd.

2. **Memory Leak Safeguards**:
   Always set a `max_memory_restart` limit (e.g. `400M` or `800M`) in `ecosystem.config.js`. If a crawler, scraper, or memory-leaking script spikes, PM2 gracefully restarts it before Linux OOM-killer strikes.

3. **Log Rotation Enforcement**:
   Never allow unbounded log files to consume VPS disk space. Always configure `pm2-logrotate` with a maximum file size (e.g. `10M`) and 7-day retention.

4. **Sanitized Environment Variables**:
   Never store plaintext passwords, secret keys, or database URIs in bash scripts or systemd unit files. Load secrets via a local `.env` file with restrictive permissions (`chmod 600 .env`).

5. **UFW Port Hardening**:
   Only expose ports `80` (HTTP), `443` (HTTPS), and custom SSH ports. Keep backend application ports (e.g. `5000`, `8000`, `27017`) bound locally to `127.0.0.1` behind a reverse proxy (Nginx or Cloudflare Worker).

---

## 3. Step-by-Step Server Setup Workflow

```
[ Step 1: VPS Hardening (UFW + Non-Root User + SSH Keys) ]
                            │
                            ▼
[ Step 2: Runtime Environment (Node LTS + Python 3.11 + PM2) ]
                            │
                            ▼
[ Step 3: Define ecosystem.config.js (Workers + Python Scripts) ]
                            │
                            ▼
[ Step 4: Start Fleet (pm2 start ecosystem.config.js) ]
                            │
                            ▼
[ Step 5: Save & Register Startup Hook (pm2 startup && pm2 save) ]
```

---

## 4. Production Code Patterns

### Pattern A: Master PM2 Fleet Configuration (`ecosystem.config.js`)
Configured to supervise mixed fleets (FastAPI backends, Node servers, and Python cron jobs):

```javascript
module.exports = {
  apps: [
    // 1. Unified REST API Gateway (FastAPI / Uvicorn)
    {
      name: 'api-gateway',
      script: 'uvicorn',
      args: 'core.main:app --host 127.0.0.1 --port 5000 --workers 4',
      interpreter: 'none',
      cwd: '/var/www/vps-gateway',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PORT: 5000
      }
    },

    // 2. Continuous Data Sync Fleet (Python Daemon)
    {
      name: 'data-sync-daemon',
      script: 'updates.py',
      interpreter: 'python3',
      cwd: '/var/www/vps-gateway',
      autorestart: true,
      restart_delay: 10000, // Wait 10s before auto-restarting on failure
      max_restarts: 10,
      max_memory_restart: '400M',
      error_file: '/var/log/pm2/data-sync-error.log',
      out_file: '/var/log/pm2/data-sync-out.log',
      time: true
    },

    // 3. Domain Expiry Sentinel (Scheduled Script)
    {
      name: 'domain-watchdog',
      script: 'dc_expires.py',
      interpreter: 'python3',
      cwd: '/var/www/vps-gateway',
      cron_restart: '0 */6 * * *', // Trigger every 6 hours
      autorestart: false,
      watch: false
    }
  ]
};
```

---

### Pattern B: VPS Initial Server Setup Script
Drop-in bash provisioning commands for new Ubuntu 22.04 / 24.04 VPS instances:

```bash
#!/usr/bin/env bash
set -e

echo "=== 1. Updating System Packages ==="
apt update && apt upgrade -y

echo "=== 2. Installing Core Utilities ==="
apt install -y curl git ufw htop fail2ban python3-pip python3-venv

echo "=== 3. Hardening Firewall ==="
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "=== 4. Installing Node LTS & PM2 ==="
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
npm install -g pm2 pm2-logrotate

# Configure automatic log rotation: 10MB file limit, 7 rotated files
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true

echo "=== 5. Provisioning Complete ==="
```

---

### Pattern C: Safe Deployment & Zero-Downtime Reload Command
```bash
# Pull latest code and reload services without dropping open connections
git pull origin main
pm2 reload api-gateway --update-env
pm2 restart data-sync-daemon --update-env
pm2 save
```

---

## 5. Anti-Patterns & Operational Pitfalls

| Pitfall | Fatal Consequence | Production Solution |
| :--- | :--- | :--- |
| **Forgetting `pm2 save`** | Server reboots and all applications stay offline | Run `pm2 startup` and execute `pm2 save` after starting services |
| **No log rotation configured** | VPS runs out of disk space in 30 days (`No space left on device`) | Install `pm2-logrotate` and set `max_size 10M` |
| **Exposing raw API port to public IP** | Port scanning bots flood internal endpoints | Bind backend to `127.0.0.1` and proxy via Cloudflare or Nginx |
| **Looping crash restart spike** | Process crashes 1,000 times/min, pegging CPU at 100% | Add `restart_delay: 5000` and `max_restarts: 10` |

---

## 6. PM2 Command Quick Reference
```bash
pm2 status                  # View status, uptime, CPU & memory of all services
pm2 logs <name> --lines 50  # Tail real-time logs with timestamps
pm2 monit                   # Terminal dashboard for real-time memory/CPU
pm2 restart <name>          # Restart specific process
pm2 save                    # Snapshot current active processes for reboot resurrection
```
