#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: db

:Synopsis:

:Author:
    servilla

:Created:
    9/9/21
"""
import urllib.parse

import daiquiri
from sqlalchemy import create_engine
from sqlalchemy.engine import ResultProxy
from sqlalchemy.exc import NoResultFound
from sqlalchemy.exc import OperationalError

from webapp.config import Config

logger = daiquiri.getLogger(__name__)


def select(host: str, sql: str) -> ResultProxy:
    db = Config.DB_DRIVER + '://' + \
         Config.DB_USER + ':' + \
         urllib.parse.quote_plus(Config.DB_PW) + '@' + \
         host + '/' + \
         Config.DB_DB

    connection = create_engine(db)
    rs = None
    try:
        rs = connection.execute(sql).fetchall()
    except NoResultFound as ex:
        logger.warning(ex)
    except OperationalError as ex:
        logger.warning(ex)
    except Exception as ex:
        logger.error(ex)
        raise ex
    return rs


def update(host: str, sql: str):
    db = Config.DB_DRIVER + '://' + \
         Config.DB_USER + ':' + \
         urllib.parse.quote_plus(Config.DB_PW) + '@' + \
         host + '/' + \
         Config.DB_DB

    connection = create_engine(db)
    rs = None
    try:
        rs = connection.execute(sql)
    except NoResultFound as ex:
        logger.warning(ex)
    except OperationalError as ex:
        logger.warning(ex)
    except Exception as ex:
        logger.error(ex)
        raise ex
    return rs
