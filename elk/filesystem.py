# -*- coding: utf-8 -*-


import os
import sys


system_encoding = sys.getfilesystemencoding()


class File(object):
    """File abstraction object."""

    def __init__(self, filename):
        if not isinstance(filename, unicode):
            filename = filename.decode(system_encoding)

        self.filename = filename
        self.name = os.path.basename(filename)

    @property
    def exists(self):
        """Whether file exists."""
        return os.path.isfile(self.filename)

    @property
    def bytes(self):
        """Size of file in bytes."""
        return os.path.getsize(self.filename)

    @property
    def kilobytes(self):
        """Size of file in kilobytes."""
        return self.bytes / 1024

    def open(self, *args, **kwargs):
        """Shorthand. Opens the file."""
        return open(self.filename, *args, **kwargs)

    @property
    def content(self):
        """Reads files's content."""
        with self.open() as f:
            return f.read()

    @content.setter
    def content(self, value):
        """Writes files's content."""
        with self.open('w') as f:
            f.write(value or '')

    def __str__(self):
        """File's path in system encoding."""
        return self.filename.encode(system_encoding)

    def __unicode__(self):
        """File's path in unicode."""
        return self.filename

    def __repr__(self):
        cls = self.__class__
        repr_name = '.'.join((cls.__module__, cls.__name__))
        return '<{name} {filename!r}>'.format(name=repr_name,
                                              filename=self.filename)


class FileEditor(object):
    """File editor abstract class."""

    def __init__(self, config=None):
        self.config = config or {}

    def lowercase_ext(self, file_obj):
        """Lowercases extension."""
        name, ext = os.path.splitext(file_obj.filename)
        if ext.lower() == ext:
            return

        with_lower_ext = name + ext.lower()
        with_upper_ext = name + ext.upper()

        os.rename(with_upper_ext, with_lower_ext)

        return file_obj.__class__(with_lower_ext)


class Directory(object):
    """Directory abstraction object."""

    def __init__(self, path):
        if not isinstance(path, unicode):
            path = path.decode(system_encoding)

        self.path = os.path.normpath(path)
        self.name = os.path.basename(path)

    def list(self, ext=None, cls=File):
        """List files.

        :param ext: Extension to filter out.
        :param cls: Class/callable to use for file instantiation.
        """
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
        """Directory's path in system encoding."""
        return self.path.encode(system_encoding)

    def __unicode__(self):
        """Directory's path in unicode."""
        return self.path

    def __repr__(self):
        cls = self.__class__
        repr_name = '.'.join((cls.__module__, cls.__name__))
        return '<{name} {path!r}>'.format(name=repr_name,
                                          path=self.path)


class DirectoryEditor(object):
    """Directory editor abstract class."""

    def __init__(self, config=None):
        self.config = config or {}

    def rename(self, dir_obj, name):
        """Renames directory."""
        path = os.path.join(os.path.split(dir_obj.path)[0], name)
        os.rename(dir_obj.path, path)
        return dir_obj.__class__(path)
