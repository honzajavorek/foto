# -*- coding: utf-8 -*-


import os
from elk import filesystem
from .utils import FileTestCase


class FileTest(FileTestCase):

    def test_exists(self):
        f = filesystem.File(self.filename)
        self.assertTrue(f.exists)
        f = filesystem.File('.......')  # non-existing file
        self.assertFalse(f.exists)

    def test_size(self):
        f = filesystem.File(self.filename)
        self.assertEqual(f.size, self.size / 1024)  # kB

    def test_open(self):
        f = filesystem.File(self.filename)
        with f.open('r') as open_file:
            one_byte = open_file.read(1)
        with f.open('w') as open_file:
            open_file.write(one_byte)

    def test_str(self):
        f = filesystem.File(self.filename)
        self.assertEqual(self.filename, str(f))

    def test_repr(self):
        f = filesystem.File(self.filename)
        self.assertEqual('<elk.filesystem.File {0!r}>'.format(self.filename),
                         repr(f))


class FileEditorTest(FileTestCase):

    def test_lowercase_ext(self):
        f = filesystem.File(self.filename)

        fe = filesystem.FileEditor()
        f = fe.lowercase_ext(f)

        self.assertEquals(os.path.splitext(f.filename)[1],
                          os.path.splitext(f.filename)[1].lower())


class Directory(FileTestCase):

    def test_list(self):
        d = filesystem.Directory(os.path.dirname(self.filename))
        self.assertEquals(d.list()[0], os.path.basename(self.filename))

    def test_list_ext(self):
        d = filesystem.Directory(os.path.dirname(self.filename))
        self.assertEquals(d.list('jpg'), [])
        self.assertEquals(d.list('JPG')[0], os.path.basename(self.filename))
        self.assertEquals(d.list('.JPG')[0], os.path.basename(self.filename))
