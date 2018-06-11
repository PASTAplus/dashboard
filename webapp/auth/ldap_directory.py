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
import daiquiri

from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPCursorError

from webapp.config import Config

logger = daiquiri.getLogger('ldap_user: ' + __name__)

#
# Class to search the LDAP directory for users
#
class LdapDirectory(object):

    def __init__(self):
        pass

    def list_ldap_users(self):
        results = []
        server = Server(Config.LDAP, use_ssl=True, get_info=ALL)

        try:
            conn = Connection(server=server, user=Config.LDAP_ADMIN,
                              password=Config.LDAP_ADMIN_PASSWORD,
                              auto_bind=True, receive_timeout=30)
            conn.search('dc=edirepository,dc=org', '(objectclass=person)')
            for e in sorted(conn.entries):
                results.append(e.entry_dn)
            conn.unbind()
        except Exception as e:
            logger.error(e)
        return results


def main():
    return 0


if __name__ == "__main__":
    main()
