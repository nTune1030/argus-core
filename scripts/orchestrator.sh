#!/bin/bash

# =================================================================
#  ARGUS ORCHESTRATOR
#  Usage: ./orchestrator.sh "Job_Name" "Command_To_Run"
# =================================================================

# 1. CONFIGURATION
# ----------------
# Automatically detect the current user and home directory
TARGET_USER=$(whoami)
HOME_DIR="$HOME"
SECRETS_FILE="$HOME_DIR/.nas_secrets"
VENV_ACTIVATE="$HOME_DIR/scripts/venv/bin/activate"
LOG_DIR="$HOME_DIR/scripts/logs"
EMAIL_SENDER="$HOME_DIR/scripts/send_log.py"

# 2. PREPARATION
# ----------------
mkdir -p "$LOG_DIR"

if [ -f "$SECRETS_FILE" ]; then
    set -a
    source "$SECRETS_FILE"
    set +a
else
    # Fail silently to log, don't crash whole system
    echo "❌ CRITICAL: Secrets file not found." >> "$LOG_DIR/orchestrator_error.log"
    exit 1
fi

if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
fi

# 3. EXECUTION
# ----------------
JOB_NAME="$1"
COMMAND="$2"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/${JOB_NAME}.log"

# Header
echo "=== STARTING JOB: $JOB_NAME [$TIMESTAMP] ===" > "$LOG_FILE"

# Run Command
eval "$COMMAND" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Footer
echo "=== END JOB [$EXIT_CODE] ===" >> "$LOG_FILE"

# 4. REPORTING (FIXED)
# ----------------
# ONLY email if the job crashed (Exit Code != 0).
# We assume the Python scripts handle their own "Success/Alert" emails.

if [ $EXIT_CODE -ne 0 ]; then
    SUBJECT="❌ ARGUS ERROR: $JOB_NAME Failed"
    python3 "$EMAIL_SENDER" "$SUBJECT" "$LOG_FILE"
fi
