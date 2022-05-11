#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: test_email

:Synopsis:

:Author:
    servilla

:Created:
    5/9/22
"""
import pytest

from webapp.mimemail import send_mail


def test_mimemail():
    subject = "Test"
    message = "Testing mimemail"

    assert(send_mail(subject, message, "chase.gaucho@gmail.com") is True)
