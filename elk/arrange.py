# -*- coding: utf-8 -*-


import re
import os

from elk import config
from elk.utils import list_files, season
from elk.creation_datetime import creation_datetime


def arrange(directory):
    dir_mode = os.stat(directory).st_mode
    exts = re.split(r'[,\s]+', config.get('filenames', 'media_exts'))

    for filename in list_files(directory, exts=exts, recursive=True):
        basename = os.path.basename(filename)
        date = creation_datetime(filename).date()

        # create new directory with date and season hint
        new_dir_basename = u'{0:%Y-%m-%d} {1}'.format(date, season(date))
        new_dir_filename = os.path.join(directory, new_dir_basename)
        try:
            os.makedirs(new_dir_filename, dir_mode)
        except OSError as e:
            if e.errno != 17:  # file already exists
                raise

        # create arrange file with index of moved files
        index_basename = config.get('arrange', 'index_basename')
        index_filename = os.path.join(new_dir_filename, index_basename)
        with open(index_filename, 'a') as f:
            f.write(u"{0}\n".format(filename).encode('utf-8'))

        # move
        new_filename = os.path.join(new_dir_filename, basename)
        filenames = [f.replace(directory, '').lstrip('/') for f
                     in [filename, new_filename]]
        if os.path.exists(new_filename):
            print u'EXISTS! {0} → {1}'.format(*filenames)
            return
        else:
            print u'{0} → {1}'.format(*filenames)
            os.rename(filename, new_filename)
