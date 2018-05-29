#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_ldap_user

:Synopsis:

:Author:
    servilla
  
:Created:
    5/22/18
"""
import os
import sys
import unittest

import daiquiri

from webapp.auth.ldap_user import LdapUser


sys.path.insert(0, os.path.abspath('../webapp'))
logger = daiquiri.getLogger(__name__)

uid = 'dduck'
gn = 'Daffy'
sn = 'Duck'
email = 'dduck@edirepository.org'
passwd = 'ducksoup'

class TestLdapUser(unittest.TestCase):

    def setUp(self):
        self.ldap_user = LdapUser(uid=None)
        self.ldap_user.uid = uid
        self.ldap_user.gn = gn
        self.ldap_user.sn = sn
        self.ldap_user.email = email
        self.ldap_user.create()

    def tearDown(self):
        self.ldap_user.delete()

    def test_create(self):
        self.ldap_user.delete()
        self.assertTrue(self.ldap_user.create())

    def test_change_password(self):
        self.ldap_user.change_password(new_password=passwd)
        self.ldap_user.password = passwd
        self.assertTrue(self.ldap_user._valid_password())

    def test_delete(self):
        self.assertTrue(self.ldap_user.delete())

    def test_existing_user(self):
        ldap_user = LdapUser(uid='dduck')
        self.assertTrue(ldap_user.email == email)

    def test_modify(self):
        self.ldap_user.gn = 'Quack'
        self.ldap_user.email = 'quacker@edirepository.org'
        self.assertTrue(self.ldap_user.modify())

    def test_reset_password(self):
        self.ldap_user.password = passwd
        self.ldap_user.reset_password()
        self.assertTrue(self.ldap_user._valid_password())


if __name__ == '__main__':
    unittest.main()
