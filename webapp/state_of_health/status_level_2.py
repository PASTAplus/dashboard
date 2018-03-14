#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: status_level_2

:Synopsis:

:Author:
    servilla

:Created:
    3/14/18
"""

status_code = {
    'text_muted': ['text-muted', 'no status'],
    'text_success': ['text-success', 'success'],
    'text_info': ['text-info', 'info'],
    'text_warning': ['text-warning', 'warning'],
    'text_danger': ['text-danger', 'danger']
}

status = {
    'production': status_code['text_muted'],
    'staging': status_code['text_muted'],
    'development': status_code['text_muted'],
    'edi_portal': status_code['text_muted'],
    'edi_portal_s': status_code['text_muted'],
    'edi_portal_d': status_code['text_muted'],
    'lter_portal': status_code['text_muted'],
    'lter_portal_s': status_code['text_muted'],
    'lter_portal_d': status_code['text_muted'],
    'edi_gmn': status_code['text_muted'],
    'edi_gmn_s': status_code['text_muted'],
    'lter_gmn': status_code['text_muted'],
    'lter_gmn_s': status_code['text_muted'],
    'edi_ldap': status_code['text_muted'],
    'lter_ldap': status_code['text_muted'],
    'unit_registry': status_code['text_muted'],
    'controlled_vocabulary': status_code['text_muted'],
}