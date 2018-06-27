#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_upload_stats

:Synopsis:

:Author:
    servilla
  
:Created:
    6/26/18
"""
import os
import sys
import unittest

import daiquiri
import pendulum

from webapp.reports.upload_stats import UploadStats

sys.path.insert(0, os.path.abspath('../src'))
logger = daiquiri.getLogger('test_upload_stats: ' + __name__)


class TestUploadStats(unittest.TestCase):

    def setUp(self):
        self.upload_stats = UploadStats(48)

    def tearDown(self):
        pass

    def test_result_set(self):
        result_set = self.upload_stats.result_set
        self.assertTrue(True)

    def test_plot(self):
        file_name = str(self.upload_stats.now_as_integer)
        self.upload_stats.plot(file_name)
        self.assertTrue(True)



if __name__ == '__main__':
    unittest.main()