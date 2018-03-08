#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: user

:Synopsis:

:Author:
    servilla

:Created:
    3/7/18
"""

import daiquiri
from flask_login import UserMixin
from webapp import login

logger = daiquiri.getLogger('user.py: ' + __name__)

class User(UserMixin):

    @staticmethod
    def authenticate(user_id=None, password=None):
        return True