#!/bin/bash

# =================================================================
#  SMART CLEANUP (Dynamic)
#  Runs as Root, but cleans the Owner's files.
# =================================================================

# 1. DYNAMIC CONFIGURATION
# ------------------------
# Detect where this script is living to find the real user
SCRIPT_DIR="$(dirname "$(realpath "$0")")"  # e.g., /home/ntune1030/scripts
USER_HOME="$(dirname "$SCRIPT_DIR")"        # e.g., /home/ntune1030
TARGET_USER="$(basename "$USER_HOME")"      # e.g., ntune1030

# Configuration
DAYS_TO_KEEP=30
LOG_RETENTION="2weeks"

# Dynamic Paths
DOWNLOADS_DIR="$USER_HOME/Downloads"
LOG_FILE="/var/log/smart_cleanup.log"
PYTHON_SCRIPT="$USER_HOME/scripts/send_log.py"
SECRETS_FILE="$USER_HOME/.nas_secrets"

# 2. START LOGGING
# ----------------
exec > >(tee -i $LOG_FILE)
exec 2>&1

echo "====================================================="
echo "SMART CLEANUP STARTED: $(date)"
echo "TARGET USER DETECTED: $TARGET_USER"
echo "====================================================="

# 3. LOAD SECRETS (For Email)
# ---------------------------
if [ -f "$SECRETS_FILE" ]; then
    source "$SECRETS_FILE"
    export NAS_EMAIL_USER
    export NAS_EMAIL_PASS
else
    echo "⚠️ Warning: Secrets file not found at $SECRETS_FILE"
fi

# 4. CLEAN DOWNLOADS
# ------------------
echo -e "\n--- Cleaning Downloads (Older than $DAYS_TO_KEEP days) ---"
if [ -d "$DOWNLOADS_DIR" ]; then
    find "$DOWNLOADS_DIR" -mindepth 1 -type f -mtime +$DAYS_TO_KEEP -print -delete
    find "$DOWNLOADS_DIR" -mindepth 1 -type d -empty -delete
else
    echo "Downloads directory not found at $DOWNLOADS_DIR"
fi

# 5. CLEAN TRASH
# --------------
echo -e "\n--- Emptying Trash (Older than $DAYS_TO_KEEP days) ---"
# We switch from Root to the Target User to clean THEIR trash correctly
if command -v trash-empty &> /dev/null; then
    yes | sudo -u "$TARGET_USER" trash-empty $DAYS_TO_KEEP
    echo "Trash compacted."
else
    echo "❌ Error: 'trash-cli' is not installed."
fi

# 6. VACUUM SYSTEM LOGS
# ---------------------
echo -e "\n--- Vacuuming System Logs ---"
journalctl --vacuum-time=$LOG_RETENTION

echo "====================================================="
echo "CLEANUP COMPLETE: $(date)"
echo "====================================================="

# 7. EMAIL REPORT
# ---------------
echo "Sending email report..."
if [ -f "$PYTHON_SCRIPT" ]; then
    python3 "$PYTHON_SCRIPT" "Monthly Cleanup Report" "$LOG_FILE"
else
    echo "❌ Python emailer not found."
fi
