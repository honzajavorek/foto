# -*- coding: utf-8 -*-


import os

from elk.utils import list_files


def names_fix(directory):
    for filename in list_files(directory):
        basename = os.path.basename(filename)

        base, ext = os.path.splitext(basename)
        if ext.lower() == '.jpeg':
            ext = '.jpg'
        new_basename = base + ext.lower()

        if basename != new_basename:
            print u'{0} → {1}'.format(basename, new_basename)
            os.rename(filename, os.path.join(directory, new_basename))
