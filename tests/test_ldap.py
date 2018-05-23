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
from webapp.auth.ldap import LDAP


sys.path.insert(0, os.path.abspath('../webapp'))
logger = daiquiri.getLogger(__name__)


class TestLdap(unittest.TestCase):

    def setUp(self):
        self.ldap = LDAP(uid='dduck')

    def tearDown(self):
        pass

    def test_is_registered(self):
        self.assertTrue(self.ldap.is_registered())

    def test_add(self):
        gn = 'Daffy'
        sn = 'Duck'
        email = 'dduck@edirepository.org'
        passwd = 'ducksoups'
        self.assertTrue(self.ldap.add(gn=gn, sn=sn, email=email, passwd=passwd))

if __name__ == '__main__':
    unittest.main()