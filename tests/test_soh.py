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

import daiquiri

from soh.config import Config
from webapp.health.health_check import SystemState


logger = daiquiri.getLogger(__name__)


def test_system_state():
    system = SystemState()
    state = system.state
    assert state is not None


def test_server_state():
    host = Config.servers['PORTAL_EDI']
    system = SystemState()
    server_state = system.server_state(host=host)
    assert server_state is not None


def test_server_status():
    host = Config.servers['PORTAL_EDI']
    system = SystemState()
    server_status = system.server_status(host=host)
    a = system.server_status(host=host)[0]
    b = system.server_status(host=host)[1]
    assert server_status is not None


def test_tier_state():
    tier = 'PRODUCTION'
    system = SystemState()
    tier_state = system.tier_state(tier=tier)
    assert tier_state is not None


def test_tier_status():
    tier = 'PRODUCTION'
    system = SystemState()
    tier_status = system.tier_status(tier=tier)
    assert tier_status is not None
