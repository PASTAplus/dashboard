#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_soh

:Synopsis:

:Author:
    servilla
  
:Created:
    3/20/18
"""
import os
import sys
import unittest

import daiquiri

from soh.config import Config
from webapp.health.health_check import SystemState

logger = daiquiri.getLogger('test_soh.py: ' + __name__)

sys.path.insert(0, os.path.abspath('../src'))


class TestSOH(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_system_state(self):
        system = SystemState()
        state = system.state
        self.assertIsNotNone(state)

    def test_server_state(self):
        host = Config.servers['VOCAB']
        system = SystemState()
        server_state = system.server_state(host=host)
        self.assertIsNotNone(server_state)

    def test_server_status(self):
        host = Config.servers['LDAP_LTER']
        system = SystemState()
        server_status = system.server_status(host=host)
        a = system.server_status(host=host)[0]
        b = system.server_status(host=host)[1]
        self.assertIsNotNone(server_status)

    def test_tier_state(self):
        tier = 'PRODUCTION'
        system = SystemState()
        tier_state = system.tier_state(tier=tier)
        self.assertIsNotNone(tier_state)

    def test_tier_status(self):
        tier = 'PRODUCTION'
        system = SystemState()
        tier_status = system.tier_status(tier=tier)
        self.assertIsNotNone(tier_status)


if __name__ == '__main__':
    unittest.main()
