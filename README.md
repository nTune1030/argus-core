# 👁️ Argus Core

> **"The All-Seeing."**
> Automated Market Intelligence, System Monitoring, and Self-Healing Infrastructure for the Argus Headless Node.

## 📖 Overview
This repository contains the automation logic ("The Brain") for **Argus**, a headless Ubuntu server repurposed from an HP laptop. It serves as a centralized NAS, a secure remote gateway, and an autonomous data scraper.

The system operates on a **"Set and Forget"** philosophy:
1.  **Scrapes** real-time market data from target e-commerce platforms using headless browsers.
2.  **Analyzes** trends using Pandas/Matplotlib.
3.  **Alerts** the administrator via Email (Gmail/Proton).
4.  **Maintains** its own health and storage hygiene automatically.

## 🏗️ Architecture & Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **OS** | Ubuntu Server 24.04 | Headless environment managed via SSH & Cockpit. |
| **Core Logic** | Python 3.12 | Web scraping, data processing, and alerting. |
| **Scrapping** | Playwright (Firefox) | Headless browser automation with dynamic layout detection. |
| **Analysis** | Pandas & Matplotlib | CSV data manipulation and trend visualization. |
| **Networking** | Tailscale | Zero-config Mesh VPN for global secure access. |
| **Storage** | Samba (SMB) | 256GB Network Drive mapped locally (Z:) and remotely. |
| **Scheduling** | Cron | Precise task orchestration (Hourly, Daily, Weekly). |

## 📂 Directory Structure

```text
/home/<user_name>/
├── nas_storage/            # (Z: Drive) Shared storage
│   ├── market_prices.csv   # Historical market data (not tracked)
│   └── price_trend.png     # Generated weekly chart (not tracked)
├── scripts/                # Active automation scripts
│   ├── venv/               # Python Virtual Environment
│   ├── market_scanner.py   # The Market Watcher (not tracked)
│   ├── plot_prices.py      # The Data Analyst (not tracked)
│   ├── health_check.py     # The Doctor
│   └── maintain_system.sh  # The Janitor
└── nas_repo/               # This Git Repository (Version Control)
```

## 🤖 Automation Schedule

| Frequency | Task | Description |
| :--- | :--- | :--- |
| **Hourly**  | health_check.py  | Checks CPU, RAM, Disk Space, and Network status. Alerts via email if critical thresholds are breached.  |
| **Daily (5 AM)** | smart_cleanup.sh  | Vacuums system logs, empties Trash (>30 days), and cleans Downloads.  |
| **Every 4 Hrs** | market_scanner.py | Scrapes target websites for specific items, filters "junk" listings, and logs valid deals to CSV. |
| **Weekly (Mon 9 AM)** | plot_prices.py | Generates a visual trend line of the CSV data and emails a PNG report. |
| **Weekly (Sun 4 AM)**  | maintain_system.sh  | Runs APT updates, upgrades system packages, cleans Snap cache, and checks for reboot requirements.  |

## 🛠️ Setup & Configuration
1. **Environment Variables**
This project relies on a secured secrets file `(~/.nas_secrets)` to handle credentials. **Do not commit this file.**
```bash
export NAS_EMAIL_USER="your_email@protonmail.com"
export NAS_EMAIL_PASS="your_app_password"
```

2. **Python Dependencies**
All Python scripts run inside a virtual environment to protect the system OS.
```bash
python3 -m venv ~/scripts/venv
source ~/scripts/venv/bin/activate
pip install playwright pandas matplotlib psutil
playwright install firefox
```

## 🛡️ Security
  * **SSH:** Password-less Key-based authentication.
  * **Firewall:** UFW enabled, allowing only SSH, Samba, and Tailscale traffic.
  * **Isolation:** Scraper runs in a sandboxed Firefox instance.
---
Maintained by [nTune1030](https://www.github.com/nTune1030)
