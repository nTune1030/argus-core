#!/bin/bash

# =================================================================
#  ARGUS ORCHESTRATOR
#  Usage: ./orchestrator.sh "Job_Name" "Command_To_Run"
# =================================================================

# 1. CONFIGURATION
# ----------------
TARGET_USER="ntune1030"  # <--- Change this to your user
HOME_DIR="/home/$TARGET_USER"
SECRETS_FILE="$HOME_DIR/.nas_secrets"
VENV_ACTIVATE="$HOME_DIR/scripts/venv/bin/activate"
LOG_DIR="$HOME_DIR/scripts/logs"
EMAIL_SENDER="$HOME_DIR/scripts/send_log.py"

# 2. PREPARATION
# ----------------
# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Load Secrets (Fixes the "Environment variables not loaded" error)
if [ -f "$SECRETS_FILE" ]; then
    set -a  # Automatically export all variables
    source "$SECRETS_FILE"
    set +a
else
    echo "❌ CRITICAL: Secrets file not found at $SECRETS_FILE"
    exit 1
fi

# Activate Python Virtual Environment (Fixes module errors)
if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
else
    echo "⚠️ Warning: Virtual environment not found."
fi

# 3. EXECUTION
# ----------------
JOB_NAME="$1"
COMMAND="$2"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/${JOB_NAME}.log"

# Print header to log
echo "=== STARTING JOB: $JOB_NAME [$TIMESTAMP] ===" > "$LOG_FILE"

# Run the command and capture BOTH output and errors to the log
# 'eval' allows complex commands with pipes/args to run correctly
eval "$COMMAND" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "=== END JOB [$EXIT_CODE] ===" >> "$LOG_FILE"

# 4. REPORTING
# ----------------
# Only email if the job FAILED (Exit code != 0) OR if it's a specific reporting job
# You can customize this logic. For now, we email the log if it's not empty.

if [ -s "$LOG_FILE" ]; then
    # If it failed, mark subject as ERROR
    if [ $EXIT_CODE -ne 0 ]; then
        SUBJECT="❌ ARGUS ERROR: $JOB_NAME"
    else
        SUBJECT="✅ ARGUS REPORT: $JOB_NAME"
    fi
    
    # Call your Python emailer to send the log content
    python3 "$EMAIL_SENDER" "$SUBJECT" "$LOG_FILE"
fi
