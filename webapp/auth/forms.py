  #!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: forms.py

:Synopsis:

:Author:
    servilla
    costa

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


class CreateLdapUser(FlaskForm):
    uid = StringField('User ID', validators=[DataRequired()])
    gn = StringField('Given name', validators=[DataRequired()])
    sn = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    confirm_email = StringField('Confirm Email', validators=[DataRequired()])
    submit = SubmitField('Create User')


class ResetPasswordInit(FlaskForm):
    uid = StringField('User ID', validators=[DataRequired()])
    submit = SubmitField('Reset Password')


class ResetLdapPassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')


class ChangeLdapPassword(FlaskForm):
    uid = StringField('User ID', validators=[DataRequired()])
    password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')


class ModifyLdapUser(FlaskForm):
    uid = StringField('User ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    gn = StringField('Given name', validators=[DataRequired()])
    sn = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    confirm_email = StringField('Confirm Email', validators=[DataRequired()])
    submit = SubmitField('Update User')


class DeleteLdapUser(FlaskForm):
    uid = StringField('User ID', validators=[DataRequired()])
    submit = SubmitField('Delete User')