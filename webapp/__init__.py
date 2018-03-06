# -*- coding: utf-8 -*-

""":Mod: __init__

:Synopsis:

:Author:
    servilla

:Created:
    2/15/18
"""
from flask import Flask

from webapp.auth.views import auth
from webapp.home.views import home
from webapp.users.views import users

app = Flask(__name__)

app.register_blueprint(auth, url_prefix='/dashboard/auth')
app.register_blueprint(home, url_prefix='/dashboard')
app.register_blueprint(users, url_prefix='/dashboard/users')
