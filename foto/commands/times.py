import os

import click

from foto import config
from foto.logger import Logger
from foto.utils import (list_files, Metadata, shift_datetime, FileFormatError,
                        format_datetime)


__all__ = ['times_fix']


TAGS = (
    'CreateDate',
    'DateTimeCreated',
    'TimeCreated',
    'DigitalCreationDateTime',
    'DigitalCreationTime',
    'DateTimeOriginal',
    'ModifyDate',
    'TrackCreateDate',
    'TrackModifyDate',
    'MediaCreateDate',
    'MediaModifyDate',
)
LONGEST_TAG_LEN = len('SubSec') + max(*map(len, TAGS))
LONGEST_DT_LEN = 32


def times_fix(directory):
    logger = Logger('times:fix')

    filenames = list_files(directory, exts=config['media_exts'])
    hours = logger.prompt(
        'Specify how to shift hours: (for example +3 or -2)', type=int)
    if hours == 0:
        return

    for basename, tag, val, val_shifted in shift(filenames, hours):
        logger.log('{}: {} {} → {}'.format(
            click.style(basename, bold=True),
            click.style(tag.ljust(LONGEST_TAG_LEN), bold=True),
            *diff(
                format_datetime(val).ljust(LONGEST_DT_LEN),
                format_datetime(val_shifted).ljust(LONGEST_DT_LEN),
            ),
        ))


def shift(filenames, hours):
    for filename in filenames:
        basename = os.path.basename(filename)
        meta = Metadata(filename)
        try:
            for tag in TAGS:
                tag, val = meta.getfirst(['SubSec' + tag, tag])
                if val:
                    val_shifted = shift_datetime(val, hours)
                    yield (basename, tag, val, val_shifted)
                    meta[tag] = val_shifted
        except FileFormatError:
            continue


def diff(s1, s2):
    if len(s1) != len(s2):
        raise ValueError('Can diff only strings of the same length')

    s1_colored = []
    s2_colored = []

    for i in range(len(s1)):
        if s1[i] == s2[i]:
            s1_colored.append(s1[i])
            s2_colored.append(s2[i])
        else:
            s1_colored.append(click.style(s1[i], fg='red', bold=True))
            s2_colored.append(click.style(s2[i], fg='green', bold=True))

    return (''.join(s1_colored), ''.join(s2_colored))
