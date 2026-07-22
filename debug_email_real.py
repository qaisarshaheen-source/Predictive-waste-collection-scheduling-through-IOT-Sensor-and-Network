import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys

# Add project root
sys.path.append(os.getcwd())
from config import *

print(f"Testing email connection...")
print(f"Server: {MAIL_SERVER}:{MAIL_PORT}")
print(f"User: {MAIL_USERNAME}")
print(f"Recipient: {ALERT_EMAIL_RECIPIENT}")

# Try to clean password just in case
CLEAN_PASSWORD = MAIL_PASSWORD.replace(" ", "")

msg = MIMEMultipart()
msg['From'] = MAIL_USERNAME
msg['To'] = ALERT_EMAIL_RECIPIENT
msg['Subject'] = "Debug Test Email"
msg.attach(MIMEText("If you see this, the email system is working!", 'plain'))

try:
    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
    server.set_debuglevel(1) # Show full SMTP conversation
    server.starttls()
    server.login(MAIL_USERNAME, CLEAN_PASSWORD)
    server.send_message(msg)
    server.quit()
    print("\nSUCCESS: Email sent successfully!")
except Exception as e:
    print(f"\nFAILURE: {e}")
