#!/bin/bash

# =================================================================
#  SYSTEM MAINTENANCE (Dynamic)
#  Updates OS and cleans logs.
# =================================================================

# 1. DYNAMIC CONFIGURATION
# ------------------------
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
USER_HOME="$(dirname "$SCRIPT_DIR")"

# Note: We don't need TARGET_USER here, just the path to secrets

LOG_FILE="/var/log/nas_maintenance.log"
SECRETS_FILE="$USER_HOME/.nas_secrets"
PYTHON_SCRIPT="$USER_HOME/scripts/send_log.py"

# 2. START LOGGING
# ----------------
exec > >(tee -i $LOG_FILE)
exec 2>&1

echo "====================================================="
echo "NAS MAINTENANCE STARTED: $(date)"
echo "====================================================="

# 3. LOAD SECRETS
# ---------------
if [ -f "$SECRETS_FILE" ]; then
    source "$SECRETS_FILE"
    export NAS_EMAIL_USER
    export NAS_EMAIL_PASS
else
    echo "❌ Error: Secrets file not found at $SECRETS_FILE"
fi

# 4. UPDATE APT
# -------------
echo -e "\n--- Updating APT ---"
apt-get update
apt-get full-upgrade -y
apt-get autoremove -y
apt-get autoclean -y

# 5. UPDATE SNAPS
# ---------------
if command -v snap >/dev/null; then
    echo -e "\n--- Updating Snaps ---"
    snap refresh
    
    echo "Cleaning old snaps..."
    snap list --all | awk '/disabled/{print $1, $3}' | \
        while read snapname revision; do
            snap remove "$snapname" --revision="$revision"
        done
fi

# 6. VACUUM LOGS
# --------------
echo -e "\n--- Vacuuming Logs ---"
journalctl --vacuum-size=100M

# 7. CHECK REBOOT
# ---------------
REBOOT_MSG=""
if [ -f /var/run/reboot-required ]; then
    echo -e "\n*** SYSTEM REQUIRES REBOOT ***"
    REBOOT_MSG="[REBOOT REQUIRED]"
fi

echo "====================================================="
echo "MAINTENANCE COMPLETE: $(date)"
echo "====================================================="

# 8. EMAIL REPORT
# ---------------
echo "Sending email report..."
if [ -f "$PYTHON_SCRIPT" ]; then
    python3 "$PYTHON_SCRIPT" "NAS Maintenance Report $REBOOT_MSG" "$LOG_FILE"
else
    echo "❌ Python emailer not found."
fi
