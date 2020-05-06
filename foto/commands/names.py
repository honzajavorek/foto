import os
import re
from multiprocessing import Pool

import click

from foto import config
from foto.logger import Logger
from foto.utils import list_files, creation_datetime, to_naive


__all__ = ['names_fix', 'names_sort']


def names_fix(directory):
    logger = Logger('names:fix')

    for filename in list_files(directory):
        basename = os.path.basename(filename)

        base, ext = os.path.splitext(basename)
        if ext.lower() == '.jpeg':
            ext = '.jpg'
        new_basename = base + ext.lower()

        if basename != new_basename:
            logger.log('{} → {}'.format(
                basename,
                click.style(new_basename, fg='green')
            ))
            os.rename(filename, os.path.join(directory, new_basename))


def names_sort(directory):
    logger = Logger('names:sort')

    exts = config['photo_exts']
    unsorted_filenames = list_files(directory, exts=exts)

    all_prefixed = all(re.match(r'\d+\-', os.path.basename(filename))
                       for filename in unsorted_filenames)
    if all_prefixed:
        logger.log('Looks like already sorted')  # keep manual changes
        return

    datetimes = Pool().map(creation_datetime, unsorted_filenames)
    datetimes = map(to_naive, datetimes)
    filenames_by_datetimes = list(zip(datetimes, unsorted_filenames))
    filenames = [
        filename for datetime, filename in sorted(filenames_by_datetimes)
    ]
    if filenames == unsorted_filenames:
        logger.log('Already sorted')
        return

    n_maxlen = len(str(len(filenames)))
    for n, filename in enumerate(filenames, start=1):
        basename = os.path.basename(filename)
        prefix = str(n).zfill(n_maxlen) + '-'

        # move
        new_basename = prefix + basename
        new_filename = os.path.join(directory, new_basename)
        if os.path.exists(new_filename):
            logger.err('Exists! {} → {}'.format(basename, new_basename))
            return
        else:
            logger.log('{} → {}'.format(
                basename,
                click.style(new_basename, fg='green')
            ))
            os.rename(filename, new_filename)


def names_unsort(directory):
    logger = Logger('names:unsort')

    exts = config['media_exts']
    sorted_filenames = list_files(directory, exts=exts)

    for filename in sorted_filenames:
        basename = os.path.basename(filename)
        if not re.match(r'\d+\-', os.path.basename(filename)):
            logger.log('{}'.format(basename))
            continue

        # move
        new_basename = re.sub(r'\d+\-', '', basename)
        new_filename = os.path.join(directory, new_basename)
        if os.path.exists(new_filename):
            logger.err('Exists! {} → {}'.format(basename, new_basename))
            return
        else:
            logger.log('{} → {}'.format(
                basename,
                click.style(new_basename, fg='green')
            ))
            os.rename(filename, new_filename)
