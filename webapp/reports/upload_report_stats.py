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
from sqlalchemy import create_engine

from webapp.config import Config


logger = daiquiri.getLogger('upload_report: ' + __name__)


def upload_report_stats(scope: str, start_date: date, end_date: date) -> list:

    db = Config.DB_DRIVER + '://' + \
         Config.DB_USER + ':' + \
         Config.DB_PW + '@' + \
         Config.DB_HOST + '/' + \
         Config.DB_DB

    connection = create_engine(db)

    _ = ('select datapackagemanager.resource_registry.package_id,'
         'datapackagemanager.resource_registry.doi,'
         'datapackagemanager.resource_registry.date_created '
         'from datapackagemanager.resource_registry where date_created >= '
         '\'START_DATE\' and date_created <= \'END_DATE\' and scope=\'SCOPE\' '
         'and resource_type=\'dataPackage\' '
         'order by date_created asc')

    sql = _.replace('SCOPE', scope).\
            replace('START_DATE', start_date.isoformat()).\
            replace('END_DATE', end_date.isoformat())

    try:
        result_set = connection.execute(sql).fetchall()
    except Exception as e:
        logger.ERROR(e)
        result_set = list()

    return result_set


def main():
    return 0


if __name__ == "__main__":
    main()
