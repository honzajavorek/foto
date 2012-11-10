# -*- coding: utf-8 -*-


import os


class File(object):

    def __init__(self, filename):
        self.filename = filename

    @property
    def exists(self):
        return os.path.isfile(self.filename)

    @property
    def bytes(self):
        return os.path.getsize(self.filename) / 1024  # kB

    def open(self, *args, **kwargs):
        return open(self.filename, *args, **kwargs)

    def __str__(self):
        return self.filename

    def __repr__(self):
        return '<elk.filesystem.File {0!r}>'.format(self.filename)


class FileEditor(object):

    def __init__(self, config=None):
        self.config = config or {}

    def lowercase_ext(self, file):
        name, ext = os.path.splitext(file.filename)
        if ext.lower() == ext:
            return

        with_lower_ext = name + ext.lower()
        with_upper_ext = name + ext.upper()

        os.rename(with_upper_ext, with_lower_ext)

        return file.__class__(with_lower_ext)


class Directory(object):

    def __init__(self, path):
        self.path = path

    def list(self, ext=None):
        files = os.listdir(self.path)
        if ext:
            ext = ext if ext.startswith('.') else '.' + ext
            f = lambda f: os.path.splitext(f)[1] == ext
            files = filter(f, files)
        return sorted(files)
