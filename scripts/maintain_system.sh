#!/bin/bash

# Note: Orchestrator handles logging and emailing. 
# We just perform the actions.

# 1. Update APT
echo "--- Updating APT ---"
apt-get update
apt-get full-upgrade -y
apt-get autoremove -y
apt-get autoclean -y

# 2. Update Snap
if command -v snap >/dev/null; then
    echo "--- Updating Snaps ---"
    snap refresh
    
    # Cleanup old revisions
    snap list --all | awk '/disabled/{print $1, $3}' | \
        while read snapname revision; do
            snap remove "$snapname" --revision="$revision"
        done
fi

# 3. Clean Logs
echo "--- Vacuuming Logs ---"
journalctl --vacuum-size=100M

# 4. Check for Reboot
if [ -f /var/run/reboot-required ]; then
    echo "*** SYSTEM REQUIRES REBOOT ***"
fi