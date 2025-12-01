#!/bin/bash

# --- CONFIGURATION ---
DAYS_TO_KEEP=30
LOG_RETENTION="2weeks"

# Paths (Sanitized using $HOME and $USER)
# Note: When running as Root via Cron, $HOME is /root. 
# We must explicitly define the target user for cleanup.
TARGET_USER="<change_me>"
TARGET_HOME="/home/$TARGET_USER"

DOWNLOADS_DIR="$TARGET_HOME/Downloads"
LOG_FILE="/var/log/smart_cleanup.log"

# Helpers
SECRETS_FILE="$TARGET_HOME/.nas_secrets"
PYTHON_SCRIPT="$TARGET_HOME/scripts/send_log.py"
# ---------------------

# 1. Start Logging
exec > >(tee -i $LOG_FILE)
exec 2>&1

echo "====================================================="
echo "SMART CLEANUP STARTED: $(date)"
echo "====================================================="

# 2. Load Secrets for Python
if [ -f "$SECRETS_FILE" ]; then
    source "$SECRETS_FILE"
    export NAS_EMAIL_USER
    export NAS_EMAIL_PASS
fi

# 3. Clean 'Downloads'
echo -e "\n--- Cleaning Downloads (Older than $DAYS_TO_KEEP days) ---"
if [ -d "$DOWNLOADS_DIR" ]; then
    find "$DOWNLOADS_DIR" -mindepth 1 -type f -mtime +$DAYS_TO_KEEP -print -delete
    find "$DOWNLOADS_DIR" -mindepth 1 -type d -empty -delete
else
    echo "Downloads directory not found."
fi

# 4. Clean Trash
echo -e "\n--- Emptying Trash (Older than $DAYS_TO_KEEP days) ---"
# 'yes' forces approval if trash-empty prompts for it
yes | sudo -u $TARGET_USER trash-empty $DAYS_TO_KEEP
echo "Trash compacted."

# 5. Vacuum Logs
echo -e "\n--- Vacuuming System Logs ---"
journalctl --vacuum-time=$LOG_RETENTION

echo "====================================================="
echo "CLEANUP COMPLETE: $(date)"
echo "====================================================="

# 6. Email Report
# Note: We use the venv python to ensure dependencies are met
VENV_PYTHON="$TARGET_HOME/scripts/venv/bin/python3"
echo "Sending email report..."
$VENV_PYTHON "$PYTHON_SCRIPT" "Daily Cleanup Report" "$LOG_FILE"
