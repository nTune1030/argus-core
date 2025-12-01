#!/bin/bash

# --- CONFIGURATION ---
TARGET_USER="<change_me>"
TARGET_HOME="/home/$TARGET_USER"
LOG_FILE="/var/log/nas_maintenance.log"
SECRETS_FILE="$TARGET_HOME/.nas_secrets"
PYTHON_SCRIPT="$TARGET_HOME/scripts/send_log.py"
# ---------------------

# 1. Start Logging
exec > >(tee -i $LOG_FILE)
exec 2>&1

echo "====================================================="
echo "NAS MAINTENANCE STARTED: $(date)"
echo "====================================================="

# 2. Load Secrets
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

# 4. Update Snap
if command -v snap >/dev/null; then
    echo -e "\n--- Updating Snaps ---"
    snap refresh
    
    echo "Cleaning old snaps..."
    snap list --all | awk '/disabled/{print $1, $3}' | \
        while read snapname revision; do
            snap remove "$snapname" --revision="$revision"
        done
fi

# 5. Vacuum Logs (Filesystem level)
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

# 7. Email Report
VENV_PYTHON="$TARGET_HOME/scripts/venv/bin/python3"
echo "Sending email report..."
$VENV_PYTHON "$PYTHON_SCRIPT" "NAS Maintenance Report $REBOOT_MSG" "$LOG_FILE"
