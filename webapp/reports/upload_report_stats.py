#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: upload_report

:Synopsis:

:Author:
    servilla

:Created:
    8/1/19
"""
from datetime import date

import daiquiri
from lxml import etree
import requests
from sqlalchemy import create_engine

from webapp.config import Config
import webapp.db as db

logger = daiquiri.getLogger('upload_report_stats: ' + __name__)


def upload_report_stats(scope: str, start_date: date, end_date: date) -> list:
    _ = ('select datapackagemanager.resource_registry.package_id,'
         'datapackagemanager.resource_registry.doi,'
         'datapackagemanager.resource_registry.date_created '
         'from datapackagemanager.resource_registry where date_created >= '
         '\'START_DATE\' and date_created <= \'END_DATE 24:00\' and '
         'scope=\'SCOPE\' and resource_type=\'dataPackage\' '
         'order by date_created asc')

    sql = _.replace('SCOPE', scope). \
        replace('START_DATE', start_date.isoformat()). \
        replace('END_DATE', end_date.isoformat())

    rs = db.select_all(Config.DB_HOST_PACKAGE, sql)
    return rs


def get_package_title(pid: str) -> str:
    title = ""
    package_path = pid.replace('.', '/')
    eml_url = f'{Config.PASTA_URL}/metadata/eml/{package_path}'
    r = requests.get(eml_url)
    if r.status_code == requests.codes.ok:
        eml = r.text.encode('utf-8')
        root = etree.fromstring(eml)
        title = flatten(root.find('.//title'))
    else:
        msg = f'A request to PASTA for {pid} failed with a {r.status_code} code.'
        logger.error(msg)
    return title


def get_scopes() -> list:
    scopes = []
    scope_url = f'{Config.PASTA_URL}/eml'
    try:
        r = requests.get(scope_url)
        if r.status_code == requests.codes.ok:
            scopes = [_.strip() for _ in r.text.split("\n")]
            for too_big in ('ecotrends', 'lter-landsat', 'lter-landsat-ledaps'):
                if too_big in scopes:
                    scopes.remove(too_big)
        else:
            msg = f'A request to PASTA for scopes failed with a {r.status_code} code.'
            logger.error(msg)
    except requests.exceptions.ConnectionError as e:
        logger.error(e)
    return scopes


def get_scope_count(scope: str) -> int:
    sql = ('select count(datapackagemanager.resource_registry.package_id) '
           'from datapackagemanager.resource_registry where '
           f'datapackagemanager.resource_registry.scope=\'{scope}\' and '
           'datapackagemanager.resource_registry.resource_type=\'dataPackage\'')

    rs = db.select_one(Config.DB_HOST_PACKAGE, sql)
    return rs[0]


def flatten(element):
    t = ''
    if hasattr(element, 'text'):
        t += element.text
    if hasattr(element, '__iter__'):
        for e in element:
            t += flatten(e)
    return t


def solr_report_stats(scope: str, rows: int) -> dict:
    solr_stats = dict()
    solr_url = ('https://pasta.lternet.edu/package/search/eml?'
                f'defType=edismax&q=*:*&fq=scope:({scope})'
                f'&fl=packageid,title&debug=false&rows={rows}')

    r = requests.get(solr_url)
    if r.status_code == requests.codes.ok:
        solr_result_set = r.text.encode('utf-8')
    else:
        logger.error(f'A request to PASTA for a solr query of {scope} failed with a {r.status_code} code.')
        return solr_stats

    root = etree.fromstring(solr_result_set)
    docs = root.findall(".//document")
    for doc in docs:
        pid = (doc.find(".//packageid")).text
        title = (doc.find(".//title")).text
        solr_stats[pid] = title

    return solr_stats
