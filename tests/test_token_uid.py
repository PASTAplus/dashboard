#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_token_uid

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

from webapp.auth import token_uid

sys.path.insert(0, os.path.abspath('../src'))
logger = daiquiri.getLogger('test_token_uid: ' + __name__)

uid = 'dduck'

class TestTokenUid(unittest.TestCase):

    def setUp(self):
        self.token = token_uid.to_token(uid=uid)

    def tearDown(self):
        token_uid.remove_token(token=self.token.decode())

    def test_token(self):
        token = token_uid.to_token(uid=uid)
        self.assertIsNotNone(token)
        token_uid.remove_token(token=token.decode())

    def test_is_valid(self):
        self.assertTrue(token_uid.decode_uid(token=self.token.decode()))


if __name__ == '__main__':
    unittest.main()