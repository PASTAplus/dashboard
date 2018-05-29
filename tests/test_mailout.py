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
from webapp.auth import mailout

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
        msg = mailout.reset_password_mail_body(ldap_user=ldap_user)
        to = ldap_user.email
        self.assertTrue(mailout.send_mail(subject=subject, msg=msg, to=to))


if __name__ == '__main__':
    unittest.main()