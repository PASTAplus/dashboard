#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: views

:Synopsis:

:Author:
    servilla

:Created:
    3/6/18
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from webapp.auth.forms import LoginForm
from webapp.config import Config
from webapp.auth.user import User

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Dude, you are already logged in...')
        return redirect(url_for('home.index'))
    form = LoginForm()
    if form.validate_on_submit():
        domain = form.domain.data # Never None
        user_id = 'uid=' + form.username.data + ',' + Config.DOMAINS[domain]
        password = form.password.data
        user = None
        if user_id in Config.USERS:
            auth_token = User.authenticate(user_id=user_id, password=password)
            if auth_token is not None:
                user = User(auth_token=auth_token)
                login_user(user)
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('home.index')
                return redirect(next_page)
        flash('Invalid username or password')
        return redirect(url_for('auth.login'))
    return render_template('login.html', title='Sign In', form=form)

@auth.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('home.index'))
