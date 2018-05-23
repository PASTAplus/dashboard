#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_ldap

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

from webapp.config import Config
from webapp.auth import ldap

sys.path.insert(0, os.path.abspath('../webapp'))
logger = daiquiri.getLogger(__name__)

uid = 'dduck'
gn = 'Daffy'
sn = 'Duck'
email = 'dduck@edirepository.org'
passwd = 'ducksoup'

class TestLdap(unittest.TestCase):

    def setUp(self):
        ldap.add(uid=uid, gn=gn, sn=sn, email=email, passwd=passwd)

    def tearDown(self):
        ldap.delete(uid=uid)

    def test_is_registered(self):
        self.assertTrue(ldap.is_registered(uid=uid))

    def test_add(self):
        ldap.delete(uid=uid)
        self.assertTrue(
            ldap.add(uid=uid, gn=gn, sn=sn, email=email, passwd=passwd))

    def test_delete(self):
        self.assertTrue(ldap.delete(uid=uid))

    def test_reset_password(self):
        new_passwd = 'chickenbones'
        self.assertTrue(ldap.reset_password(uid=uid, new_passwd=new_passwd))
        self.assertIsNotNone(ldap.bind(uid=uid, passwd=new_passwd))

    def test_change_password(self):
        new_passwd = 'chickenbones'
        self.assertTrue(
            ldap.change_password(uid=uid, passwd=passwd, new_passwd=new_passwd))
        self.assertIsNotNone(ldap.bind(uid=uid, passwd=new_passwd))

    def test_bind(self):
        self.assertIsNotNone(ldap.bind(uid=uid, passwd=passwd))


if __name__ == '__main__':
    unittest.main()
