# -*- coding: utf-8 -*-


import os
import sys


system_encoding = sys.getfilesystemencoding()


def list_files(directory, exts=None, recursive=False):
    exts = frozenset('.' + ext.lstrip('.') for ext in exts)

    def list_dir(directory):
        for basename in os.listdir(directory):
            filename = os.path.join(directory, basename)
            if recursive and os.path.isdir(filename):
                for filename in list_files(filename, exts, recursive=True):
                    yield filename
                continue
            elif exts and not os.path.splitext(filename)[1].lower() in exts:
                continue
            yield filename

    return sorted(list_dir(directory))
