#!/usr/bin/env python3
"""
Log Dispatcher CLI.

This script allows Bash scripts to send their log files via email.
It acts as a bridge between shell scripting and the Python email module.

Usage:
    python3 send_log.py "Subject Line" "/path/to/logfile.log"
"""

import sys
import os
import emails  # Local module

def main():
    # Ensure arguments are provided
    if len(sys.argv) < 3:
        print("Usage: python3 send_log.py <subject> <logfile>")
        sys.exit(1)

    subject = sys.argv[1]
    log_file = sys.argv[2]
    
    # Fetch user email to send to self
    user_email = os.getenv("NAS_EMAIL_USER")

    if not user_email:
        print("❌ Error: NAS_EMAIL_USER not set in environment.")
        sys.exit(1)

    # Read log content
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            body = f.read()
    else:
        body = f"⚠️ Error: Log file at {log_file} could not be found."

    # Generate and Send
    email = emails.generate_email(
        sender=user_email,
        recipient=user_email,
        subject=subject,
        body=body
    )

    if emails.send_email(email):
        print("✅ Log emailed successfully.")
    else:
        print("❌ Failed to email log.")

if __name__ == "__main__":
    main()
