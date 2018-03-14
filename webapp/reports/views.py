#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: views.py

:Synopsis:

:Author:
    Duane Costa

:Created:
    3/6/18
"""
import json

from flask import Blueprint, render_template
from flask_login import login_required

reports = Blueprint('reports', __name__, template_folder='templates')


@reports.route('/render_no_public', methods=['GET', 'POST'])
@login_required
def render_no_public():
    return render_report(report_type='no_public')


@reports.route('/render_offline', methods=['GET', 'POST'])
@login_required
def render_offline():
    return render_report(report_type='offline')


def render_report(report_type=None):
    if report_type:
        if report_type == 'no_public':
            metadata_resources, data_resources = load_no_public()
            return render_template('report_no_public.html', 
                                   metadata_resources=metadata_resources, 
                                   data_resources=data_resources)
        elif report_type == 'offline':
            offline_resources, unparsed_resources = load_offline()
            return render_template('report_offline.html', 
                                   offline_resources=offline_resources, 
                                   unparsed_resources=unparsed_resources)
            
           
def load_no_public():
    with open('webapp/reports/public_no_access.json') as fh:
        resource_dict = json.load(fh)
        metadata_resources = resource_dict["metadata"]
        data_resources = resource_dict["data"]
    fh.close()
    return (metadata_resources, data_resources)


def load_offline():
    with open('webapp/reports/offline_data.json') as fh:
        resource_dict = json.load(fh)
        offline_resources = resource_dict["offline"]
        unparsed_resources = resource_dict["unparsed"]
    fh.close()
    return (offline_resources, unparsed_resources)
