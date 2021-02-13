#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_auth_user

:Synopsis:

:Author:
    servilla
  
:Created:
    3/8/18
"""
import daiquiri

from webapp.config import Config
from webapp.auth.user import User


logger = daiquiri.getLogger(__name__)


user_dn = Config.TEST_USER_DN
user_pw = Config.TEST_USER_PW
user_uid = Config.TEST_USER_UID
user_name = Config.TEST_USER_NAME


def test_authenticate():
    auth_token = User.authenticate(user_dn=user_dn, password=user_pw)
    assert auth_token is not None


def test_get_id():
    auth_token = User.authenticate(user_dn=user_dn, password=user_pw)
    user = User(auth_token=auth_token)
    user_id = user.get_id()
    assert user_id == auth_token


def test_get_dn():
    auth_token = User.authenticate(user_dn=user_dn, password=user_pw)
    user = User(auth_token)
    dn = user.get_dn()
    assert dn == user_dn


def test_get_uid():
    auth_token = User.authenticate(user_dn=user_dn, password=user_pw)
    user = User(auth_token)
    uid = user.get_uid()
    assert uid == user_uid


def test_get_name():
    auth_token = User.authenticate(user_dn=user_dn, password=user_pw)
    user = User(auth_token)
    name = user.get_username()
    assert name == user_name
