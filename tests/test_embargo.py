#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:Mod: test_embargo

:Synopsis:

:Author:
    servilla

:Created:
    9/9/21
"""
import pytest
from webapp.pasta.embargo import Embargo


def test_embargo_class():
    e = Embargo("edi.1.1")
    assert isinstance(e, Embargo)
