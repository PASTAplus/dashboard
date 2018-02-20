# -*- coding: utf-8 -*-

""":Mod: __init__

:Synopsis:

:Author:
    servilla

:Created:
    2/15/18
"""
from flask import Flask
from dashboard.users.views import users

app = Flask(__name__)
app.register_blueprint(users, url_prefix='/dashboard/users')