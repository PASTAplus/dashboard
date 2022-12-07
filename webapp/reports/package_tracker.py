#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: package_tracker

:Synopsis:

:Author:
    servilla

:Created:
    1/6/19
"""
from datetime import datetime
from dateutil import tz
from pathlib import Path
from typing import List
from urllib.parse import quote

import daiquiri
from lxml import etree
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pendulum
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

from webapp.config import Config
import webapp.db as db


logger = daiquiri.getLogger(__name__)
ABQ_TZ = tz.gettz("America/Denver")


def clean(text):
    return " ".join(text.split())


def get_d1_date_uploaded(sysmeta_xml: str) -> str:
    root = etree.fromstring(sysmeta_xml.encode('utf-8'))
    date_uploaded = root.find('.//dateUploaded')
    return date_uploaded.text


def get_d1_date_replica_verified(sysmeta_xml: str) -> str:
    root = etree.fromstring(sysmeta_xml.encode('utf-8'))
    date_verified = root.find('.//replicaVerified')
    return date_verified.text


def get_d1_solr_count(solr_xml: str) -> int:
    root = etree.fromstring(solr_xml.encode('utf-8'))
    result = root.find('.//result')
    return int(result.get('numFound'))


def get_d1_solr_result(pid: str, d1_url: str) -> tuple:
    pid = quote(f'"{pid}"', safe='')
    url = f'{d1_url}/query/solr/?start=0&rows=10&fl=id%2Ctitle%2CformatId&q=id%3A{pid}'
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        return True, r.text
    elif r.status_code == requests.codes.not_found:
        return False, 'Not Found'
    elif r.status_code == requests.codes.unauthorized:
        return False, 'Unauthorized'
    else:
        return False, f'Unknown error with status code: {r.status_code}'


def get_d1_sysmeta(pid: str, d1_url: str) -> tuple:
    pid = quote(pid, safe='')
    url = f'{d1_url}/meta/{pid}'
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        return True, r.text
    elif r.status_code == requests.codes.not_found:
        return False, 'Not Found'
    elif r.status_code == requests.codes.unauthorized:
        return False, 'Unauthorized'
    else:
        return False, f'Unknown error with status code: {r.status_code}'


def get_resource_counts(rid: str, start: str = None, end: str = None) -> int:
    sql = (
        "SELECT COUNT(*) FROM auditmanager.eventlog "
        "WHERE servicemethod='<SERVICE_METHOD>' AND statuscode=200 "
        "AND userid NOT LIKE '%%robot%%' AND resourceid='<RID>'"
    )

    if "/metadata/eml/" in rid:
        service_method = "readMetadata"
    elif "/report/eml/" in rid:
        service_method = "readDataPackageReport"
    else:
        service_method = "readDataEntity"

    sql = sql.replace("<SERVICE_METHOD>", service_method)
    sql = sql.replace("<RID>", rid.replace("%", "%%"))

    if start is not None:
        sql += f" AND entrytime >= '{start}'"

    if end is not None:
        sql += f" AND entrytime <= '{end}'"

    rs = db.select_all(Config.DB_HOST_AUDIT, sql)
    return rs[0][0]


def get_resource_downloads(rid: str, start: str = None, end: str = None):
    sql = (
        "SELECT entrytime FROM auditmanager.eventlog "
        "WHERE servicemethod='<SERVICE_METHOD>' AND statuscode=200 "
        "AND userid NOT LIKE '%%robot%%' AND resourceid='<RID>' "
    )

    if "/metadata/eml/" in rid:
        service_method = "readMetadata"
    elif "/report/eml/" in rid:
        service_method = "readDataPackageReport"
    else:
        service_method = "readDataEntity"

    sql = sql.replace("<SERVICE_METHOD>", service_method)
    sql = sql.replace("<RID>", rid.replace("%", "%%"))

    if start is not None:
        sql += f"AND entrytime >= '{start}' "

    if end is not None:
        sql += f"AND entrytime <= '{end}' "

    sql += "ORDER BY entrytime ASC"

    rs = db.select_all(Config.DB_HOST_AUDIT, sql)
    return rs


def get_entity_name(dataset, rid: str):
    name = None
    urls = dataset.findall("./physical/distribution/online/url")
    for url in urls:
        if rid == url.text.strip():
            name = dataset.find("./entityName").text.strip()
            break
    return name


def get_package_doi(pid: list, auth: tuple = None) -> str:
    url = Config.PASTA_URL + f'/doi/eml/{pid[0]}/{pid[1]}/{pid[2]}'
    r = requests.get(url=url, auth=auth)
    if r.status_code == requests.codes.ok:
        return r.text
    else:
        return 'None'


def get_resource_create_date(resource_xml: str) -> str:
    root = etree.fromstring(resource_xml.encode('utf-8'))
    date_created = root.find('.//dateCreated')
    return date_created.text


def get_package_eml(pid: list, auth: tuple = None) -> str:
    url = Config.PASTA_URL + f'/metadata/eml/{pid[0]}/{pid[1]}/{pid[2]}'
    r = requests.get(url=url, auth=auth)
    r.raise_for_status()
    return r.text


def get_resource_metadata(pid: list, auth: tuple = None) -> str:
    url = Config.PASTA_URL + f'/rmd/eml/{pid[0]}/{pid[1]}/{pid[2]}'
    r = requests.get(url=url, auth=auth)
    r.raise_for_status()
    return r.text


def get_resources(pid: list, auth: tuple = None) -> tuple:
    url = Config.PASTA_URL + f'/eml/{pid[0]}/{pid[1]}/{pid[2]}'
    r = requests.get(url=url, auth=auth)
    if r.status_code == requests.codes.ok:
        return True, r.text
    elif r.status_code == requests.codes.not_found:
        return False, 'Not Found'
    elif r.status_code == requests.codes.unauthorized:
        return False, 'Unauthorized'
    else:
        return False, f'Unknown error with status code: {r.status_code}'


def is_real_package(pid: list, auth: tuple = None):
    is_real = False
    url = Config.PASTA_URL + f'/rmd/eml/{pid[0]}/{pid[1]}/{pid[2]}'
    r = requests.get(url=url, auth=auth)
    if r.status_code == requests.codes.ok:
        is_real = True
    return is_real


def plot(stats: List) -> str:
    first_download = stats[0][0]
    now = pendulum.now()
    delta = now - first_download.astimezone(tz=ABQ_TZ)
    days = int(delta.total_days())
    _ = pendulum.datetime(
        year=now.year, month=now.month, day=now.day
    )

    dt_tbl = {}
    for day in range(days + 2):
        dt_tbl[_.subtract(days=day)] = 0

    for result in stats:
        p = pendulum.instance(result[0])
        _ = pendulum.datetime(year=p.year, month=p.month, day=p.day)
        dt_tbl[_] += 1

    dt = []
    count = []
    for _ in dt_tbl:
        dt.append(datetime.strptime(_.to_datetime_string(), "%Y-%m-%d %H:%M:%S"))
        count.append(dt_tbl[_])

    p = Path(Config.STATIC)
    if not p.exists():
        p.mkdir(parents=True)

    file_name = f"{now.timestamp()}.png"
    file_path = p / file_name

    plt.figure(figsize=(8.0, 2.4), tight_layout=True)
    plt.plot(dt, count, "g")
    # plt.xlabel("Date")
    plt.ylabel("Downloads")
    plt.gca().set_ylim(bottom=0.0)
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    if sum(count) == 0:
        plt.gca().set_yticks([0.0, 1.0])
    plt.gca().grid(True)
    plt.gcf().autofmt_xdate()
    plt.savefig(file_path)
    plt.close()

    return f"/static/{file_name}"


def query(host: str, sql: str):
    rs = None
    db = (
        f"{Config.DB_DRIVER}://"
        f"{Config.DB_USER}:"
        f"{Config.DB_PW}@"
        f"{host}/"
        f"{Config.DB_DB}"
    )
    engine = create_engine(db)
    try:
        with engine.connect() as connection:
            rs = connection.execute(sql).fetchall()
    except NoResultFound as e:
        logger.warning(e)
        rs = list()
    except Exception as e:
        logger.error(sql)
        logger.error(e)
        raise e
    return rs


class PackageStatus(object):

    def __init__(self, package_identifier: str):
        self._package_identifier = package_identifier.strip()
        self._pid = self._package_identifier.split('.')
        self._is_real = is_real_package(self._pid)
        if self._is_real:
            eml = get_package_eml(self._pid)
            self._eml = etree.fromstring(eml.encode("utf-8"))
            self._date_created_mt, self._date_created_utc = self.get_pasta_create_date()
            self._package_resources = self.get_pasta_resources()
            self._package_resource_downloads = self.get_resource_downloads()
            self._gmn_host = self.get_gmn_host()
            self._gmn_url = self.get_gmn_url()
            self._gmn_resources = self.get_gmn_resource_times()
            self._cn_url = 'https://cn.dataone.org/cn/v2'
            self._cn_sync_times = self.get_cn_sync_times()
            self._cn_index_status = self.get_cn_indexed_status()
            self._title = self._get_title()


    @property
    def title(self):
        return self._title

    @property
    def cn_index_status(self):
        return self._cn_index_status

    @property
    def cn_sync_times(self):
        return self._cn_sync_times

    @property
    def cn_url(self):
        return self._cn_url

    @property
    def date_created_mt(self):
        return self._date_created_mt

    @property
    def date_created_utc(self):
        return self._date_created_utc

    @property
    def gmn_resources(self):
        return self._gmn_resources

    @property
    def gmn_host(self):
        return self._gmn_host

    @property
    def gmn_url(self):
        return self._gmn_url

    @property
    def is_real(self):
        return self._is_real

    @property
    def package_identifier(self):
        return self._package_identifier

    @property
    def package_resources(self):
        return self._package_resources

    @property
    def resource_downloads(self):
        return self._package_resource_downloads

    def get_cn_sync_times(self):
        resources = dict()
        for resource in self._package_resources[:-1]:
            success, response = get_d1_sysmeta(resource, self._cn_url)
            if success:
                dt_utc = pendulum.parse(get_d1_date_replica_verified(response))
                date_verified = dt_utc.to_iso8601_string()
                resources[resource] = date_verified
            else:
                resources[resource] = response
        return resources

    def get_cn_indexed_status(self):
        status = False
        for resource in self._package_resources[:-1]:
            if 'metadata/eml' in resource:
                break
            success, response = get_d1_solr_result(resource, self._cn_url)
            if success:
                solr_count = get_d1_solr_count(response)
                if solr_count >= 1:
                    status = True
        return status

    def _get_title(self) -> str:
        title = clean(self._eml.find("./dataset/title").xpath("string()"))
        return title

    def get_gmn_resource_times(self):
        resources = dict()
        for resource in self._package_resources[:-1]:
            success, response = get_d1_sysmeta(resource, self._gmn_url)
            if success:
                dt_utc = pendulum.parse(get_d1_date_uploaded(response))
                date_uploaded = dt_utc.to_iso8601_string()
                resources[resource] = date_uploaded
            else:
                resources[resource] = response
        return resources

    def get_gmn_host(self):
        if self._pid[0] == 'edi':
            gmn_host = 'EDI'
        else:
            gmn_host = 'LTER'
        return gmn_host

    def get_gmn_url(self):
        if self._pid[0] == 'edi':
            gmn_host = 'edirepository.org'
        else:
            gmn_host = 'lternet.edu'
        return f'https://gmn.{gmn_host}/mn/v2'

    def get_pasta_create_date(self):
        xml = get_resource_metadata(self._pid)
        date_created_raw = get_resource_create_date(xml)
        local_tz = 'America/Denver'
        utc_tz = pendulum.timezone('UTC')
        dt_mt = pendulum.parse(date_created_raw, tz=local_tz)
        dt_utc = pendulum.instance(utc_tz.convert(dt_mt))
        date_created_mt = dt_mt.to_iso8601_string()
        date_created_utc = pendulum.parse(
            dt_utc.to_iso8601_string()).to_iso8601_string()
        return date_created_mt, date_created_utc

    def get_pasta_resources(self):
        resources = list()
        success, response = get_resources(self._pid)
        if success:
            resources = response.strip().split('\n')
            resources.append(resources[-1])
            resources[-2] = get_package_doi(self._pid)
        return resources

    def get_resource_downloads(self):
        resource_downloads = dict()
        for resource in self._package_resources[:-2]:
            count = get_resource_counts(resource)
            if count > 0:
                series = get_resource_downloads(resource)
                plot_name = plot(series)
                if "/data/eml/" in resource:
                    name = self.get_entity_name(resource)
                elif "/metadata/eml/" in resource:
                    name = "EML Metadata"
                elif "/report/eml/" in resource:
                    name = "Quality Report"
                else:
                    name = ""
                resource_downloads[resource] = (count, plot_name, name)
        return resource_downloads

    def get_entity_name(self, rid: str) -> str:
        name = None
        datatables = self._eml.findall("./dataset/dataTable")
        for datatable in datatables:
            name = get_entity_name(datatable, rid)
            if name is not None: return name
        otherentities = self._eml.findall("./dataset/otherEntity")
        for otherentity in otherentities:
            name = get_entity_name(otherentity, rid)
            if name is not None: return name
        spatialrasters = self._eml.findall("./dataset/spatialRaster")
        for spatialraster in spatialrasters:
            name = get_entity_name(spatialraster, rid)
            if name is not None: return name
        spatialvectors = self._eml.findall("./dataset/spatialVector")
        for spatialvector in spatialvectors:
            name = get_entity_name(spatialvector, rid)
        return name

