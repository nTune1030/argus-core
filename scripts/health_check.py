#!/usr/bin/env python3
"""
System Health Monitor.

Runs periodically (via Cron) to check critical system metrics:
- CPU Usage
- OS Drive Space
- SD Card (NAS Storage) Space
- RAM Usage
- Network Identity

If any metric exceeds the configured thresholds, an alert email is sent.
"""

import shutil
import psutil
import socket
import os
import emails  # Imports local emails.py

# --- CONFIGURATION ---
USER_EMAIL = os.getenv("NAS_EMAIL_USER")
SENDER = USER_EMAIL
RECIPIENT = USER_EMAIL

# Dynamically find home directory (e.g., /home/username)
HOME_DIR = os.path.expanduser("~")
SD_CARD_PATH = os.path.join(HOME_DIR, "nas_storage")

# --- THRESHOLDS ---
CPU_LIMIT = 80        # Percent usage
DISK_MIN_FREE = 20    # Percent free (OS Drive)
SD_MIN_FREE = 10      # Percent free (Data Drive)
MEM_MIN_MB = 100      # MB free

def check_cpu_usage() -> bool:
    """Returns True if CPU usage is over limit."""
    usage = psutil.cpu_percent(interval=1)
    return usage > CPU_LIMIT

def check_disk_usage() -> bool:
    """Returns True if Root (OS) partition space is low."""
    du = shutil.disk_usage("/")
    percent_free = (du.free / du.total) * 100
    return percent_free < DISK_MIN_FREE

def check_sd_usage() -> bool:
    """Returns True if SD Card storage is low or missing."""
    try:
        du = shutil.disk_usage(SD_CARD_PATH)
        percent_free = (du.free / du.total) * 100
        return percent_free < SD_MIN_FREE
    except FileNotFoundError:
        # Critical alert if the drive unmounted itself
        return True 

def check_memory_usage() -> bool:
    """Returns True if available RAM is critically low."""
    limit = MEM_MIN_MB * 1024 * 1024 
    mem = psutil.virtual_memory()
    return mem.available < limit

def check_localhost() -> bool:
    """Returns True if hostname does not resolve to localhost."""
    try:
        localhost = socket.gethostbyname('localhost')
        return localhost != "127.0.0.1"
    except:
        return True

def main():
    if not USER_EMAIL:
        print("❌ Error: Environment variables not loaded.")
        return

    checks = [
        (check_cpu_usage, "⚠️ Critical: CPU usage is over 80%"),
        (check_disk_usage, "⚠️ Critical: OS Drive Space Low (< 20%)"),
        (check_sd_usage, "⚠️ Critical: SD Card Storage Low/Missing"),
        (check_memory_usage, "⚠️ Critical: Low Memory (< 100MB)"),
        (check_localhost, "⚠️ Critical: Localhost resolution failed")
    ]

    # Run checks
    for check_func, error_subject in checks:
        if check_func():
            print(f"Alert Triggered: {error_subject}")
            
            email = emails.generate_email(
                sender=SENDER, 
                recipient=RECIPIENT, 
                subject=f"[NAS ALERT] {error_subject}", 
                body="Please check your NAS via Cockpit or SSH."
            )
            
            if emails.send_email(email):
                print(f"✅ Alert email sent to {RECIPIENT}")
        else:
            print(f"✅ {check_func.__name__} passed.")

if __name__ == "__main__":
    main()
