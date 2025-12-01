#!/bin/bash

# Use this file in crontab to load secrets before health_check.py
# 1. Define Paths
USER_HOME="/home/ntune1030"
SECRETS_FILE="$USER_HOME/.nas_secrets"
PYTHON_EXEC="$USER_HOME/scripts/venv/bin/python3"
SCRIPT_FILE="$USER_HOME/scripts/health_check.py"

# 2. Load Secrets (Crucial Step)
if [ -f "$SECRETS_FILE" ]; then
    source "$SECRETS_FILE"
    export NAS_EMAIL_USER
    export NAS_EMAIL_PASS
else
    echo "Error: Secrets file not found at $SECRETS_FILE"
fi

# 3. Run the Health Check
$PYTHON_EXEC "$SCRIPT_FILE"
