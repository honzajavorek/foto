# -*- coding: utf-8 -*-


import re
import os

from elk import config
from elk.convert import convert
from elk.captions import captions_fix
from elk.utils import list_files, to_trash
from elk.names import names_fix, names_sort


def auto(directory):
    print "Removing rubbish..."
    rubbish_names = re.split(r'[,\s]+', config.get('filenames', 'rubbish'))
    for filename in list_files(directory):
        basename = os.path.basename(filename)
        if basename in rubbish_names:
            print u'RUBBISH: {0}'.format(basename)
            to_trash(filename)

    print "Fixing filenames..."
    names_fix(directory)

    print "Sorting filenames..."
    names_sort(directory)

    print "Fixing captions..."

    captions_fix(directory)
    convert(directory)
