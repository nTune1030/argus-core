#!/usr/bin/env python3

import shutil
import psutil
import socket
import os
import sys
from pathlib import Path
import emails  # Imports your local emails.py file

# --- CONFIGURATION ---
# Auto-detects home directory (e.g., /home/ntune1030) for portability
HOME_DIR = Path.home()
USER_EMAIL = os.getenv("NAS_EMAIL_USER")
SENDER = USER_EMAIL
RECIPIENT = USER_EMAIL
BASE_BODY = "The following resource alerts were triggered on your NAS system:\n"

# Path to the mounted storage
SD_CARD_PATH = HOME_DIR / "nas_storage"

# --- THRESHOLDS ---
CPU_LIMIT_PERCENT = 80
DISK_MIN_FREE_PERCENT = 20
MEM_MIN_MB = 100
SD_MIN_FREE_PERCENT = 10

def is_cpu_high() -> bool:
    """Returns True if CPU usage is above the limit."""
    # interval=1 blocks for 1 second to get an accurate reading
    return psutil.cpu_percent(interval=1) > CPU_LIMIT_PERCENT

def is_disk_space_low() -> bool:
    """Returns True if Root (/) disk space is below limit."""
    du = shutil.disk_usage("/")
    percent_free = (du.free / du.total) * 100
    return percent_free < DISK_MIN_FREE_PERCENT

def is_memory_low() -> bool:
    """Returns True if available Memory is below limit."""
    limit_bytes = MEM_MIN_MB * 1024 * 1024
    return psutil.virtual_memory().available < limit_bytes

def is_network_broken() -> bool:
    """Returns True if localhost cannot be resolved."""
    try:
        socket.gethostbyname('localhost')
        return False
    except socket.error:
        return True

def is_sd_card_low() -> bool:
    """Returns True if SD Card space is low or drive is missing."""
    if not SD_CARD_PATH.exists():
        return True

    try:
        du = shutil.disk_usage(SD_CARD_PATH)
        percent_free = (du.free / du.total) * 100
        return percent_free < SD_MIN_FREE_PERCENT
    except (FileNotFoundError, OSError):
        return True

def main():
    # 1. Validation
    if not USER_EMAIL:
        print("Error: NAS_EMAIL_USER environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    # 2. Check for Interactive Mode (Is a human running this?)
    # If running manually, we print PASS/FAIL. If Cron, we stay silent.
    interactive = sys.stdout.isatty()

    health_checks = [
        (is_cpu_high, f"⚠️ Critical: CPU usage > {CPU_LIMIT_PERCENT}%"),
        (is_disk_space_low, f"⚠️ Critical: Root Disk Free < {DISK_MIN_FREE_PERCENT}%"),
        (is_sd_card_low, f"⚠️ Critical: SD Card Storage Low (< {SD_MIN_FREE_PERCENT}% or Missing)"),
        (is_memory_low, f"⚠️ Critical: RAM Free < {MEM_MIN_MB}MB"),
        (is_network_broken, "⚠️ Critical: Localhost DNS resolution failed")
    ]

    active_alerts = []

    if interactive:
        print(f"🔍 Running diagnostics on {socket.gethostname()}...")

    # 3. Execution Loop
    for check_func, error_msg in health_checks:
        if check_func():
            # FAIL
            if interactive:
                print(f"❌ [FAIL] {check_func.__name__} -> {error_msg}")
            active_alerts.append(error_msg)
        else:
            # PASS
            if interactive:
                print(f"✅ [PASS] {check_func.__name__}")

    # 4. Reporting
    if active_alerts:
        alert_count = len(active_alerts)
        subject = f"[NAS ALERT] {alert_count} System Issue{'s' if alert_count > 1 else ''} Detected"
        alert_list_str = "\n".join(f"- {msg}" for msg in active_alerts)
        full_body = f"{BASE_BODY}\n{alert_list_str}\n\nPlease check Cockpit or SSH immediately."

        # We allow this print in Cron because it explains why an email is being sent.
        print(f"Issues detected. Triggering email to {RECIPIENT}...")

        email = emails.generate_email(
            sender=SENDER,
            recipient=RECIPIENT,
            subject=subject,
            body=full_body
        )

        if emails.send_email(email):
            print("✅ Alert email sent successfully.")
        else:
            print("❌ Failed to send alert email.")
    else:
        # Success message ONLY for humans, not Cron.
        if interactive:
            print("\n🎉 All systems healthy. No email sent.")

if __name__ == "__main__":
    main()
