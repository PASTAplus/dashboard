#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: views.py

:Synopsis:

:Author:
    servilla

:Created:
    3/6/18
"""
from flask import Blueprint, render_template


from webapp.state_of_health import status_level_2


home = Blueprint('home', __name__, template_folder='templates')


@home.route('/')
@home.route('/index')
def index():
    return render_template('index.html', status =status_level_2.status)


@home.route('/about')
def about():
    return render_template('about.html')