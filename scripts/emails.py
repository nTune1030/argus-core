#!/usr/bin/env python3

import mimetypes
import smtplib
import ssl
import os
from email.message import EmailMessage
from pathlib import Path
from typing import Union, Optional

# --- CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def generate_email(
    sender: str, 
    recipient: str, 
    subject: str, 
    body: str, 
    attachment_path: Optional[Union[str, Path]] = None
) -> EmailMessage:
    """
    Creates a MIME EmailMessage object with optional attachment.
    Accepts attachment_path as either a string or a Path object.
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    msg.set_content(body)

    if attachment_path:
        # Normalize input to a Path object
        file_path = Path(attachment_path)

        if file_path.is_file():
            # Guess the file type (png, jpg, pdf)
            # mimetypes.guess_type requires a string or path-like object
            ctype, encoding = mimetypes.guess_type(file_path)
            
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compressed)
                ctype = 'application/octet-stream'

            maintype, subtype = ctype.split('/', 1)

            # Read and attach
            with file_path.open('rb') as f:
                file_data = f.read()

            msg.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename=file_path.name
            )
    
    return msg

def send_email(message: EmailMessage) -> bool:
    """
    Sends the email using credentials from Environment Variables.
    Returns True if successful, False otherwise.
    """
    # 1. Load and Clean Secrets safely
    raw_user = os.getenv("NAS_EMAIL_USER")
    raw_pass = os.getenv("NAS_EMAIL_PASS")

    if not raw_user or not raw_pass:
        # Print to stderr for better error logging in cron/systemd
        print("❌ Error: Secrets not found in environment.")
        return False

    email_user = raw_user.strip()
    # Remove spaces from App Password just in case user copied them
    email_pass = raw_pass.strip().replace(" ", "")

    # 2. Send via SSL
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(email_user, email_pass)
            server.send_message(message)
        return True
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ General Error sending email: {e}")
        return False
