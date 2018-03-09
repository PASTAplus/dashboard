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
import requests

from webapp import login
from webapp.config import Config

logger = daiquiri.getLogger('user.py: ' + __name__)

class User(UserMixin):

    def __init__(self, auth_token=None):
        self.auth_token = auth_token

    @staticmethod
    def authenticate(user_id=None, password=None):
        auth_token = None
        r = requests.get(Config.PASTA_URL, auth=(user_id, password))
        if r.status_code == requests.codes.ok:
            auth_token = r.cookies['auth-token']
        return auth_token

    def get_id(self):
        return self.auth_token


@login.user_loader
def load_user(id):
    auth_token = id
    return User(auth_token=id)