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
from flask_login import login_required


home = Blueprint('home', __name__, template_folder='templates')

@home.route('/')
@home.route('/index')
def index():
    return render_template('index.html')
