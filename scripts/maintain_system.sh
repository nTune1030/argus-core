#!/bin/bash


# --- CONFIGURATION ---
LOG_FILE="/var/log/nas_maintenance.log"
USER_HOME="/home/ntune1030"
SECRETS_FILE="$USER_HOME/.nas_secrets"
PYTHON_SCRIPT="$USER_HOME/scripts/send_log.py"
# ---------------------

# 1. Start Logging
# Redirect all output (stdout and stderr) to the log file
exec > >(tee -i $LOG_FILE)
exec 2>&1

echo "====================================================="
echo "NAS MAINTENANCE STARTED: $(date)"
echo "====================================================="

# 2. Load Secrets (So we can email later)
if [ -f "$SECRETS_FILE" ]; then
    source "$SECRETS_FILE"
    export NAS_EMAIL_USER
    export NAS_EMAIL_PASS
else
    echo "ERROR: Secrets file not found at $SECRETS_FILE"
fi

# 3. Update APT
echo -e "\n--- Updating APT ---"
apt-get update
apt-get full-upgrade -y
apt-get autoremove -y
apt-get autoclean -y

# 4. Update Snap (If exists)
if command -v snap >/dev/null; then
    echo -e "\n--- Updating Snaps ---"
    snap refresh
    
    # Cleanup old revisions
    echo "Cleaning old snaps..."
    snap list --all | awk '/disabled/{print $1, $3}' | \
        while read snapname revision; do
            snap remove "$snapname" --revision="$revision"
        done
fi

# 5. Clean Logs
echo -e "\n--- Vacuuming Logs ---"
journalctl --vacuum-size=100M

# 6. Check for Reboot
REBOOT_MSG=""
if [ -f /var/run/reboot-required ]; then
    echo -e "\n*** SYSTEM REQUIRES REBOOT ***"
    REBOOT_MSG="[REBOOT REQUIRED]"
fi

echo "====================================================="
echo "MAINTENANCE COMPLETE: $(date)"
echo "====================================================="

# 7. Email the Report
# We call python using the full path
echo "Sending email report..."
python3 "$PYTHON_SCRIPT" "NAS Maintenance Report $REBOOT_MSG" "$LOG_FILE"
