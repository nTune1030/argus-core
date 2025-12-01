# 👁️ Project Panoptes (Argus Core)

> **"The All-Seeing."**
> Automated Market Intelligence, System Monitoring, and Self-Healing Infrastructure for the **Argus** Headless Node.

## 📖 Overview
This repository contains the automation logic ("The Brain") for **Argus**, a headless Ubuntu server repurposed from an HP laptop. It serves as a centralized NAS, a secure remote gateway, and an autonomous data scraper.

The system operates on a **"Set and Forget"** philosophy:
1.  **Scrapes** real-time market data (eBay) using headless browsers.
2.  **Analyzes** trends using Pandas/Matplotlib.
3.  **Alerts** the administrator via Email (Gmail/Proton).
4.  **Maintains** its own health and storage hygiene automatically.

## 🏗️ Architecture & Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **OS** | Ubuntu Server 24.04 | Headless environment managed via SSH & Cockpit. |
| **Core Logic** | Python 3.12 | Web scraping, data processing, and alerting. |
| **Scraping** | Playwright (Firefox) | Headless browser automation with dynamic layout detection. |
| **Analysis** | Pandas & Matplotlib | CSV data manipulation and trend visualization. |
| **Networking** | Tailscale | Zero-config Mesh VPN for global secure access. |
| **Storage** | Samba (SMB) | 256GB Network Drive mapped locally (Z:) and remotely. |
| **Scheduling** | Cron | Precise task orchestration (Hourly, Daily, Weekly). |

## 📂 Directory Structure

```text
/home/ntune1030/
├── nas_storage/          # (Z: Drive) Shared storage
│   ├── ebay_prices.csv   # Historical market data
│   └── price_trend.png   # Generated weekly chart
├── scripts/              # Active automation scripts
│   ├── venv/             # Python Virtual Environment
│   ├── ebay_scanner.py   # The Market Watcher
│   ├── plot_prices.py    # The Data Analyst
│   ├── health_check.py   # The Doctor
│   └── maintain_system.sh# The Janitor
└── nas_repo/             # This Git Repository (Version Control)
