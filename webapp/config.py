#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: config

:Synopsis:

:Author:
    servilla

:Created:
    3/6/18
"""

import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-aint-gonna-guess-it'
