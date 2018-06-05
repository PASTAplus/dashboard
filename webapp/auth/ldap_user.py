#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: ldap_user

:Synopsis:

:Author:
    servilla
    costa

:Created:
    5/22/18
"""
import random
import string

import daiquiri
from ldap3 import Server, Connection, ALL, HASHED_SALTED_SHA, MODIFY_REPLACE
from ldap3.utils.hashed import hashed

from webapp.config import Config
from webapp.auth import token_uid

logger = daiquiri.getLogger('ldap_user: ' + __name__)



class LdapUser(object):

    def __init__(self, uid=None):
        self._uid = uid
        self._gn = None
        self._sn = None
        self._email = None
        self._cn = None
        self._password = None
        if self._uid is not None:
            if not self._load_attributes():
                msg = 'Unknown UID: {0}'.format(self._uid)
                raise UidError(msg)

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, uid):
        self._uid = uid

    @property
    def gn(self):
        return self._gn

    @gn.setter
    def gn(self, gn=None):
        self._gn = gn

    @property
    def sn(self):
        return self._sn

    @sn.setter
    def sn(self, sn=None):
        self._sn = sn

    @property
    def cn(self):
        return self._cn

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password=None):
        self._password = password

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email=None):
        self._email = email

    @property
    def token(self):
        return token_uid.to_token(uid = self._uid)

    def change_password(self, new_password):
        result = False
        dn = Config.LDAP_DN.replace(Config.LDAP_UID, self._uid)
        user_password = {'userPassword': [
            (MODIFY_REPLACE, [hashed(HASHED_SALTED_SHA, new_password)])]}
        server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
        try:
            conn = Connection(server=server, user=dn, password=self._password,
                              auto_bind=True, receive_timeout=30)
            if conn.modify(dn, user_password):
                self._password = new_password
                result = True
            conn.unbind()
        except Exception as e:
            logger.error(e)
        return result

    def create(self):
        result = False
        none_attributes = self._none_attributes()
        if len(none_attributes) != 0:
            attrs = ', '.join([_ for _ in none_attributes])
            msg = 'The following user attributes are None: {0}'.format(attrs)
            raise AttributeError(msg)
        uid = self._uid.lower() # Force lowercase
        dn = Config.LDAP_DN.replace(Config.LDAP_UID, uid)
        self._cn = self._gn + ' ' + self._sn
        if self._password is None:
            self._password = self._random_password()
        ldap_class = 'inetOrgPerson'
        # All attributes are case sensitive
        attributes = {
            'givenName': self._gn,
            'sn': self._sn,
            'cn': self._cn,
            'mail': self._email,
            'o': 'EDI',
            'userPassword': hashed(HASHED_SALTED_SHA, self._password)
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

    def delete(self):
        result = False
        dn = Config.LDAP_DN.replace(Config.LDAP_UID, self._uid)
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

    def modify(self):
        result = False
        dn = Config.LDAP_DN.replace(Config.LDAP_UID, self._uid)
        none_attributes = self._none_attributes()
        if len(none_attributes) != 0:
            attrs = ', '.join([_ for _ in none_attributes])
            msg = 'The following user attributes are None: {0}'.format(attrs)
            raise AttributeError(msg)
        self._cn = self._gn + ' ' + self._sn
        attributes = {
            'givenName': [(MODIFY_REPLACE, [self._gn])],
            'sn': [(MODIFY_REPLACE, [self._sn])],
            'cn':  [(MODIFY_REPLACE, [self._cn])],
            'mail': [(MODIFY_REPLACE, [self._email])]
            }
        server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
        try:
            if self._valid_password(): # User must authenticate
                conn = Connection(server=server, user=Config.LDAP_ADMIN,
                                  password=Config.LDAP_ADMIN_PASSWORD,
                                  auto_bind=True, receive_timeout=30)
                result = conn.modify(dn, attributes)
                conn.unbind()
        except Exception as e:
            logger.error(e)
        return result

    def reset_password(self):
        result = False
        dn = Config.LDAP_DN.replace(Config.LDAP_UID, self._uid)
        user_password = {'userPassword': [
            (MODIFY_REPLACE, [hashed(HASHED_SALTED_SHA, self._password)])]}
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

    def _load_attributes(self):
        result = False
        dn = Config.LDAP_DN.replace(Config.LDAP_UID, self._uid)
        attributes = ['givenName', 'sn', 'mail']
        filter = '(&(objectclass=inetOrgPerson)(uid={uid}))'.format(uid=self._uid)
        server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
        try:
            conn = Connection(server=server, user=Config.LDAP_ADMIN,
                              password=Config.LDAP_ADMIN_PASSWORD,
                              auto_bind=True, receive_timeout=30)
            if conn.search(dn, filter, attributes=attributes):
                entry = conn.entries[0]
                self._gn = entry['givenName'].values[0]
                self._sn = entry['sn'].values[0]
                self._email = entry['mail'].values[0]
                self._cn = self._gn + ' ' + self._sn
                result = True
            conn.unbind()
        except Exception as e:
            logger.error(e)
        return result


    def _none_attributes(self):
        none_attributes = []
        if self._uid is None: none_attributes.append('uid')
        if self._gn is None: none_attributes.append('gn')
        if self._sn is None: none_attributes.append('sn')
        if self._email is None: none_attributes.append('email')
        return none_attributes

    def _random_password(self):
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        password = ''.join(random.choice(chars) for x in range(24))
        return password

    def _valid_password(self):
        result = False
        dn = Config.LDAP_DN.replace(Config.LDAP_UID, self._uid)
        server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
        try:
            conn = Connection(server=server, user=dn, password=self._password,
                              auto_bind=True, receive_timeout=30)
            result = True
            conn.unbind()
        except Exception as e:
            logger.error(e)
        return result


class LdapError(Exception):
    pass

class UidError(LdapError):
    pass

class AttributeError(LdapError):
    pass


def main():
    return 0


if __name__ == "__main__":
    main()
