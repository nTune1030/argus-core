#!/bin/bash

# --- CONFIGURATION ---
# How many days to keep files?
DAYS_TO_KEEP=30
LOG_RETENTION="2weeks"

# Paths
USER_HOME="/home/ntune1030"
DOWNLOADS_DIR="$USER_HOME/Downloads"
TRASH_DIR="$USER_HOME/.local/share/Trash/files"
LOG_FILE="/var/log/smart_cleanup.log"

# Email Settings
PYTHON_SCRIPT="$USER_HOME/scripts/send_log.py"
SECRETS_FILE="$USER_HOME/.nas_secrets"
# ---------------------

# 1. Start Logging
exec > >(tee -i $LOG_FILE)
exec 2>&1

echo "====================================================="
echo "SMART CLEANUP STARTED: $(date)"
echo "====================================================="

# 2. Load Secrets (for email)
if [ -f "$SECRETS_FILE" ]; then
    source "$SECRETS_FILE"
    export NAS_EMAIL_USER
    export NAS_EMAIL_PASS
fi

# 3. Clean 'Downloads' (Older than 30 Days)
echo -e "\n--- Cleaning Downloads (Older than $DAYS_TO_KEEP days) ---"
if [ -d "$DOWNLOADS_DIR" ]; then
    # Find and print files first, then delete
    find "$DOWNLOADS_DIR" -mindepth 1 -type f -mtime +$DAYS_TO_KEEP -print -delete
    # Clean empty directories in Downloads
    find "$DOWNLOADS_DIR" -mindepth 1 -type d -empty -delete
else
    echo "Downloads directory not found."
fi

# 4. Clean User Trash (Older than 30 Days)
echo -e "\n--- Emptying Trash (Older than $DAYS_TO_KEEP days) ---"
# Pipe "yes" into the command to auto-approve any prompts
yes | sudo -u ntune1030 trash-empty $DAYS_TO_KEEP
echo "Trash compacted."

# 5. Vacuum System Logs
echo -e "\n--- Vacuuming System Logs ---"
# Keep only the last 2 weeks of journals to save space
journalctl --vacuum-time=$LOG_RETENTION

echo "====================================================="
echo "CLEANUP COMPLETE: $(date)"
echo "====================================================="

# 6. Email the Report
# We check if the log has interesting content (more than just headers)
# If file line count is < 15, it probably didn't do anything, so maybe don't spam?
# For now, we will always send it so you know it worked.
echo "Sending email report..."
python3 "$PYTHON_SCRIPT" "Monthly Cleanup Report" "$LOG_FILE"
