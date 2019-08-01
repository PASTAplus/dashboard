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
from wtforms import DateField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Optional


class PackageIdentifier(FlaskForm):
    package_identifier = StringField('Package Identifier',
                                     validators=[DataRequired()])


class UploadReport(FlaskForm):
    scope = StringField('Package Scope', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[Optional()], description='YYYY-MM-DD (defaults to 2013-01-01)')
    end_date = DateField('End Date', validators=[Optional()], description='YYYY-MM-DD (defaults to today)')