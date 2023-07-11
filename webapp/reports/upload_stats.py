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
from pathlib import Path
from typing import List

import daiquiri
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pendulum
from pendulum import timezone
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

from webapp.config import Config
import webapp.db as db


logger = daiquiri.getLogger(__name__)


def get_recent_uploads(days: int, scope: str):
    sql = (
        "SELECT datapackagemanager.resource_registry.package_id,"
        "datapackagemanager.resource_registry.date_created FROM "
        "datapackagemanager.resource_registry WHERE "
        "resource_type='dataPackage' "
    )

    if scope is not None:
        sql += f"AND scope = '{scope}' "

    # mtn = timezone("America/Denver")
    # now = mtn.convert(pendulum.now())
    utc = timezone("UTC")
    now = utc.convert(pendulum.now())
    past = now.subtract(days=days)
    sql += f"AND date_created > '{past.to_iso8601_string()}' "
    sql += "ORDER BY date_created DESC"

    rs = db.select_all(Config.DB_HOST_PACKAGE, sql)

    return rs


def plot(days: int, stats: List):
    mtn = timezone("America/Denver")
    # now = mtn.convert(pendulum.now())
    utc = timezone("UTC")
    now = utc.convert(pendulum.now())
    _ = pendulum.datetime(
        year=now.year, month=now.month, day=now.day, hour=now.hour
    )

    dt_tbl = {}
    hours = days * 24
    for hour in range(hours + 2):
        dt_tbl[_.subtract(hours=hour)] = 0

    for result in stats:
        p = pendulum.instance(result[1])
        _ = pendulum.datetime(year=p.year, month=p.month, day=p.day, hour=p.hour)
        if _ in dt_tbl:
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

    plt.plot(dt, count, "g")
    plt.xlabel("Date")
    plt.ylabel("Uploads")
    plt.gca().set_ylim(bottom=0.0)
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    if sum(count) == 0:
        plt.gca().set_yticks([0.0, 1.0])
    plt.gca().grid(True)
    plt.gcf().autofmt_xdate()
    plt.savefig(file_path)
    plt.close()

    return file_name
