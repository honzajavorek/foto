# -*- coding: utf-8 -*-


import os
import re

from elk import config
from elk.utils import list_files
from elk.creation_datetime import creation_datetime


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


def names_sort(directory):
    exts = re.split(r'[,\s]+', config.get('filenames', 'media_exts'))

    unsorted_filenames = list_files(directory, exts=exts)
    filenames = sorted(
        unsorted_filenames,
        key=lambda filename: creation_datetime(filename)
    )

    if filenames == unsorted_filenames:
        return  # already sorted

    n_maxlen = len(str(len(filenames)))
    for n, filename in enumerate(filenames):
        basename = os.path.basename(filename)
        prefix = str(n).zfill(n_maxlen) + '-'

        # move
        new_basename = prefix + basename
        new_filename = os.path.join(directory, new_basename)
        if os.path.exists(new_filename):
            print u'EXISTS! {0} → {1}'.format(basename, new_basename)
            return
        else:
            print u'{0} → {1}'.format(basename, new_basename)
            os.rename(filename, new_filename)
