#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: views

:Synopsis:

:Author:
    servilla

:Created:
    3/6/18
"""
import daiquiri
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import abort
from flask_login import current_user, login_user, logout_user, login_required

from werkzeug.urls import url_parse

from webapp.auth import mailout
from webapp.auth import token_uid
from webapp.auth.forms import CreateLdapUser
from webapp.auth.forms import LoginForm
from webapp.auth.forms import ResetLdapPassword
from webapp.auth.ldap_user import LdapUser
from webapp.auth.ldap_user import AttributeError, UidError
from webapp.auth.user import User
from webapp.config import Config


logger = daiquiri.getLogger('views: ' + __name__)
auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(current_user.get_username() + ', you are already logged in...')
        return redirect(url_for('home.index'))
    # Process POST
    form = LoginForm()
    if form.validate_on_submit():
        domain = form.domain.data # Never None
        user_dn = 'uid=' + form.username.data + ',' + Config.DOMAINS[domain]
        password = form.password.data
        user = None
        if user_dn in Config.USERS:
            auth_token = User.authenticate(user_dn=user_dn, password=password)
            if auth_token is not None:
                user = User(auth_token=auth_token)
                login_user(user)
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('home.index')
                return redirect(next_page)
        flash('Invalid username or password')
        return redirect(url_for('auth.login'))
    # Process GET
    return render_template('login.html', title='Sign In', form=form)

@auth.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('home.index'))


@auth.route('/create_ldap_user', methods=['GET', 'POST'])
@login_required
def create_ldap_user():
    form = CreateLdapUser()
    # Process POST
    if form.validate_on_submit():
        ldap_user = LdapUser()
        ldap_user.uid = form.uid.data
        ldap_user.gn = form.gn.data
        ldap_user.sn = form.sn.data
        if form.email.data != form.confirm_email.data:
            flash('Emails do not match')
            return redirect(url_for('auth.create_ldap_user'))
        ldap_user.email = form.email.data
        try:
            created = ldap_user.create()
            if not created:
                msg = 'User ID "{0}" already in use'.format(ldap_user.uid)
                flash(msg)
                return redirect(url_for('auth.create_ldap_user'))
        except AttributeError as e:
            flash('Attribute error - ' + e)
            return redirect(url_for('auth.create_ldap_user'))
        except Exception as e:
            abort(500)
        url = request.host_url + \
              url_for('auth.reset_password', token=ldap_user.token.decode())[1:]
        msg = mailout.reset_password_mail_body(ldap_user=ldap_user, url=url)
        subject = 'EDI reset password...'
        mailout.send_mail(subject=subject, msg=msg,to=ldap_user.email)
        return redirect(url_for('auth.user_created', uid=ldap_user.uid))
    # Process GET
    return render_template('create_ldap_user.html', title='Create LDAP User',
                           form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token=None):
    uid = None
    try:
        uid = token_uid.decode_uid(token=token)
    except Exception as e:
        logger.error(e)
        abort(400)
    form = ResetLdapPassword()
    # Process POST
    if form.validate_on_submit():
        password = form.password.data
        confirm_password = form.confirm_password.data
        if password != confirm_password:
            msg = 'Passwords do not match'
            flash(msg)
            url = request.host_url + \
                  url_for('auth.reset_password', token=token)[1:]
            return redirect(url)
        try:
            ldap_user = LdapUser(uid=uid)
            ldap_user.password = password
            reset = ldap_user.reset_password()
            token_uid.remove_token(token=token)
            if not reset:
                abort(500)
        except UidError as e:
            logger.error(e)
            abort(400)
        return redirect(url_for('auth.welcome_user', uid=ldap_user.uid))
    # Process GET
    return render_template('reset_ldap_password.html', title='Password Rest',
                           form=form)


@auth.route('/welcome_user/<uid>')
def welcome_user(uid=None):
    ldap_user = LdapUser(uid=uid)
    return render_template('welcome_user.html', ldap_user=ldap_user)


@auth.route('/user_created/<uid>')
def user_created(uid=None):
    ldap_user = LdapUser(uid=uid)
    return render_template('user_created.html', ldap_user=ldap_user)