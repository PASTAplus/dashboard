#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: package_tracker

:Synopsis:

:Author:
    servilla

:Created:
    1/6/19
"""
from urllib.parse import quote

from lxml import etree
import requests
import pendulum


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


def get_package_doi(pid: list, pasta_url: str, auth: tuple) -> str:
    url = pasta_url + f'/doi/eml/{pid[0]}/{pid[1]}/{pid[2]}'
    r = requests.get(url=url, auth=auth)
    if r.status_code == requests.codes.ok:
        return r.text
    else:
        return 'None'


def get_resource_create_date(resource_xml: str) -> str:
    root = etree.fromstring(resource_xml.encode('utf-8'))
    date_created = root.find('.//dateCreated')
    return date_created.text


def get_resource_metadata(pid: list, pasta_url: str, auth: tuple) -> str:
    url = pasta_url + f'/rmd/eml/{pid[0]}/{pid[1]}/{pid[2]}'
    r = requests.get(url=url, auth=auth)
    r.raise_for_status()
    return r.text


def get_resources(pid: list, pasta_url: str, auth: tuple) -> tuple:
    url = pasta_url + f'/eml/{pid[0]}/{pid[1]}/{pid[2]}'
    r = requests.get(url=url, auth=auth)
    if r.status_code == requests.codes.ok:
        return True, r.text
    elif r.status_code == requests.codes.not_found:
        return False, 'Not Found'
    elif r.status_code == requests.codes.unauthorized:
        return False, 'Unauthorized'
    else:
        return False, f'Unknown error with status code: {r.status_code}'


def is_real_package(pid: list, pasta_url: str, auth: tuple):
    is_real = False
    url = pasta_url + f'/rmd/eml/{pid[0]}/{pid[1]}/{pid[2]}'
    r = requests.get(url=url, auth=auth)
    if r.status_code == requests.codes.ok:
        is_real = True
    return is_real


class PackageStatus(object):

    def __init__(self, package_identifier: str):
        self._package_identifier = package_identifier.strip()
        self._pid = self._package_identifier.split('.')
        self._pasta_url = 'https://pasta.lternet.edu/package'
        self._auth = None
        self._is_real = is_real_package(self._pid, self._pasta_url, self._auth)
        if self._is_real:
            self._date_created_mt, self._date_created_utc = self.get_pasta_create_date()
            self._package_resources = self.get_pasta_resources()
            self._gmn_url = self.get_gmn_url()
            self._gmn_resources = self.get_gmn_resource_times()
            self._cn_url = 'https://cn.dataone.org/cn/v2'
            self._cn_sync_times = self.get_cn_sync_times()
            self._cn_index_status = self.get_cn_indexed_status()

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

    def get_cn_sync_times(self):
        resources = dict()
        for resource in self._package_resources:
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
        for resource in self._package_resources:
            if 'metadata/eml' in resource:
                break
            success, response = get_d1_solr_result(resource, self._cn_url)
            if success:
                solr_count = get_d1_solr_count(response)
                if solr_count >= 1:
                    status = True
        return status

    def get_gmn_resource_times(self):
        resources = dict()
        for resource in self._package_resources:
            success, response = get_d1_sysmeta(resource, self._gmn_url)
            if success:
                dt_utc = pendulum.parse(get_d1_date_uploaded(response))
                date_uploaded = dt_utc.to_iso8601_string()
                resources[resource] = date_uploaded
            else:
                resources[resource] = response
        return resources

    def get_gmn_url(self):
        if self._pid[0] == 'edi':
            gmn_host = 'edirepository.org'
        else:
            gmn_host = 'lternet.edu'

        return f'https://gmn.{gmn_host}/mn/v2'


    def get_pasta_create_date(self):
        xml = get_resource_metadata(self._pid, self._pasta_url, self._auth)
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
        success, response = get_resources(self._pid, self._pasta_url,
                                          self._auth)
        if success:
            resources = response.strip().split('\n')
            resources[-1] = get_package_doi(self._pid, self._pasta_url,
                                            self._auth)
        return resources
