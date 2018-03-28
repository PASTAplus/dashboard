#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: views

:Synopsis:

:Author:
    servilla

:Created:
    3/24/18
"""
from flask import abort, Blueprint, render_template

from soh.config import Config as soh_Config
from webapp.health.health_check import SystemState
from webapp.health.health_check import tiers

health = Blueprint('health', __name__, template_folder='templates')


@health.route('/glance')
def glance():
    servers = soh_Config.servers
    system = SystemState()
    return render_template('glance.html', system=system, servers=servers)


@health.route('/server/<server>')
def server(server=None):
    servers = [soh_Config.servers[_] for _ in soh_Config.servers]
    if server in servers:
        system = SystemState()
        return render_template('server.html', system=system, server=server)
    else:
        abort(404)


@health.route('/tier/<tier>')
def tier(tier=None):
    if tier in tiers:
        system = SystemState()
        return render_template('tier.html', system=system, tier=tiers[tier])
    else:
        abort(404)