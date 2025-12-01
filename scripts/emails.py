#!/usr/bin/env python3
"""
Email Notification Module.

This module handles the construction and sending of emails using SMTP SSL.
It relies on environment variables for security to prevent hardcoding credentials.

Environment Variables Required:
    - NAS_EMAIL_USER: The sender's email address.
    - NAS_EMAIL_PASS: The sender's App Password (spaces removed automatically).
"""

import smtplib
import ssl
import os
import mimetypes
from email.message import EmailMessage
from typing import Optional

def generate_email(
    sender: str, 
    recipient: str, 
    subject: str, 
    body: str, 
    attachment_path: Optional[str] = None
) -> EmailMessage:
    """
    Creates a MIME EmailMessage object, optionally attaching a file.

    Args:
        sender (str): Email address of the sender.
        recipient (str): Email address of the receiver.
        subject (str): Subject line of the email.
        body (str): The main text content of the email.
        attachment_path (str, optional): Absolute path to a file to attach. 
                                         Defaults to None.

    Returns:
        EmailMessage: A prepared email object ready for sending.
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    msg.set_content(body)

    if attachment_path and os.path.isfile(attachment_path):
        # Guess the file type/subtype (e.g., 'image/png' or 'text/plain')
        ctype, encoding = mimetypes.guess_type(attachment_path)
        if ctype is None or encoding is not None:
            # Fallback for unknown types
            ctype = 'application/octet-stream'
        
        maintype, subtype = ctype.split('/', 1)

        try:
            with open(attachment_path, 'rb') as f:
                file_data = f.read()
            
            msg.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(attachment_path)
            )
        except IOError as e:
            print(f"⚠️ Warning: Could not attach file {attachment_path}: {e}")

    return msg

def send_email(message: EmailMessage) -> bool:
    """
    Sends the provided EmailMessage object using Gmail SMTP.

    Credentials are fetched from the environment variables 'NAS_EMAIL_USER'
    and 'NAS_EMAIL_PASS'.

    Args:
        message (EmailMessage): The prepared email object.

    Returns:
        bool: True if sent successfully, False otherwise.
    """
    # 1. Load and Clean Secrets safely
    raw_user = os.getenv("NAS_EMAIL_USER")
    raw_pass = os.getenv("NAS_EMAIL_PASS")

    if not raw_user or not raw_pass:
        print("❌ Error: Secrets not found in environment variables.")
        return False

    email_user = raw_user.strip()
    # Remove spaces from App Password just in case user copy-pasted formatting
    email_pass = raw_pass.strip().replace(" ", "")

    # 2. Send via SSL (Port 465 is standard for Gmail SSL)
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
