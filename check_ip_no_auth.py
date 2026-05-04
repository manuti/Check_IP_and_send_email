#!/usr/bin/env python3
# Sends an email with the current IP address when the device connects to a
# network other than its usual home network.
#
# All configuration is read from environment variables — no credentials in
# this file. Set them in /etc/check-ip-email.env (see check-ip-email.service).

import os
import smtplib
import subprocess
import time
from email.message import EmailMessage


def require_env(key):
    val = os.environ.get(key)
    if not val:
        raise SystemExit(f'[error] Required environment variable not set: {key}')
    return val


FIXED_IP    = os.environ.get('FIXED_IP', '')
IFACE       = os.environ.get('NETWORK_IFACE', 'eth0')
SMTP_USER   = require_env('SMTP_USERNAME')
SMTP_PASS   = require_env('SMTP_PASSWORD')
SMTP_TO     = require_env('SMTP_RECIPIENT')
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT   = int(os.environ.get('SMTP_PORT', '465'))


result = subprocess.run(
    ['ip', '-4', 'addr', 'show', IFACE],
    capture_output=True, text=True
)

inet_string = None
for line in result.stdout.splitlines():
    stripped = line.strip()
    if stripped.startswith('inet '):
        inet_string = stripped.split()[1].split('/')[0]
        break

if inet_string is None:
    print(f'\033[31;1m[warning]\033[0m Interface {IFACE} not found or has no IPv4 address')
elif inet_string == FIXED_IP:
    print(f'\033[32;1m[ ok ]\033[0m Home IP {inet_string} on {IFACE} — no email sent')
else:
    msg = EmailMessage()
    msg['From'] = SMTP_USER
    msg['To'] = SMTP_TO
    msg['Subject'] = f'IP Address ({IFACE}) at: {time.asctime()}'
    msg.set_content(f'Interface {IFACE} has IP address: {inet_string}')

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f'\033[36;1m[info]\033[0m Emailed {IFACE} IP {inet_string} to {SMTP_TO}')
