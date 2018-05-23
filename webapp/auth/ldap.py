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
from ldap3 import Server, Connection, ALL, HASHED_SALTED_SHA
from ldap3.utils.hashed import hashed

from config import Config

logger = daiquiri.getLogger('ldap: ' + __name__)


class LDAP(object):

    def __init__(self, uid=None):
        self._uid = uid

    def is_registered(self):
        search_result = False
        server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
        try:
            conn = Connection(server, auto_bind=True, receive_timeout=30)
            search_result = conn.search(Config.LDAP_BASE,
                                Config.LDAP_FILTER.replace('USER', self._uid))
        except Exception as e:
            logger.error(e)
        return search_result

    def add(self, gn=None, sn=None, email=None, passwd=None):
        add_result = False
        dn = 'uid=' + self._uid + ',o=EDI,dc=edirepository,dc=org'
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
            conn = Connection(server, Config.LDAP_ADMIN, Config.LDAP_ADMIN_PASSWORD, auto_bind=True, receive_timeout=30)
            add_result = conn.add(dn, ldap_class, attributes)
        except Exception as e:
            logger.error(e)
        return add_result


    def delete(self):
        pass

    def reset_password(self):
        pass

    def reset_email(self):
        pass



def main():
    return 0


if __name__ == "__main__":
    main()
