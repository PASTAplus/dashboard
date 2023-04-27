#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_mailout

:Synopsis:

:Author:
    servilla
  
:Created:
    5/29/18
"""
import daiquiri

from webapp.auth.ldap_user import LdapUser
from webapp import mimemail


logger = daiquiri.getLogger(__name__)


def test_mailout():
        uid = 'chase'
        ldap_user = LdapUser(uid=uid)
        subject = 'EDI account password reset...'
        msg = reset_password_mail_body(ldap_user=ldap_user, url='https://dashboard.edirepository.org/dashboard/auth/deadlink')
        to = ldap_user.email
        assert mimemail.send_mail(subject=subject, msg=msg, to=to)


def reset_password_mail_body(ldap_user=None, url=None):
    msg = 'Hello ' + ldap_user.cn + ',\n\n' + \
          'A user account with the identifier "' + ldap_user.uid + \
          '" was created on your behalf for you to access the ' + \
          'Environmental Data Initiative data repository, namely through ' + \
          'the EDI Data Portal. Please use the following URL to set ' + \
          'your password:\n\n' + url + '\n\n' + \
          'This URL provides a one-time password reset and will expire ' + \
          'in 24 hours.\n\nIf you have received this email in error, ' + \
          'please ignore.\n\nSincerely,\nThe EDI Team'

    return msg
