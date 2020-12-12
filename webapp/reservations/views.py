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


logger = daiquiri.getLogger(__name__)


reservations = Blueprint('reservations', __name__, template_folder='templates')


@reservations.route('/render_reservations', methods=['GET', 'POST'])
def render_reservations():
    datetime_str = get_datetime_str()
    production_dict = request_reservations('https://pasta.lternet.edu')
    staging_dict = request_reservations('https://pasta-s.lternet.edu')
    development_dict = request_reservations('https://pasta-d.lternet.edu')
    return render_template('reservations.html', 
                            production_dict=production_dict, 
                            staging_dict=staging_dict, 
                            development_dict=development_dict,
                            datetime_str=datetime_str)


def get_datetime_str():
    mtn = timezone("America/Denver")
    lt = mtn.convert(pendulum.now())
    return lt.to_day_datetime_string()
                           
          
def request_reservations(base_url=None):
    reservations_dict = {}
    try:
        if (base_url):
            url = base_url + '/package/reservations/eml'
        else:
            url = 'http://localhost:8080/reservationsTest.txt'
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            logger.error('Bad status code ({code}) for {url}'.format(
                code=r.status_code, url=url))
        else:
            xml = r.text
            root = ET.fromstring(xml)
            for child in root:
                if child.tag == 'reservation':
                    docid = ''
                    principal = ''
                    date_reserved = ''
                    for grandchild in child:
                        if grandchild.tag == 'docid':
                            docid = grandchild.text
                        if grandchild.tag == 'principal':
                            principal = grandchild.text
                        if grandchild.tag == 'dateReserved':
                            date_reserved = grandchild.text
                    if (docid and principal and date_reserved):
                        values = []
                        values.append(principal)
                        values.append(date_reserved)
                        reservations_dict[docid] = values
    except Exception as e:
        logger.error(e)
    return reservations_dict
    
