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

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('home.index'))
    return render_template('login.html',  title='Sign In', form=form)