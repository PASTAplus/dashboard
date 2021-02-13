#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_token_uid

:Synopsis:

:Author:
    servilla
  
:Created:
    5/29/18
"""
import pytest

import daiquiri

from webapp.auth import token_uid


logger = daiquiri.getLogger(__name__)


uid = 'dduck'


@pytest.fixture()
def user_token():
    token = token_uid.to_token(uid=uid)
    yield token
    token_uid.remove_token(token=token.decode())


def test_token(user_token):
    user_token = token_uid.to_token(uid=uid)
    assert user_token is not None


def test_is_valid(user_token):
    token = user_token.decode()
    uid, ttl = token_uid.decode_token(token=token)
    assert uid is not None
    assert ttl is not None
