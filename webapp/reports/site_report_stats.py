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
                f'&fl=id,packageid,title,doi,author,pubdate,funding,'
                f'begindate,enddate,singledate,keyword&sort=id,asc'
                f'&debug=false')

    r = requests.get(solr_url)
    if r.status_code == requests.codes.ok:
        solr_result_set = r.text.encode('utf-8')
        root = etree.fromstring(solr_result_set)
        rows = root.attrib["numFound"]
        solr_url = f'{solr_url}&rows={rows}'
    else:
        msg = f'A request to PASTA for a solr query of {scope} failed with ' \
              + 'a {r.status_code} code.'
        logger.error(msg)

    r = requests.get(solr_url)
    if r.status_code == requests.codes.ok:
        r.encoding = "utf-8"
        solr_result_set = r.text.encode('utf-8')
        root = etree.fromstring(solr_result_set)
        docs = root.findall(".//document")
        for doc in docs:
            pid_info = dict()
            pid = (doc.find(".//packageid")).text.strip()
            id = pid.split(".")[1]
            title = (doc.find(".//title")).text.strip()
            doi = (doc.find(".//doi")).text
            if doi is not None:
                doi = doi.strip()
            else:
                doi = ""
            funding = (doc.find(".//funding")).text
            if funding is not None:
                funding = funding.strip()
            else:
                funding = ""
            pubdate = (doc.find(".//pubdate")).text
            if pubdate is not None:
                pubdate = pubdate.strip()
            else:
                pubdate = ""
            single_dates = doc.findall(".//singledate")
            if single_dates is not None:
                single_dates = "; ".join([_.text.strip() for _ in single_dates])
            begin_date = (doc.find(".//begindate")).text
            if begin_date is not None:
                begin_date = begin_date.strip()
            else:
                begin_date = ""
            end_date = (doc.find(".//enddate")).text
            if end_date is not None:
                end_date = end_date.strip()
            else:
                end_date = ""
            authors = doc.findall(".//author")
            if authors is not None:
                authors = "; ".join([_.text.strip() for _ in authors])
            keywords = doc.findall(".//keyword")
            if keywords is not None:
                keywords = ", ".join([_.text.strip() for _ in keywords])

            pid_info["pid"] = pid
            pid_info["id"] = int(id)
            pid_info["title"] = " ".join(title.split())
            pid_info["doi"] = doi.replace("doi:", "")
            pid_info["funding"] = " ".join(funding.split())
            pid_info["pubdate"] = pubdate
            pid_info["authors"] = authors.replace("\"", "'")
            pid_info["singledates"] = single_dates
            pid_info["begindate"] = begin_date
            pid_info["enddate"] = end_date
            pid_info["keywords"] = keywords

            solr_stats.append(pid_info)

    else:
        msg = f'A request to PASTA for a solr query of {scope} failed with ' \
              + 'a {r.status_code} code.'
        logger.error(msg)

    return sorted(solr_stats, key=itemgetter("id"))
