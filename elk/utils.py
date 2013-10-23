# -*- coding: utf-8 -*-


import os
import sys


system_encoding = sys.getfilesystemencoding()


def list_files(directory, ext=None):
    if ext:
        ext = '.' + ext.lstrip('.')

    def list_dir(directory):
        for basename in os.listdir(directory):
            filename = os.path.join(directory, basename)

            if ext and not os.path.splitext(filename)[1].lower() == ext:
                continue
            yield filename

    return sorted(list_dir(directory))
