#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: upload_stats

:Synopsis:

:Author:
    servilla

:Created:
    6/25/18
"""
from datetime import datetime
import uuid

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import pendulum
from sqlalchemy import create_engine

from webapp.config import Config


class UploadStats(object):

    def __init__(self, hours_in_past):
        self._hours_in_past = hours_in_past
        self._now = pendulum.now()
        self._result_set = self._get_recent_past()

    @property
    def now_as_integer(self):
        return self._now.int_timestamp

    @property
    def result_set(self):
        return self._result_set


    def _get_recent_past(self):

        db = Config.DB_DRIVER + '://' + \
             Config.DB_USER + ':' + \
             Config.DB_PW + '@' + \
             Config.DB_HOST + '/' + \
             Config.DB_DB

        connection = create_engine(db)

        _ = ('select datapackagemanager.resource_registry.package_id,'
               'datapackagemanager.resource_registry.date_created from '
               'datapackagemanager.resource_registry where date_created > '
               '\'TIME_IN_PAST\''
               ' and resource_type=\'dataPackage\' '
               'order by date_created desc')

        now = pendulum.now()
        past = now.subtract(hours=self._hours_in_past)
        sql = _.replace('TIME_IN_PAST', past.to_iso8601_string())
        result_set = connection.execute(sql).fetchall()

        return result_set


    def plot(self, file_name):
        now = self._now
        _ = pendulum.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour)

        dt_tbl = {}
        for hour in range(self._hours_in_past):
            dt_tbl[_.subtract(hours=hour)] = 0

        for result in self._result_set:
            p = pendulum.instance(result[1])
            _ = pendulum.datetime(year=p.year, month=p.month, day=p.day, hour=p.hour)
            dt_tbl[_] += 1

        dt = []
        count = []
        for _ in dt_tbl:
            dt.append(datetime.strptime(_.to_datetime_string(), '%Y-%m-%d %H:%M:%S'))
            count.append(dt_tbl[_])


        plt.plot(dt, count, 'g')
        plt.xlabel('Date')
        plt.ylabel('Uploads')
        plt.gca().set_ylim(bottom=0.0)
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        if sum(count) == 0:
            plt.gca().set_yticks([0.0,1.0])
        plt.gca().grid(True)
        plt.gcf().autofmt_xdate()
        plt.savefig(file_name)
        plt.close()