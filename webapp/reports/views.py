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
import os

from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import login_required
import pendulum

from webapp.config import Config
from webapp.reports.forms import PackageIdentifier
from webapp.reports.package_tracker import PackageStatus
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

            if metadata_resources is None:
                len_metadata_resources = 0
            else:
                len_metadata_resources = len(metadata_resources)

            if data_resources is None:
                len_data_resources = 0
            else:
                len_data_resources = len(data_resources)

            return render_template('report_no_public.html',
                                   metadata_resources=metadata_resources,
                                   data_resources=data_resources,
                                   len_metadata_resources=len_metadata_resources,
                                   len_data_resources=len_data_resources)
        elif report_type == 'offline':
            offline_resources, unparsed_resources = load_offline()

            if offline_resources is None:
                len_offline_resources = 0
            else:
                len_offline_resources = len(offline_resources)

            if unparsed_resources is None:
                len_unparsed_resources = 0
            else:
                len_unparsed_resources = len(unparsed_resources)

            return render_template('report_offline.html',
                                   offline_resources=offline_resources,
                                   unparsed_resources=unparsed_resources,
                                   len_offline_resources=len_offline_resources,
                                   len_unparsed_resources=len_unparsed_resources)


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
    return offline_resources, unparsed_resources


@reports.route('/package_tracker', methods=['GET', 'POST'])
def package_tracker():
    form = PackageIdentifier()
    if form.validate_on_submit():
        # Process POST
        package_identifier = form.package_identifier.data
        if len(package_identifier.split('.')) != 3:
            msg = 'should be in the form of scope.identifier.revision'
            flash(f'"{package_identifier}" {msg}')
            return redirect(url_for('reports.package_tracker'))
        package_status = PackageStatus(package_identifier)
        return render_template('package_status.html', package_status=package_status)
    # Process GET
    return render_template('package_tracker.html', form=form)




@reports.route('/recent_uploads', methods=['GET'])
def recent_uploads():
    days = int(request.args.get('days'))
    if days is None:
        days = 7
    scope = request.args.get('scope')
    stats = UploadStats(hours_in_past=days * 24, scope=scope)
    count = stats.count

    # Create webapp static directory if not exists
    if not os.path.exists(Config.STATIC):
        os.makedirs(Config.STATIC)

    file_name = str(stats.now_as_integer) + '.png'
    file_path = Config.STATIC + '/' + file_name
    plot = '/static/' + file_name
    stats.plot(file_path=file_path)
    result_set = []
    i = 0
    for result in stats.result_set:
        i += 1
        pid = result[0]
        dt = pendulum.instance(result[1]).to_datetime_string()
        result_set.append((i, pid, dt))
    return render_template('recent_uploads.html', result_set=result_set,
                           count=count, plot=plot, days=days)
