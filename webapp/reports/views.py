#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: views.py

:Synopsis:

:Author:
    servilla

:Created:
    3/6/18
"""
import json

from flask import Blueprint, render_template
from flask_login import login_required

reports = Blueprint('reports', __name__, template_folder='templates')


@reports.route('/render', methods=['GET', 'POST'])
@login_required
def render():
    report_html = generate_report()
    return render_template('report.html', report_html=report_html)


def generate_report(report_type=None):
    if report_type is None:
        no_public_html = render_report(report_type='no_public')
        offline_html = render_report(report_type='offline')
        return no_public_html + "\n" + offline_html
    else:
        return render_report(report_type=report_type)


def render_report(report_type=None):
    if report_type:
        if report_type == 'no_public':
            return render_no_public()
        elif report_type == 'offline':
            return render_offline()


def render_no_public():
    html_strings = []

    with open('./webapp/reports/public_no_access.json') as fh:
        resource_dict = json.load(fh)
        metadata_resources = resource_dict["metadata"]
        data_resources = resource_dict["data"]

        html_strings.append(
            "<h1>PASTA Resources Lacking Public Read Access</h1>")
        html_strings.append("<h2>Metadata Resources</h2>")
        html_strings.append("<table style='border: 1px solid black'>")
        html_strings.append("    <tr>")
        html_strings.append("        <th>Package ID</th>")
        html_strings.append("        <th>Resource ID</th>")
        html_strings.append("        <th>ACL XML</th>")
        html_strings.append("    </tr>")
        for metadata_dict in metadata_resources:
            html_strings.append("    <tr>")
            html_strings.append(
                "        <td>%s</td>" % metadata_dict["package_id"])
            html_strings.append(
                "        <td>%s</td>" % metadata_dict["resource_id"])
            html_strings.append(
                "        <td>%s</td>" % metadata_dict["acl_xml"])
            html_strings.append("    </tr>")
        html_strings.append("</table>")

        html_strings.append("<h2>Data Resources</h2>")
        html_strings.append("<table style='border: 1px solid black'>")
        html_strings.append("    <tr>")
        html_strings.append("        <th>Package ID</th>")
        html_strings.append("        <th>Resource ID</th>")
        html_strings.append("        <th>ACL XML</th>")
        html_strings.append("    </tr>")
        for data_dict in metadata_resources:
            html_strings.append("    <tr>")
            html_strings.append("        <td>%s</td>" % data_dict["package_id"])
            html_strings.append(
                "        <td>%s</td>" % data_dict["resource_id"])
            html_strings.append("        <td>%s</td>" % data_dict["acl_xml"])
            html_strings.append("    </tr>")
        html_strings.append("</table>")

    fh.close()
    html_string = "\n".join(html_strings)
    return html_string


def render_offline():
    html_strings = []

    with open('./webapp/reports/offline_data.json') as fh:
        resource_dict = json.load(fh)
        offline_resources = resource_dict["offline"]
        unparsed_resources = resource_dict["unparsed"]

        html_strings.append(
            "<h1>PASTA Data Entities with Offline Distribution</h1>")

        html_strings.append("<h2>Offline Data Resources</h2>")
        html_strings.append("<table style='border: 1px solid black'>")
        html_strings.append("    <tr>")
        html_strings.append("        <th>Package ID</th>")
        html_strings.append("        <th>Resource ID</th>")
        html_strings.append("        <th>Object Name</th>")
        html_strings.append("        <th>Medium Name</th>")
        html_strings.append("    </tr>")
        for offline_dict in offline_resources:
            html_strings.append("    <tr>")
            html_strings.append(
                "        <td>%s</td>" % offline_dict["package_id"])
            html_strings.append(
                "        <td>%s</td>" % offline_dict["resource_id"])
            html_strings.append(
                "        <td>%s</td>" % offline_dict["object_name"])
            html_strings.append(
                "        <td>%s</td>" % offline_dict["medium_name"])
            html_strings.append("    </tr>")
        html_strings.append("</table>")

        html_strings.append(
            "<h2>Unparsed Resources (Metadata could not be accessed)</h2>")
        html_strings.append("<table style='border: 1px solid black'>")
        html_strings.append("    <tr>")
        html_strings.append("        <th>Package ID</th>")
        html_strings.append("        <th>Resource ID</th>")
        html_strings.append("        <th>Object Name</th>")
        html_strings.append("        <th>Medium Name</th>")
        html_strings.append("    </tr>")
        for unparsed_dict in unparsed_resources:
            html_strings.append("    <tr>")
            html_strings.append(
                "        <td>%s</td>" % unparsed_dict["package_id"])
            html_strings.append(
                "        <td>%s</td>" % unparsed_dict["resource_id"])
            html_strings.append(
                "        <td>%s</td>" % unparsed_dict["object_name"])
            html_strings.append(
                "        <td>%s</td>" % unparsed_dict["medium_name"])
            html_strings.append("    </tr>")
        html_strings.append("</table>")

    fh.close()
    html_string = "\n".join(html_strings)
    return html_string
