#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: views.py

:Synopsis:

:Author:
    Duane Costa

:Created:
    4/11/18
"""

import daiquiri
from flask import Blueprint, render_template
from flask_login import login_required
import xml.etree.ElementTree as ET
import pendulum
from pendulum import timezone
import requests


logger = daiquiri.getLogger('upload_report: ' + __name__)


pasta = Blueprint('pasta', __name__, template_folder='templates')


@pasta.route('/render_working_on', methods=['GET', 'POST'])
def render_working_on():
    datetime_str = get_datetime_str()
    production_dict = working_on('https://pasta.lternet.edu')
    staging_dict = working_on('https://pasta-s.lternet.edu')
    development_dict = working_on('https://pasta-d.lternet.edu')
    return render_template('working_on.html', 
                            production_dict=production_dict, 
                            staging_dict=staging_dict, 
                            development_dict=development_dict,
                            datetime_str=datetime_str)


def get_datetime_str():
    mtn = timezone("America/Denver")
    lt = mtn.convert(pendulum.now())
    return lt.to_day_datetime_string()
                           
          
def working_on(base_url=None):
    working_on_dict = {}
    try:
        if (base_url):
            url = base_url + '/package/workingon/eml'
        else:
            url = 'http://localhost:8080/workingOnTest.txt'
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            logger.error('Bad status code ({code}) for {url}'.format(
                code=r.status_code, url=url))
        else:
            xml = r.text
            root = ET.fromstring(xml)
            for child in root:
                has_principal_public = False
                has_permission_read = False
                if child.tag == 'dataPackage':
                    package_id = ''
                    service_method = ''
                    start_date = ''
                    for grandchild in child:
                        if grandchild.tag == 'packageId':
                            package_id = grandchild.text
                        if grandchild.tag == 'serviceMethod':
                            service_method = grandchild.text[:-11]
                        if grandchild.tag == 'startDate':
                            start_date = grandchild.text
                    if (package_id and start_date):
                        value_list = []
                        value_list.append(service_method)
                        value_list.append(start_date)
                        working_on_dict[package_id] = value_list

    except Exception as e:
        logger.error(e)
    return working_on_dict