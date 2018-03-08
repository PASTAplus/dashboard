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
from flask_login import LoginManager

from webapp import properties

cwd = os.path.dirname(os.path.realpath(__file__))
logfile = cwd + '/dashboard.log'
daiquiri.setup(level=logging.INFO,
               outputs=(daiquiri.output.File(logfile), 'stdout',))
logger = daiquiri.getLogger(__name__)

app = Flask(__name__)

login = LoginManager(app)

app.config.update(
    DEBUG=properties.DEBUG,
    SECRET_KEY=properties.SECRET_KEY
)

from webapp.auth.views import auth
app.register_blueprint(auth, url_prefix='/dashboard/auth')

from webapp.home.views import home
app.register_blueprint(home, url_prefix='/dashboard')
