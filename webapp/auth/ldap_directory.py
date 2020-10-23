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

from ldap3 import Server, Connection, ALL, Reader, ObjectDef
from ldap3.core.exceptions import LDAPCursorError

from webapp.config import Config

logger = daiquiri.getLogger("ldap_user: " + __name__)


class LdapDirectory(object):
    def __init__(self):
        pass

    @staticmethod
    def list_ldap_users():
        users = dict()
        server = Server(Config.LDAP, use_ssl=True, get_info=ALL)
        person = ObjectDef('inetOrgPerson')
        try:
            with Connection(
                server=server,
                user=Config.LDAP_ADMIN,
                password=Config.LDAP_ADMIN_PASSWORD,
                auto_bind=True,
                receive_timeout=30,
            ) as conn:
                conn.search(
                    search_base="dc=edirepository,dc=org",
                    search_filter="(objectclass=person)",
                    attributes=["cn", "sn", "uid", "givenName", "mail"]
                )
                for e in sorted(conn.entries):
                    dn = e.entry_dn
                    user = {
                        "dn": e.entry_dn,
                        "cn": e.cn[0],
                        "sn": e.sn[0],
                        "givenName": e.givenName[0],
                        "mail": e.mail[0],
                    }
                    users[e.uid[0]] = user
        except Exception as e:
            logger.error(e)
        return users


def main():
    return 0


if __name__ == "__main__":
    main()
