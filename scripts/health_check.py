#!/usr/bin/env python3

import shutil
import psutil
import socket
import os
import sys
from pathlib import Path
import emails  # Imports your local emails.py file

# --- CONFIGURATION ---
USER_EMAIL = os.getenv("NAS_EMAIL_USER")
SENDER = USER_EMAIL
RECIPIENT = USER_EMAIL
BASE_BODY = "The following resource alerts were triggered on your NAS system:\n"

# Use Pathlib for robust path handling
SD_CARD_PATH = Path("/home/ntune1030/nas_storage")

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
    # Convert MB to Bytes for comparison
    limit_bytes = MEM_MIN_MB * 1024 * 1024
    return psutil.virtual_memory().available < limit_bytes

def is_network_broken() -> bool:
    """
    Returns True if localhost cannot be resolved.
    Improved: Checks if resolution succeeds rather than checking for a specific IP string.
    This handles 127.0.1.1 (Debian) and ::1 (IPv6) cases correctly.
    """
    try:
        socket.gethostbyname('localhost')
        return False  # Resolution successful, network is fine
    except socket.error:
        return True   # Resolution failed

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
    # 1. Validation: Fail fast if config is missing
    if not USER_EMAIL:
        # We print to stderr so Cron might still catch this specific configuration error
        print("Error: NAS_EMAIL_USER environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    # 2. Define Checks: (Function, Error Message)
    health_checks = [
        (is_cpu_high, f"⚠️ Critical: CPU usage > {CPU_LIMIT_PERCENT}%"),
        (is_disk_space_low, f"⚠️ Critical: Root Disk Free < {DISK_MIN_FREE_PERCENT}%"),
        (is_sd_card_low, f"⚠️ Critical: SD Card Storage Low (< {SD_MIN_FREE_PERCENT}% or Missing)"),
        (is_memory_low, f"⚠️ Critical: RAM Free < {MEM_MIN_MB}MB"),
        (is_network_broken, "⚠️ Critical: Localhost DNS resolution failed")
    ]

    active_alerts = []

    # 3. Execution Loop
    # Removed "Running system health checks..." print to keep Cron silent
    for check_func, error_msg in health_checks:
        if check_func():
            # Only print FAIL logic if you are debugging manually,
            # otherwise, keep it silent unless sending the email.
            active_alerts.append(error_msg)

    # 4. Reporting: Send ONE email if there are alerts
    if active_alerts:
        alert_count = len(active_alerts)
        subject = f"[NAS ALERT] {alert_count} System Issue{'s' if alert_count > 1 else ''} Detected"

        # List comprehension for cleaner string joining
        alert_list_str = "\n".join(f"- {msg}" for msg in active_alerts)
        full_body = f"{BASE_BODY}\n{alert_list_str}\n\nPlease check Cockpit or SSH immediately."

        # Printing here is acceptable as it will log that an email attempt is happening
        print(f"Issues detected. Triggering email to {RECIPIENT}...")

        email = emails.generate_email(
            sender=SENDER,
            recipient=RECIPIENT,
            subject=subject,
            body=full_body,
            attachment_path=None
        )

        if emails.send_email(email):
            print("✅ Alert email sent successfully.")
        else:
            print("❌ Failed to send alert email.")
    
    # REMOVED the 'else' block printing "All systems healthy."
    # This ensures the script produces NO OUTPUT when successful.
    # No output = No Cron email.

if __name__ == "__main__":
    main()
