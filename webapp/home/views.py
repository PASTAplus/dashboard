#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: views.py

:Synopsis:

:Author:
    servilla

:Created:
    3/6/18
"""
from flask import Blueprint, render_template, redirect, url_for

from soh.config import Config as soh_Config
from webapp.health.health_check import SystemState


home = Blueprint('home', __name__, template_folder='templates')


@home.route('/')
@home.route('/index')
def index():
    servers = soh_Config.servers
    system = SystemState()
    # return render_template('index.html', system=system, servers=servers)
    return redirect(url_for('health.glance'))

@home.route('/about')
def about():
    return render_template('about.html')