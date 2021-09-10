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
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class PackageIdentifier(FlaskForm):
    package_identifier = StringField('Package Identifier',
                                     validators=[DataRequired()])


class Toggle(FlaskForm):
    toggle = SubmitField('Toggle')