import smtplib
import ssl
import os

# 1. Load and Clean Secrets
raw_email = os.getenv("NAS_EMAIL_USER")
raw_pass = os.getenv("NAS_EMAIL_PASS")

if not raw_email or not raw_pass:
    print("❌ Error: Environment variables are empty.")
    exit()

# STRIP: Removes invisible newlines at the end
# REPLACE: Removes spaces from the App Password (e.g., "abcd efgh" -> "abcdefgh")
email_user = raw_email.strip()
email_pass = raw_pass.strip().replace(" ", "")

print(f"🔍 DEBUG: Attempting login for: [{email_user}]")
print(f"🔍 DEBUG: Password length: {len(email_pass)} characters")

# 2. Setup Email
port = 465
context = ssl.create_default_context()
message = f"Subject: NAS Test\n\nSent from {email_user} on Ubuntu."

# 3. Send
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(email_user, email_pass)
        server.sendmail(email_user, email_user, message)
    print("✅ Success! Email sent.")
except Exception as e:
    print(f"❌ Failed: {e}")
