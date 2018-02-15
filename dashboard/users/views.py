# -*- coding: utf-8 -*-

""":Mod: views

:Synopsis:

:Author:
    servilla

:Created:
    2/15/18
"""
from flask import Blueprint

users = Blueprint('users', __name__)


@users.route('/me')
def me():
    return "This is my page.", 200