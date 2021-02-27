import os
import ssl
import smtplib
from email.mime.text import MIMEText


def send_email(to: str, subject: str, body: str, cc: str = None, bcc: str = None, mimetype: str = 'plain') -> bool:
    port = int(os.getenv('SMTP_PORT', '587'))
    smtp_server = os.getenv('SMTP_SERVER')
    sender_email = os.getenv('SMTP_USERNAME')
    sender_password = os.getenv('SMTP_PASSWORD')
    if not(smtp_server) or not(sender_email) or not (sender_password):
        return False
    context = ssl.create_default_context()
    message = MIMEText(body, mimetype)
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = to
    message['CC'] = cc
    message['BCC'] = bcc
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, sender_password)
        server.send_message(message)
        return True
