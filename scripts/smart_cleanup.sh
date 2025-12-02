#!/bin/bash

# --- CONFIGURATION ---
DAYS_TO_KEEP=30
LOG_RETENTION="2weeks"

# We need to know the user to clean their specific Trash
TARGET_USER="<change_me>"
TARGET_HOME="/home/$TARGET_USER"
DOWNLOADS_DIR="$TARGET_HOME/Downloads"

# 1. Clean 'Downloads'
echo "--- Cleaning Downloads (Older than $DAYS_TO_KEEP days) ---"
if [ -d "$DOWNLOADS_DIR" ]; then
    find "$DOWNLOADS_DIR" -mindepth 1 -type f -mtime +$DAYS_TO_KEEP -print -delete
    find "$DOWNLOADS_DIR" -mindepth 1 -type d -empty -delete
else
    echo "Downloads directory not found."
fi

# 2. Clean Trash
echo "--- Emptying Trash (Older than $DAYS_TO_KEEP days) ---"
# 'yes' forces approval if trash-empty prompts for it
yes | sudo -u $TARGET_USER trash-empty $DAYS_TO_KEEP

# 3. Vacuum Logs
echo "--- Vacuuming System Logs ---"
journalctl --vacuum-time=$LOG_RETENTION
