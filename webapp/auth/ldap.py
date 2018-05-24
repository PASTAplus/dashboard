#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: ldap

:Synopsis:

:Author:
    servilla

:Created:
    5/22/18
"""
import daiquiri
from ldap3 import Server, Connection, ALL, HASHED_SALTED_SHA, MODIFY_REPLACE
from ldap3.utils.hashed import hashed

from config import Config

logger = daiquiri.getLogger('ldap: ' + __name__)


def add(uid=None, gn=None, sn=None, email=None, passwd=None):
    result = False
    dn = Config.LDAP_DN.replace(Config.LDAP_UID, uid)
    ldap_class = 'inetOrgPerson'
    attributes = {
        'givenName': gn,
        'sn': sn,
        'cn': gn + ' ' + sn,
        'mail': email,
        'o': 'EDI',
        'userPassword': hashed(HASHED_SALTED_SHA, passwd)
    }
    server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
    try:
        conn = Connection(server=server, user=Config.LDAP_ADMIN,
                          password=Config.LDAP_ADMIN_PASSWORD,
                          auto_bind=True, receive_timeout=30)
        result = conn.add(dn, ldap_class, attributes)
        conn.unbind()
    except Exception as e:
        logger.error(e)
    return result


def bind(uid=None, passwd=None):
    conn = None
    dn = Config.LDAP_DN.replace(Config.LDAP_UID, uid)
    server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
    try:
        conn = Connection(server=server, user=dn, password=passwd,
                          auto_bind=True, receive_timeout=30)
    except Exception as e:
        logger.error(e)
    return conn


def change_password(uid=None, passwd=None, new_passwd=None):
    result = False
    dn = Config.LDAP_DN.replace(Config.LDAP_UID, uid)
    user_password = {'userPassword': [
        (MODIFY_REPLACE, [hashed(HASHED_SALTED_SHA, new_passwd)])]}
    try:
        conn = bind(uid=uid, passwd=passwd)
        result = conn.modify(dn, user_password)
        conn.unbind()
    except Exception as e:
        logger.error(e)
    return result


def delete(uid=None):
    result = False
    dn = Config.LDAP_DN.replace(Config.LDAP_UID, uid)
    server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
    try:
        conn = Connection(server=server, user=Config.LDAP_ADMIN,
                          password=Config.LDAP_ADMIN_PASSWORD,
                          auto_bind=True, receive_timeout=30)
        result = conn.delete(dn)
        conn.unbind()
    except Exception as e:
        logger.error(e)
    return result


def get_email(uid=None):
    email = None
    filter = Config.LDAP_FILTER.replace(Config.LDAP_UID, uid)
    server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
    try:
        conn = Connection(server=server, user=Config.LDAP_ADMIN,
                          password=Config.LDAP_ADMIN_PASSWORD,
                          auto_bind=True, receive_timeout=30)
        result = conn.search(Config.LDAP_BASE, filter, attributes=['mail'])
        if result:
            entry = conn.entries[0]
            email = entry['mail']
        conn.unbind()
    except Exception as e:
        logger.error(e)
    return email


def is_registered(uid=None):
    result = False
    filter = Config.LDAP_FILTER.replace(Config.LDAP_UID, uid)
    server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
    try:
        conn = Connection(server=server, auto_bind=True, receive_timeout=30)
        result = conn.search(Config.LDAP_BASE, filter)
        conn.unbind()
    except Exception as e:
        logger.error(e)
    return result


# TODO: need to provide email verification for changes to email addresses
def reset_email(uid=None, new_email=None):
    result = False
    dn = Config.LDAP_DN.replace(Config.LDAP_UID, uid)
    email = {'mail': [(MODIFY_REPLACE, [new_email])]}
    server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
    try:
        conn = Connection(server=server, user=Config.LDAP_ADMIN,
                          password=Config.LDAP_ADMIN_PASSWORD,
                          auto_bind=True, receive_timeout=30)
        result = conn.modify(dn, email)
        conn.unbind()
    except Exception as e:
        logger.error(e)
    return result


def reset_password(uid=None, new_passwd=None):
    result = False
    dn = Config.LDAP_DN.replace(Config.LDAP_UID, uid)
    user_password = {'userPassword': [
        (MODIFY_REPLACE, [hashed(HASHED_SALTED_SHA, new_passwd)])]}
    server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
    try:
        conn = Connection(server=server, user=Config.LDAP_ADMIN,
                          password=Config.LDAP_ADMIN_PASSWORD,
                          auto_bind=True, receive_timeout=30)
        result = conn.modify(dn, user_password)
        conn.unbind()
    except Exception as e:
        logger.error(e)
    return result


def main():
    return 0


if __name__ == "__main__":
    main()
