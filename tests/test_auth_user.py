#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_auth_user

:Synopsis:

:Author:
    servilla
  
:Created:
    3/8/18
"""
import os
import sys
import unittest

import daiquiri

from webapp.config import Config
from webapp.auth.user import User


sys.path.insert(0, os.path.abspath('../webapp'))
logger = daiquiri.getLogger(__name__)

user_dn = Config.TEST_USER_DN
user_pw = Config.TEST_USER_PW
user_uid = Config.TEST_USER_UID
user_name = Config.TEST_USER_NAME


class TestAuthUser(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_authenticate(self):
        auth_token = User.authenticate(user_dn=user_dn, password=user_pw)
        self.assertIsNotNone(auth_token)

    def test_get_id(self):
        auth_token = User.authenticate(user_dn=user_dn, password=user_pw)
        user = User(auth_token=auth_token)
        user_id = user.get_id()
        self.assertEqual(user_id, auth_token)

    def test_get_dn(self):
        auth_token = User.authenticate(user_dn=user_dn, password=user_pw)
        user = User(auth_token)
        dn = user.get_dn()
        self.assertEqual(dn, user_dn)

    def test_get_uid(self):
        auth_token = User.authenticate(user_dn=user_dn, password=user_pw)
        user = User(auth_token)
        uid = user.get_uid()
        self.assertEqual(uid, user_uid)

    def test_get_name(self):
        auth_token = User.authenticate(user_dn=user_dn, password=user_pw)
        user = User(auth_token)
        name = user.get_username()
        self.assertEqual(name, user_name)


if __name__ == '__main__':
    unittest.main()