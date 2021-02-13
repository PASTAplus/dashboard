#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_ldap_user

:Synopsis:

:Author:
    servilla
  
:Created:
    5/22/18
"""
import daiquiri
import pytest

from webapp.auth.ldap_user import LdapUser


logger = daiquiri.getLogger(__name__)


uid = 'dduck'
gn = 'Daffy'
sn = 'Duck'
email = 'dduck@edirepository.org'
passwd = 'ducksoup'


@pytest.fixture()
def ldap_user():
    user = LdapUser()
    user.uid = uid
    user.gn = gn
    user.sn = sn
    user.email = email
    user.create()
    yield user
    user.delete()


def test_create(ldap_user):
    ldap_user.delete()
    assert ldap_user.create()


def test_change_password(ldap_user):
    ldap_user.change_password(new_password=passwd)
    ldap_user.password = passwd
    assert ldap_user._valid_password()


def test_delete(ldap_user):
    assert ldap_user.delete()


def test_existing_user(ldap_user):
    user = LdapUser(uid='dduck')
    assert user.email == email


def test_modify(ldap_user):
    ldap_user.gn = 'Quack'
    ldap_user.email = 'quacker@edirepository.org'
    ldap_user.modify()


def test_reset_password(ldap_user):
    ldap_user.password = passwd
    ldap_user.reset_password()
    assert ldap_user._valid_password()
