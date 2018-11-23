#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_mailout

:Synopsis:

:Author:
    servilla
  
:Created:
    5/29/18
"""
import os
import sys
import unittest

import daiquiri

from webapp.auth.ldap_user import LdapUser
from webapp import mailout

sys.path.insert(0, os.path.abspath('../src'))
logger = daiquiri.getLogger('test_mailout: ' + __name__)


class TestMailOut(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_mailout(self):
        uid = 'chase'
        ldap_user = LdapUser(uid=uid)
        subject = 'EDI account password reset...'
        msg = reset_password_mail_body(ldap_user=ldap_user, url='https://dashboard.edirepository.org/dashboard/auth/deadlink')
        to = ldap_user.email
        self.assertTrue(mailout.send_mail(subject=subject, msg=msg, to=to))


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


if __name__ == '__main__':
    unittest.main()