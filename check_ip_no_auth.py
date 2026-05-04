#!/usr/bin/env python3
# If you plug a Raspberry Pi into a foreign network whilst running it headless
# (without a monitor), this script emails you the IP address so you can SSH in.
#
# It sends an email only when the IP differs from your usual home IP.
#
# Gmail requirement: create an App Password at myaccount.google.com/apppasswords
# (requires 2-step verification enabled on the account).

import smtplib
import subprocess
import time
from email.message import EmailMessage

################################################
###### Remember to set all constants here ######
################################################
FIXED_IP = '10.0.1.2'          # Your normal home IP — no email sent if matched
IP_FILEPATH = '/home/pi/current_ip.txt'
SMTP_USERNAME = 'YOUR_SENDER_EMAIL_ADDRESS@gmail.com'
SMTP_PASSWORD = 'YOUR_APP_PASSWORD'  # 16-char App Password from Google, not your login password
SMTP_RECIPIENT = 'YOUR_RECIPIENT_EMAIL_ADDRESS@gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SSL_PORT = 465
################################################
################################################


subprocess.run(['ip', '-4', 'addr'], stdout=open(IP_FILEPATH, 'w'), check=True)

inet_string = None

with open(IP_FILEPATH, 'r') as ip_file:
    for line in ip_file:
        if 'eth0:' in line:
            inet_line = next(ip_file, None)
            if inet_line and 'inet ' in inet_line:
                stripped = inet_line.strip()
                # Extract IP from "inet x.x.x.x/prefix"
                inet_string = stripped.split()[1].split('/')[0]
            break

if inet_string is None:
    print('\033[31;1m[warning]\033[0m eth0 not found or has no IPv4 address')
elif inet_string == FIXED_IP:
    print(f'\033[32;1m[ ok ]\033[0m Normal home IP address {inet_string} found — no email sent')
else:
    subject = f'IP Address from Raspberry Pi at: {time.asctime()}'
    body = f'The IP address is: {inet_string}'

    msg = EmailMessage()
    msg['From'] = SMTP_USERNAME
    msg['To'] = SMTP_RECIPIENT
    msg['Subject'] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL(SMTP_SERVER, SSL_PORT) as server:
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)

    print(f'\033[36;1m[info]\033[0m Emailed eth0 IP address {inet_string} to {SMTP_RECIPIENT}')
