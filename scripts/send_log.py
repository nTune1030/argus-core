#!/usr/bin/env python3


import sys
import os
import emails # local module

# USAGE: python3 send_log.py "Subject Line" "/path/to/log.txt"

if len(sys.argv) < 3:
    print("Usage: send_log.py <subject> <logfile>")
    sys.exit(1)

subject = sys.argv[1]
log_file = sys.argv[2]
user_email = os.getenv("NAS_EMAIL_USER")

# Read the log file
with open(log_file, 'r') as f:
    body = f.read()

# Send
email = emails.generate_email(
    sender=user_email,
    recipient=user_email,
    subject=subject,
    body=body
)

if emails.send_email(email):
    print("Log emailed successfully.")
else:
    print("Failed to email log.")
