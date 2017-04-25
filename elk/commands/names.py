import os
import re

import click

from elk import config
from elk.logger import Logger
from elk.utils import list_files, creation_datetime


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

    exts = config['media_exts']
    unsorted_filenames = list_files(directory, exts=exts)

    all_prefixed = all(re.match(r'\d+\-', os.path.basename(filename))
                       for filename in unsorted_filenames)
    if all_prefixed:
        logger.log('Looks like already sorted')  # keep manual changes
        return

    datetimes = frozenset(map(creation_datetime, unsorted_filenames))
    if len(datetimes) < len(unsorted_filenames):
        logger.err(
            'Multiple files were created in the same time, '
            'sorting would create a mess'
        )
        return

    filenames = sorted(unsorted_filenames, key=creation_datetime)
    if filenames == unsorted_filenames:
        logger.log('Already sorted')
        return

    n_maxlen = len(str(len(filenames)))
    for n, filename in enumerate(filenames):
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
