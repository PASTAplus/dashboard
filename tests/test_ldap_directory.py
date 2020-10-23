#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: test_ldap_directory

:Synopsis:

:Author:
    servilla

:Created:
    10/23/20
"""
import pytest

from webapp.auth.ldap_directory import LdapDirectory


def test_list_users():
    user_list = LdapDirectory.list_ldap_users()
    assert user_list is not None
    msobol = user_list["msobol"]
    assert msobol["cn"] == "Matthew Sobol"

