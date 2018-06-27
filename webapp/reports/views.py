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
from flask import request
from flask_login import login_required
import pendulum
from webapp.reports.upload_stats import UploadStats

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


@reports.route('/recent_uploads', methods=['GET'])
def recent_uploads():
    days = int(request.args.get('days'))
    if days is None:
        days = 7
    stats = UploadStats(hours_in_past=days*24)
    file_name = str(stats.now_as_integer) + '.png'
    file_path = 'webapp/static/' + file_name
    plot = '/static/' + file_name
    stats.plot(file_name=file_path)
    result_set = []
    i = 0
    for result in stats.result_set:
        i += 1
        pid = result[0]
        dt = pendulum.instance(result[1]).to_datetime_string()
        result_set.append((i, pid, dt))
    return render_template('recent_uploads.html', result_set=result_set, plot=plot, days=days)

