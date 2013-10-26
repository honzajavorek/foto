# -*- coding: utf-8 -*-


import os

from elk.utils import list_files
from elk.creation_date import creation_date


def arrange(directory):
    for filename in list_files(directory, exts=['jpg', 'mov'], recursive=True):
        basename = os.path.basename(filename)

        # TODO nekam zaznamenat v jake slozce to puvodne bylo, asi do nejakeho
        # pracovniho souboru primo v nove slozce, append

        print u'{0}: {1}'.format(basename, creation_date(filename))
