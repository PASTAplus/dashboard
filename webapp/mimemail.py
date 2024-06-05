#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: mimemail

:Synopsis:
    Provide MIME Multipart email support (see: https://realpython.com/python-send-email/)

:Author:
    servilla

:Created:
    4/3/22
"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib
import ssl

import daiquiri

from webapp.config import Config


logger = daiquiri.getLogger(__name__)


def send_mail(subject: str, msg: str, to: str) -> bool:

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formataddr((Config.FROM_NAME, Config.FROM))
    message["To"] = formataddr(("", to))
    message["X-SES-CONFIGURATION-SET"] = "edi-managed"

    part = MIMEText(msg, "plain")
    message.attach(part)

    try:
        with smtplib.SMTP(Config.RELAY_HOST, Config.RELAY_TLS_PORT) as server:
            server.starttls()
            server.login(Config.RELAY_USER, Config.RELAY_PASSWORD)
            server.sendmail(Config.FROM, to, message.as_string())
        return True
    except Exception as e:
        logger.error(e)
        return False
