# -*- coding: utf-8 -*-


import os
import shutil
import tempfile
import datetime

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestCase(unittest.TestCase):
    pass


class FileTestCase(TestCase):

    basename = 'file.TXT'
    bytes = 0

    def setUp(self):
        filename = os.path.join(os.path.dirname(__file__), self.basename)
        temp_dir = tempfile.mkdtemp()
        shutil.copy(filename, temp_dir)

        self.temp_dir = temp_dir
        self.filename = os.path.join(temp_dir, self.basename)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)


class PhotoTestCase(FileTestCase):
    basename = 'P1150648.JPG'
    bytes = 3419633
    datetime = datetime.datetime(2011, 11, 11, 16, 27, 25)
    size = (3072, 2304)


class VideoTestCase(FileTestCase):
    basename = 'P1170591.MOV'
    bytes = 2820346
