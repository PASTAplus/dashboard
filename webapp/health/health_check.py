#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: health_check

:Synopsis:

:Author:
    servilla

:Created:
    3/20/18
"""
import daiquiri
import pendulum

from soh.config import Config as soh_Config
from soh.model.soh_db import SohDb

logger = daiquiri.getLogger('health_check.py: ' + __name__)

status_code = {
    'text_muted': ['text-muted', 'no status'],
    'text_success': ['text-success', 'ok'],
    'text_info': ['text-info', 'info'],
    'text_warning': ['text-warning', 'warning'],
    'text_danger': ['text-danger', 'problem']
}

production_servers = [soh_Config.servers['PASTA'],
                      soh_Config.servers['PACKAGE'],
                      soh_Config.servers['AUDIT'],
                      soh_Config.servers['SOLR']]

staging_servers = [soh_Config.servers['PASTA_S'],
                   soh_Config.servers['PACKAGE_S'],
                   soh_Config.servers['AUDIT_S'],
                   soh_Config.servers['SOLR_S']]

development_servers = [soh_Config.servers['PASTA_D'],
                       soh_Config.servers['PACKAGE_D'],
                       soh_Config.servers['AUDIT_D'],
                       soh_Config.servers['SOLR_D']]

tiers = {
    'PRODUCTION': ['Production', '', production_servers],
    'STAGING': ['Staging', '-s', staging_servers],
    'DEVELOPMENT': ['Development', '-d', development_servers]
}


class SystemState:

    def __init__(self):
        self._state = {}
        self._event_id = None
        self._event_timestamp = None
        # Initialize server state
        self._set_state()

    def _set_state(self):
        soh_db = SohDb()
        soh_db.connect_soh_db()
        event_id_query = soh_db.get_soh_latest_event()
        if event_id_query:
            self._event_id = event_id_query.event_id
            self._event_timestamp = event_id_query.timestamp
            servers = soh_db.get_soh_status_by_event(event_id=self._event_id)
            for server in servers:
                self._state[server.server] = int(server.status)
    @property
    def state(self):
        return self._state

    def server_assertions(self, host=None):
        assertions = {}
        server_type = None
        if host in soh_Config.server_types['APACHE']:
            server_type = 'APACHE'
        elif host in soh_Config.server_types['APACHE_TOMCAT']:
            server_type = 'APACHE_TOMCAT'
        elif host in soh_Config.server_types['AUDIT']:
            server_type = 'AUDIT'
        elif host in soh_Config.server_types['AUTH']:
            server_type = 'AUTH'
        elif host in soh_Config.server_types['GMN']:
            server_type = 'GMN'
        elif host in soh_Config.server_types['JETTY']:
            server_type = 'JETTY'
        elif host in soh_Config.server_types['LDAP']:
            server_type = 'LDAP'
        elif host in soh_Config.server_types['PACKAGE']:
            server_type = 'PACKAGE'
        elif host in soh_Config.server_types['PORTAL']:
            server_type = 'PORTAL'
        elif host in soh_Config.server_types['SERVER']:
            server_type = 'SERVER'
        elif host in soh_Config.server_types['SOLR']:
            server_type = 'SOLR'
        elif host in soh_Config.server_types['TOMCAT']:
            server_type = 'TOMCAT'

        if host in self._state and server_type is not None:
            for assertion in soh_Config.server_assertions[server_type]:
                assertions[assertion] = self._state[host] & \
                                        soh_Config.assertions[assertion]
        return assertions

    def server_state(self, host=None):
        if host in self._state:
            return self._state[host]
        else:
            return None

    def server_status(self, host=None):
        status = status_code['text_muted']
        if host in self._state:
            if self._state[host] == soh_Config.UP:
                status = status_code['text_success']
            else:
                status = status_code['text_danger']
        return status

    def tier_state(self, tier=None):

        if tier not in tiers:
            raise NameError('{tier} not recognized'.format(tier=tier))

        state = 0
        for server in tiers[tier][2]:
            if server in self._state:
                state = state | self._state[server]
            else:
                return None

        return state

    def tier_status(self, tier=None):
        status = status_code['text_muted']
        state = self.tier_state(tier)
        if state is not None:
            if state == soh_Config.UP:
                status = status_code['text_success']
            else:
                status = status_code['text_danger']
        return status

    def timestamp(self, local=False):
        if local:
            tz = pendulum.now().timezone
            dt = pendulum.instance(self._event_timestamp)
            lt = dt.astimezone(tz)
            return lt.to_day_datetime_string()
        else:
            return self._event_timestamp

