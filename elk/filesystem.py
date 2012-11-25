# -*- coding: utf-8 -*-


import os


class File(object):

    def __init__(self, filename):
        self.filename = filename
        self.name = os.path.basename(filename)

    @property
    def exists(self):
        return os.path.isfile(self.filename)

    @property
    def bytes(self):
        return os.path.getsize(self.filename) / 1024  # kB

    def open(self, *args, **kwargs):
        return open(self.filename, *args, **kwargs)

    @property
    def content(self):
        with self.open() as f:
            return f.read()

    @content.setter
    def content(self, value):
        with self.open('w') as f:
            f.write(value or '')

    def __str__(self):
        return self.filename

    def __repr__(self):
        cls = self.__class__
        repr_name = '.'.join((cls.__module__, cls.__name__))
        return '<{name} {filename!r}>'.format(name=repr_name,
                                              filename=self.filename)


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
        self.name = os.path.basename(path)

    def list(self, ext=None, cls=File):
        files = os.listdir(self.path)
        if ext:
            ext = (ext if ext.startswith('.') else '.' + ext).lower()
            f = lambda f: os.path.splitext(f)[1].lower() == ext
            files = filter(f, files)
        files = sorted(files)
        if cls:
            return [cls(os.path.join(self.path, f)) for f in files]
        return files

    def __str__(self):
        return self.path

    def __repr__(self):
        cls = self.__class__
        repr_name = '.'.join((cls.__module__, cls.__name__))
        return '<{name} {path!r}>'.format(name=repr_name,
                                          path=self.path)


class DirectoryEditor(object):

    def __init__(self, config=None):
        self.config = config or {}

    def rename(self, dir, name):
        path = os.path.join(os.path.split(dir.path)[0], name)
        os.rename(dir.path, path)
        return dir.__class__(path)
