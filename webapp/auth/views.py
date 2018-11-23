#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: views

:Synopsis:

:Author:
    servilla
    costa

:Created:
    3/6/18
"""
import daiquiri
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import abort
from flask_login import current_user, login_user, logout_user, login_required

from werkzeug.urls import url_parse

from webapp.auth import token_uid
from webapp.auth.forms import CreateLdapUser
from webapp.auth.forms import LoginForm
from webapp.auth.forms import ResetPasswordInit
from webapp.auth.forms import ResetLdapPassword
from webapp.auth.forms import ChangeLdapPassword
from webapp.auth.forms import ModifyLdapUserInit
from webapp.auth.forms import ModifyLdapUser
from webapp.auth.forms import DeleteLdapUser
from webapp.auth.ldap_directory import LdapDirectory
from webapp.auth.ldap_user import LdapUser
from webapp.auth.ldap_user import AttributeError, UidError
from webapp.auth.user import User
from webapp.config import Config
from webapp import mailout


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
        msg = reset_password_mail_body(ldap_user=ldap_user, url=url)
        subject = 'EDI reset password...'
        sent = mailout.send_mail(subject=subject, msg=msg, to=ldap_user.email)
        if not sent:
            abort(500)
        return redirect(url_for('auth.user_created', uid=ldap_user.uid))
    # Process GET
    return render_template('create_ldap_user.html', title='Create LDAP User',
                           form=form)


@auth.route('/reset_password_init', methods=['GET', 'POST'])
def reset_password_init():
    form = ResetPasswordInit()
    # Process POST
    if form.validate_on_submit():
        ldap_user = LdapUser(uid=form.uid.data)
        url = request.host_url + \
              url_for('auth.reset_password', token=ldap_user.token.decode())[1:]
        msg = reset_password_mail_body(ldap_user=ldap_user, url=url)
        subject = 'EDI reset password...'
        sent = mailout.send_mail(subject=subject, msg=msg, to=ldap_user.email)
        if not sent:
            abort(500)
        return redirect(url_for('auth.password_reset', uid=ldap_user.uid))
    # Process GET
    return render_template('reset_password_init.html', title='Reset EDI Password',
                           form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token=None):
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
        uid, _ = token_uid.decode_token(token=token)
        token_uid.remove_token(token=token)
        try:
            ldap_user = LdapUser(uid=uid)
            ldap_user.password = password
            reset = ldap_user.reset_password()
            if not reset:
                abort(500)
            return redirect(url_for('auth.welcome_user', uid=ldap_user.uid))
        except UidError as e:
            logger.error(e)
            abort(400)
    # Process GET
    token_file, ttl = token_uid.decode_token(token=token)
    # Ensure token file and ttl are valid
    if token_file is None:
        abort(400)
    elif token_uid.is_expired(ttl=ttl, expiry=1440): # Expiry is 24 hours
        token_uid.remove_token(token=token)
        abort(400)
    else:
       return render_template('reset_ldap_password.html', title='Password Reset',
                           form=form)


@auth.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangeLdapPassword()
    # Process POST
    if form.validate_on_submit():
        ldap_user = LdapUser()
        ldap_user.uid = form.uid.data
        ldap_user.password = form.password.data
        if form.new_password.data != form.confirm_new_password.data:
            flash('New password values do not match')
            return redirect(url_for('auth.change_password'))
        try:
            changed = ldap_user.change_password(form.new_password.data)
            if not changed:
                msg = 'Password for User ID "{0}" could not be changed'.format(ldap_user.uid)
                flash(msg)
                return redirect(url_for('auth.change_password'))
        except AttributeError as e:
            flash('Attribute error - ' + e)
            return redirect(url_for('auth.change_password'))
        except Exception as e:
            abort(500)
        return redirect(url_for('auth.password_changed', uid=ldap_user.uid))
    # Process GET
    return render_template('change_password.html', title='Change EDI Password',
                           form=form)


@auth.route('/modify_ldap_user_init', methods=['GET', 'POST'])
def modify_ldap_user_init():
    form = ModifyLdapUserInit()
    # Process POST
    if form.validate_on_submit():
        uid = form.uid.data
        password = form.password.data
        try:
            ldap_user = LdapUser(uid=uid)
            ldap_user.password = password
            is_valid = ldap_user._valid_password()
        except AttributeError as e:
            flash('Attribute error - ' + e)
            return redirect(url_for('auth.modify_ldap_user'))
        except Exception as e:
            abort(500)
        if is_valid:
            return redirect(url_for('auth.modify_ldap_user', uid=uid, 
                                                            password=password))
        else:
            msg = 'User ID "{0}" could not be updated'.format(ldap_user.uid)
            flash(msg)
            return redirect(url_for('auth.modify_ldap_user_init'))
    # Process GET
    return render_template('modify_ldap_user_init.html',
                            title='Modify LDAP User',
                            form=form)


@auth.route('/modify_ldap_user/<uid>', methods=['GET', 'POST'])
def modify_ldap_user(uid=None):
    form = ModifyLdapUser()
    ldap_user = LdapUser(uid=uid)
    # Process POST
    if form.validate_on_submit():
        if form.email.data != form.confirm_email.data:
            flash('Emails do not match')
            return redirect(url_for('auth.modify_ldap_user'))
        ldap_user.gn = form.gn.data
        ldap_user.sn = form.sn.data
        ldap_user.email = form.email.data
        ldap_user.password = form.password.data
        try:
            modified = ldap_user.modify()
            if not modified:
                msg = 'User ID "{0}" could not be updated'.format(ldap_user.uid)
                flash(msg)
                return redirect(url_for('auth.modify_ldap_user_init'))
        except AttributeError as e:
            flash('Attribute error - ' + e)
            return redirect(url_for('auth.modify_ldap_user_init'))
        except Exception as e:
            abort(500)
        return redirect(url_for('auth.user_modified', uid=uid))
    # Process GET
    form.gn.data = ldap_user.gn
    form.sn.data = ldap_user.sn
    form.email.data = ldap_user.email
    form.confirm_email.data = form.email.data
    return render_template('modify_ldap_user.html', title='Modify LDAP User',
                           form=form, uid=uid)


@auth.route('/delete_ldap_user', methods=['GET', 'POST'])
@login_required
def delete_ldap_user():
    form = DeleteLdapUser()
    # Process POST
    if form.validate_on_submit():
        ldap_user = LdapUser()
        ldap_user.uid = form.uid.data
        try:
            deleted = ldap_user.delete()
            if not deleted:
                msg = 'User ID "{0}" was not found in the LDAP directory'.format(ldap_user.uid)
                flash(msg)
                return redirect(url_for('auth.delete_ldap_user'))
        except AttributeError as e:
            flash('Attribute error - ' + e)
            return redirect(url_for('auth.delete_ldap_user'))
        except Exception as e:
            abort(500)
        return redirect(url_for('auth.user_deleted', uid=ldap_user.uid))
    # Process GET
    return render_template('delete_ldap_user.html', title='Delete LDAP User',
                           form=form)


@auth.route('/list_ldap_users')
@login_required
def list_ldap_users():
    ldap_directory = LdapDirectory()
    users_list = ldap_directory.list_ldap_users()
    return render_template('list_ldap_users.html', users_list=users_list)


@auth.route('/welcome_user/<uid>')
def welcome_user(uid=None):
    ldap_user = LdapUser(uid=uid)
    return render_template('welcome_user.html', ldap_user=ldap_user)


@auth.route('/user_created/<uid>')
def user_created(uid=None):
    ldap_user = LdapUser(uid=uid)
    return render_template('user_created.html', ldap_user=ldap_user)


@auth.route('/password_reset/<uid>')
def password_reset(uid=None):
    ldap_user = LdapUser(uid=uid)
    return render_template('password_reset.html', ldap_user=ldap_user)


@auth.route('/password_changed/<uid>')
def password_changed(uid=None):
    return render_template('password_changed.html', uid=uid)


@auth.route('/user_modified/<uid>')
def user_modified(uid=None):
    ldap_user = LdapUser(uid=uid)
    return render_template('user_modified.html', ldap_user=ldap_user)


@auth.route('/user_deleted/<uid>')
def user_deleted(uid=None):
    return render_template('user_deleted.html', uid=uid)


def reset_password_mail_body(ldap_user=None, url=None):
    msg = 'Hello ' + ldap_user.cn + ',\n\n' + \
          'A user account with the identifier "' + ldap_user.uid + \
          '" was created on your behalf for you to access the ' + \
          'Environmental Data Initiative data repository, namely through ' + \
          'the EDI Data Portal. Please use the following URL to set ' + \
          'your password:\n\n' + url + '\n\n' + \
          'This URL provides a one-time password reset and will expire ' + \
          'in 24 hours.\n\nIf you have received this email in error, ' + \
          'please ignore.\n\nSincerely,\nThe EDI Team'

    return msg