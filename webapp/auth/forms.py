#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: forms.py

:Synopsis:

:Author:
    servilla

:Created:
    3/6/18
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    domain_choices = [('edi', 'EDI'), ('lter', 'LTER')]
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    domain = SelectField('Domain', choices=domain_choices)
    submit = SubmitField('Sign In')