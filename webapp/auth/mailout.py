#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: mailout

:Synopsis:

:Author:
    servilla

:Created:
    5/24/18
"""
import smtplib

import daiquiri

from webapp.config import Config
from webapp.auth.ldap_user import LdapUser

logger = daiquiri.getLogger('mailout: ' + __name__)


def send_mail(subject=None, msg=None, to=None):
    result = False
    # Convert subject and msg to byte array
    body = ('Subject: ' + subject + '\n').encode() + \
           ('To: ' + to + '\n').encode() + \
           ('From: ' + Config.HOVER_MAIL + '\n\n').encode() + \
           (msg + '\n').encode()

    smtpObj = smtplib.SMTP('mail.hover.com', 587)
    try:
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(Config.HOVER_MAIL, Config.HOVER_PASSWORD)
        smtpObj.sendmail(from_addr=Config.HOVER_MAIL, to_addrs=to, msg=body)
        result = True
    except Exception as e:
        response = 'Sending email failed - ' + str(e)
        logger.error(response)
    finally:
        smtpObj.quit()
    return result


def reset_password_mail_body(ldap_user=None, url=None):
    gn = ldap_user.gn
    msg = 'Hi ' + gn + ',\n\n' + \
        'Please use the following URL to reset your EDI account ' + \
        'password:\n\n' + \
        url + \
        '\n\nIf you have received this email in error, please ignore.' + \
        '\n\nSincerely,\nThe EDI Team\n'
    return msg


def main():
    return 0


if __name__ == "__main__":
    main()
