#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: views.py

:Synopsis:

:Author:
    Duane Costa

:Created:
    3/6/18
"""
import datetime
import time
import json
import os

import daiquiri
from flask import Blueprint, flash, render_template, request, redirect, send_from_directory, url_for
from flask_login import login_required
import pendulum

from webapp.config import Config
from webapp.reports.forms import PackageIdentifier
from webapp.reports.forms import UploadReport
from webapp.reports.package_tracker import PackageStatus
from webapp.reports.upload_stats import UploadStats
from webapp.reports.upload_report_stats import get_package_title
from webapp.reports.upload_report_stats import get_scope_count
from webapp.reports.upload_report_stats import solr_report_stats
from webapp.reports.upload_report_stats import upload_report_stats

reports = Blueprint('reports', __name__, template_folder='templates')
logger = daiquiri.getLogger(__name__)


@reports.route('/render_no_public', methods=['GET', 'POST'])
@login_required
def render_no_public():
    return render_report(report_type='no_public')


@reports.route('/render_offline', methods=['GET', 'POST'])
@login_required
def render_offline():
    return render_report(report_type='offline')


@reports.route('/render_doi_report', methods=['GET', 'POST'])
@login_required
def render_doi_report():
    return render_report(report_type='doi_report')


def render_report(report_type=None):
    if report_type:
        if report_type == 'no_public':
            metadata_resources, data_resources, md = load_no_public()

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
                                   len_data_resources=len_data_resources,
                                   modification_date=md)

        elif report_type == 'offline':
            offline_resources, unparsed_resources, md = load_offline()

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
                                   len_unparsed_resources=len_unparsed_resources,
                                   modification_date=md)

        elif report_type == "doi_report":
            not_resolved_resources, missing_resources, not_resolved_deactivated_resources, missing_deactivated_resources, md = load_doi_report()

            if not_resolved_resources is None:
                len_not_resolved_resources = 0
            else:
                len_not_resolved_resources = len(not_resolved_resources)

            if missing_resources is None:
                len_missing_resources = 0
            else:
                len_missing_resources = len(missing_resources)

            if not_resolved_deactivated_resources is None:
                len_not_resolved_deactivated_resources = 0
            else:
                len_not_resolved_deactivated_resources = len(not_resolved_deactivated_resources)

            if missing_deactivated_resources is None:
                len_missing_deactivated_resources = 0
            else:
                len_missing_deactivated_resources = len(missing_deactivated_resources)

            return render_template('report_doi_report.html',
                                   not_resolved_resources=not_resolved_resources,
                                   missing_resources=missing_resources,
                                   not_resolved_deactivated_resources=not_resolved_deactivated_resources,
                                   missing_deactivated_resources=missing_deactivated_resources,
                                   len_not_resolved_resources=len_not_resolved_resources,
                                   len_missing_resources=len_missing_resources,
                                   len_not_resolved_deactivated_resources=len_not_resolved_deactivated_resources,
                                   len_missing_deactivated_resources=len_missing_deactivated_resources,
                                   modification_date=md)


def load_no_public():
    filename = 'webapp/reports/public_no_access.json'
    with open(filename) as fh:
        resource_dict = json.load(fh)
        metadata_resources = resource_dict["metadata"]
        data_resources = resource_dict["data"]
    fh.close()
    md = modification_date(filename)
    return (metadata_resources, data_resources, md)


def load_offline():
    filename = 'webapp/reports/offline_data.json'
    with open(filename) as fh:
        resource_dict = json.load(fh)
        offline_resources = resource_dict["offline"]
        unparsed_resources = resource_dict["unparsed"]
    fh.close()
    md = modification_date(filename)
    return offline_resources, unparsed_resources, md


def load_doi_report():
    filename = 'webapp/reports/doi_report.json'
    with open(filename) as fh:
        resource_dict = json.load(fh)
        not_resolved_resources = resource_dict["not_resolved"]
        missing_resources = resource_dict["missing"]
        not_resolved_deactivated_resources = resource_dict["not_resolved_deactivated"]
        missing_deactivated_resources = resource_dict["missing_deactivated"]
    fh.close()
    md = modification_date(filename)
    return not_resolved_resources, missing_resources,\
           not_resolved_deactivated_resources, missing_deactivated_resources,\
           md


def modification_date(filename):
    t = os.path.getmtime(filename)
    mod_date = time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(t))
    return mod_date


@reports.route('/package_tracker', methods=['GET', 'POST'])
def package_tracker():
    package_identifier = request.args.get('pid')
    form = PackageIdentifier()
    if form.validate_on_submit():
        package_identifier = form.package_identifier.data
    if package_identifier is not None:  # Process and return
        if len(package_identifier.split('.')) != 3:
            msg = 'should be in the form of scope.identifier.revision'
            flash(f'"{package_identifier}" {msg}')
            return redirect(url_for('reports.package_tracker'))
        package_status = PackageStatus(package_identifier)
        return render_template('package_status.html',
                               package_status=package_status)
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


@reports.route('/upload_report', methods=['GET', 'POST'])
def upload_report():
    form = UploadReport()
    if form.validate_on_submit():
        # Process POST
        scope = form.scope.data

        start_date = form.start_date.data
        if start_date is None:
            # Set to PASTA birthday
            start_date = datetime.date(2013, 1, 1)

        end_date = form.end_date.data
        if end_date is None:
            end_date = datetime.date.today()

        show_title = form.show_title.data

        stats = upload_report_stats(scope, start_date, end_date)
        rows = get_scope_count(scope)
        solr_stats = solr_report_stats(scope, rows)
        result_set = list()
        i = 0
        j = 0
        for stat in stats:
            i += 1
            pid = stat[0]
            doi = stat[1]
            dt = pendulum.instance(stat[2]).to_datetime_string()
            package_title = None
            if show_title:
                if pid in solr_stats:
                    package_title = solr_stats[pid]
                    j += 1
                else:
                    package_title = get_package_title(pid)
                    if package_title is None:
                        package_title = '404 - Not allowed'

            result_set.append((i, pid, doi, package_title, dt))

        file_name = str(time.time())
        with open(f'{Config.TMP_DIR}/{file_name}.csv', 'w') as f:
            if show_title:
                line = f'Count,Package ID,DOI,Title,Upload Date-Time\n'
            else:
                line = f'Count,Package ID,DOI,Upload Date-Time\n'
            f.write(line)

            for result in result_set:
                if show_title:
                    line = f'{result[0]},{result[1]},{result[2]},"{result[3]}",{result[4]}\n'
                else:
                    line = f'{result[0]},{result[1]},{result[2]},{result[4]}\n'
                f.write(line)

        return render_template('upload_report_stats.html',
                               scope=scope, start_date=start_date.isoformat(),
                               end_date=end_date.isoformat(),
                               result_set=result_set, show_title=show_title,
                               count=i, solr_count=j, file_name=file_name)

    # Process GET
    return render_template('upload_report.html', form=form)

@reports.route('/download_report/<filename>', methods=['GET'])
def download_report(filename):
    return send_from_directory(Config.TMP_DIR, filename, as_attachment=True,
                               attachment_filename='upload_report.csv')
