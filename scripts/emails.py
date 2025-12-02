#!/usr/bin/env python3

import mimetypes
import smtplib
import ssl
import os
from email.message import EmailMessage


def generate_email(sender, recipient, subject, body, attachment_path=None):
    """Creates a MIME EmailMessage object with optional attachment."""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    msg.set_content(body)

    if attachment_path and os.path.isfile(attachment_path):
        # Guess the file type (png, jpg, pdf)
        ctype, encoding = mimetypes.guess_type(attachment_path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        
        maintype, subtype = ctype.split('/', 1)

        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            
        # Attach the file
        msg.add_attachment(
            file_data,
            maintype=maintype,
            subtype=subtype,
            filename=os.path.basename(attachment_path)
        )
        print(f"   -> Attached: {attachment_path}")

    return msg

def send_email(message):
    """Sends the email using credentials from Environment Variables."""
    # 1. Load and Clean Secrets safely
    raw_user = os.getenv("NAS_EMAIL_USER")
    raw_pass = os.getenv("NAS_EMAIL_PASS")

    if not raw_user or not raw_pass:
        print("❌ Error: Secrets not found in environment.")
        return

    email_user = raw_user.strip()
    # Remove spaces from App Password just in case
    email_pass = raw_pass.strip().replace(" ", "")

    # 2. Send via SSL
    port = 465
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email_user, email_pass)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False
