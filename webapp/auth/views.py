#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: views

:Synopsis:

:Author:
    servilla

:Created:
    3/6/18
"""

from flask import Blueprint, flash, redirect, render_template, url_for
from webapp.auth.forms import LoginForm
from webapp import properties
from webapp.auth.user import User

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, password {}, domain {}'.format(
            form.username.data, form.password.data, form.domain.data))
        if form.domain.data == 'edi':
            dn_suffix = properties.EDI_DN
        else:
            dn_suffix = properties.LTER_DN
        user_id = 'uid=' + form.username.data + ',' + dn_suffix
        password = form.password.data
        if user_id not in properties.USERS \
                or not User.authenticate(user_id=user_id, password=password):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        return redirect(url_for('home.index'))
    return render_template('login.html', title='Sign In', form=form)
