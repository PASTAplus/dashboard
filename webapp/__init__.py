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
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from webapp.config import Config

cwd = os.path.dirname(os.path.realpath(__file__))
logfile = cwd + '/dashboard.log'
daiquiri.setup(level=logging.INFO,
               outputs=(daiquiri.output.File(logfile), 'stdout',))
logger = daiquiri.getLogger(__name__)

app = Flask(__name__)

app.config.from_object(Config)

bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'auth.login'

from webapp.auth.views import auth
app.register_blueprint(auth, url_prefix='/dashboard/auth')

from webapp.home.views import home
app.register_blueprint(home, url_prefix='/dashboard')

from webapp.reports.views import reports
app.register_blueprint(reports, url_prefix='/dashboard/reports')

from webapp.pasta.views import pasta
app.register_blueprint(pasta, url_prefix='/dashboard/pasta')

from webapp.health.views import health
app.register_blueprint(health, url_prefix='/dashboard/health')
