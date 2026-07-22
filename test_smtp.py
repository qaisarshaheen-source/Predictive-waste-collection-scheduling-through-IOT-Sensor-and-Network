import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

gmail_user = 'rb0494259@gmail.com'
gmail_pass = 'dbwv mvlq nkjb acam'
to_email = 'shahzadabbas4178@gmail.com'  # Recipient
subject = 'Config Test - Smart Waste Bin'
body = 'Ye test email hai. Config sahi lag raha hai! 📧'

msg = MIMEMultipart()
msg['From'] = gmail_user  # Ya MAIL_DEFAULT_SENDER use karo
msg['To'] = to_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(gmail_user, gmail_pass)
    server.sendmail(gmail_user, to_email, msg.as_string())
    server.quit()
    print("✅ Email bheja gaya! Check inbox/spam.")
except Exception as e:
    print(f"❌ Error: {e}")