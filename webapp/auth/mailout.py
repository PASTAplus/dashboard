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

from config import Config
from webapp.auth import ldap_user
from webapp.auth.ldap_user import LdapUser
from webapp.auth import token_uid

logger = daiquiri.getLogger('mailout: ' + __name__)


def send_mail(subject=None, msg=None, to=None):
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
        response = 'Sending email to ' + to + ' succeeded'
        logger.info(response)
        return response
    except Exception as e:
        response = 'Sending email failed - ' + str(e)
        logger.error(response)
        return response
    finally:
        smtpObj.quit()


def reset_password_mail_body(ldap_user=None):
    gn = ldap_user.gn
    msg = 'Hi ' + gn + ',\n\n' + \
        'Please use the following URL to reset your EDI account ' + \
        'password:\n\n' + \
        'https://dashboard.edirepository.org/dashboard/auth/reset?token=' + \
        ldap_user.token.decode() + \
        '\n\nIf you have received this email in error, please ignore.' + \
        '\n\nSincerely,\nThe EDI Team\n'
    return msg


def main():
    ldap_user = LdapUser(uid='chase', gn='chase', sn='gaucho', email='chase.gaucho@gmail.com')
    subject = 'EDI account password reset...'
    msg = reset_password_mail_body(ldap_user=ldap_user)
    to = 'servilla@unm.edu'

    r = send_mail(subject=subject, msg=msg, to=to)
    print(r)
    return 0


if __name__ == "__main__":
    main()
