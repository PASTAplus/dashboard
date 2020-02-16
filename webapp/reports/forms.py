#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: forms

:Synopsis:

:Author:
    servilla

:Created:
    1/6/19
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import DateField
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Optional

from webapp.reports.upload_report_stats import get_scopes


class PackageIdentifier(FlaskForm):
    package_identifier = StringField('Package Identifier',
                                     validators=[DataRequired()])


class SiteReport(FlaskForm):
    scopes = get_scopes()
    choices = list()
    for scope in scopes:
        choices.append((scope, scope))

    scope = SelectField('Site Scope', choices=choices, default="edi")


class UploadReport(FlaskForm):
    scopes = get_scopes()
    choices = list()
    for scope in scopes:
        choices.append((scope, scope))

    scope = SelectField('Package Scope', choices=choices, default="edi")
    start_date = DateField('Start Date', validators=[Optional()], description='YYYY-MM-DD (defaults to 2013-01-01)')
    end_date = DateField('End Date', validators=[Optional()], description='YYYY-MM-DD (defaults to today)')
    show_title = BooleanField('Show data package title (slower)')
