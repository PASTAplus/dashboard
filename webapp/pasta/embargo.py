#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: embargo

:Synopsis:

:Author:
    servilla

:Created:
    9/9/21
"""
import daiquiri

import webapp.db as db
from webapp.config import Config

logger = daiquiri.getLogger(__name__)


class Embargo:
    def __init__(self, pid: str):
        self._pid = pid
        if len(self._pid.split('.')) == 3:
            self._scope, self._identifier, self._revision = self._pid.split('.')
        else:
            msg = f'pid "{pid}" not in canonical scope.identifier.revision form'
            raise ValueError(msg)
        self.resources = []

    def _get_package_acl(self):
        sql = (
            "SELECT resource_id, principal, access_type, access_order, permission "
            "FROM datapackagemanager.access_matrix WHERE resource_id LIKE "
            f"'%%/package/data/eml/{self._scope}/{self._identifier}/{self._revision}/%%'"
            "AND principal='public' ORDER BY resource_id ASC;"
        )
        rs = db.select_all(Config.DB_HOST_PACKAGE, sql)
        return rs

    def get_status(self) -> list:
        for r in self._get_package_acl():
            self.resources.append(r)
        return self.resources

    def set_embargo(self):
        sql = (
            "UPDATE datapackagemanager.access_matrix SET access_type='deny' WHERE resource_id LIKE "
            f"'%%/package/data/eml/{self._scope}/{self._identifier}/{self._revision}/%%'"
            "AND principal='public';"
        )
        rs = db.update(Config.DB_HOST_PACKAGE, sql)

    def clear_embargo(self):
        sql = (
            "UPDATE datapackagemanager.access_matrix SET access_type='allow' WHERE resource_id LIKE "
            f"'%%/package/data/eml/{self._scope}/{self._identifier}/{self._revision}/%%'"
            "AND principal='public';"
        )
        rs = db.update(Config.DB_HOST_PACKAGE, sql)
