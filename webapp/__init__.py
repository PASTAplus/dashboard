# -*- coding: utf-8 -*-

""":Mod: __init__

:Synopsis:

:Author:
    servilla

:Created:
    2/15/18
"""
import logging
import os

import daiquiri
from flask import Flask

from webapp.config import Config
from webapp.auth.views import auth
from webapp.home.views import home
from webapp.users.views import users

cwd = os.path.dirname(os.path.realpath(__file__))
logfile = cwd + '/dashboard.log'
daiquiri.setup(level=logging.INFO, outputs=(daiquiri.output.File(logfile),
                                            'stdout',))
logger = daiquiri.getLogger(__name__)

app = Flask(__name__)

app.config.from_object(Config)

app.register_blueprint(auth, url_prefix='/dashboard/auth')
app.register_blueprint(home, url_prefix='/dashboard')
app.register_blueprint(users, url_prefix='/dashboard/users')
