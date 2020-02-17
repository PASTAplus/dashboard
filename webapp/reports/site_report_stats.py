#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: site_report_stats

:Synopsis:

:Author:
    servilla

:Created:
    2/15/20
"""
from operator import itemgetter

import daiquiri
from lxml import etree
import requests

from webapp.config import Config


logger = daiquiri.getLogger('site_report_stats: ' + __name__)


def get_site_report(scope: str) -> list:
    solr_stats = list()
    solr_url = ('https://pasta.lternet.edu/package/search/eml?'
                 f'defType=edismax&q=*:*&fq=scope:({scope})'
                 f'&fl=id,packageid,title,doi,author,pubdate&sort=id,asc'
                 f'&debug=false')

    r = requests.get(solr_url)
    if r.status_code == requests.codes.ok:
        solr_result_set = r.text.encode('utf-8')
        root = etree.fromstring(solr_result_set)
        rows = root.attrib["numFound"]
        solr_url = f'{solr_url}&rows={rows}'
    else:
        msg = f'A request to PASTA for a solr query of {scope} failed with ' + \
               'a {r.status_code} code.'
        logger.error(msg)

    r = requests.get(solr_url)
    if r.status_code == requests.codes.ok:
        r.encoding = "utf-8"
        solr_result_set = r.text.encode('utf-8')
        root = etree.fromstring(solr_result_set)
        docs = root.findall(".//document")
        for doc in docs:
            pid_info = dict()
            pid = (doc.find(".//packageid")).text
            pid_info["pid"] = pid
            id = pid.split(".")[1]
            pid_info["id"] = int(id)
            title = (doc.find(".//title")).text
            pid_info["title"] = " ".join(title.split())
            doi = (doc.find(".//doi")).text
            pid_info["doi"] = doi.replace("doi:", "https://doi.org/")
            pid_info["pubdate"] = (doc.find(".//pubdate")).text
            authors = doc.findall(".//author")
            if authors is not None:
                pid_info["authors"] = "; ".join([_.text for _ in authors])
            solr_stats.append(pid_info)
    else:
        msg = f'A request to PASTA for a solr query of {scope} failed with ' + \
               'a {r.status_code} code.'
        logger.error(msg)

    return sorted(solr_stats, key=itemgetter("id"))
