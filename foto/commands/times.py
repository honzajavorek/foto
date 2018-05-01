import os

import click

from foto import config
from foto.logger import Logger
from foto.utils import (list_files, detect_camera, Metadata, shift_datetime,
                        FileFormatError, format_datetime)


__all__ = ['times_fix']


TAGS = (
    'CreateDate',
    'DateTimeCreated',
    'TimeCreated',
    'DigitalCreationDateTime',
    'DigitalCreationTime',
    'DateTimeOriginal',
    'ModifyDate',
)
LONGEST_TAG_LEN = len('SubSec') + max(*map(len, TAGS))
LONGEST_DT_LEN = 32


def times_fix(directory):
    logger = Logger('times:fix')
    logger.log('Looking for camera types')

    filenames = list_files(directory, exts=config['media_exts'])
    cameras = list(sorted(set(filter(None, map(detect_camera, filenames)))))

    if not len(cameras):
        logger.err('No cameras found')
        return

    if len(cameras) == 1:
        logger.warn('Just one camera found')
        chosen_camera = cameras[0]
    else:
        for i, camera in enumerate(cameras):
            logger.log('{} ... {} {}'.format(
                click.style(str(i + 1), fg='blue', bold=True), *camera
            ))

        chosen_camera_no = -1
        while chosen_camera_no < 0 or chosen_camera_no >= len(cameras):
            chosen_camera_no = logger.prompt('Choose camera type number', type=int) - 1
        chosen_camera = cameras[chosen_camera_no]

    hours = logger.prompt((
        'Specify how to shift hours for photos '
        'made by the {} {}: (for example +3 or -2)'.format(*chosen_camera)
    ), type=int)
    if hours == 0:
        return

    for basename, tag, val, val_shifted in shift(filenames, chosen_camera, hours):
        logger.log('{}: {} {} → {}'.format(
            click.style(basename, bold=True),
            click.style(tag.ljust(LONGEST_TAG_LEN), bold=True),
            *diff(
                format_datetime(val).ljust(LONGEST_DT_LEN),
                format_datetime(val_shifted).ljust(LONGEST_DT_LEN),
            ),
        ))


def shift(filenames, camera, hours):
    for filename in filenames:
        detected_camera = detect_camera(filename)
        if not detected_camera or detected_camera != camera:
            continue
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
