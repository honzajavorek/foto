import os

import click

from foto.logger import Logger
from foto.utils import list_files, Metadata, FileFormatError


__all__ = ['captions', 'captions_fix', 'captions_clean']


def captions(directory):
    logger = Logger('captions')

    for filename in list_files(directory, exts=['jpg']):
        basename = os.path.basename(filename)

        meta = Metadata(filename)
        basename_fmt = click.style('{}'.format(basename), bold=True)

        try:
            caption = meta.get_caption()
            logger.log('{}: {}'.format(basename_fmt, caption or ' - '))
        except FileFormatError:
            logger.log('{}:  -  (not an image file)'.format(basename_fmt))


def captions_fix(directory):
    logger = Logger('captions:fix')

    for filename in list_files(directory, exts=['jpg']):
        basename = os.path.basename(filename)

        meta = Metadata(filename)
        try:
            caption = meta.get_caption()
            if not caption:
                continue

            old_caption = caption

            single_quoted = caption[0] in "'" and caption[-1] == "'"
            double_quoted = caption[0] in '"' and caption[-1] == '"'

            if single_quoted or double_quoted:
                caption = caption[1:-1]

            meta.set_caption(caption)

            logger.log('{}: {} → {}'.format(
                click.style(basename, bold=True),
                old_caption,
                click.style(caption, fg='green'),
            ))

        except FileFormatError:
            continue


def captions_clean(directory):
    logger = Logger('captions:clean')

    for filename in list_files(directory, exts=['jpg']):
        basename = os.path.basename(filename)

        meta = Metadata(filename)
        basename_fmt = click.style('{}'.format(basename), bold=True)

        try:
            caption = meta.get_caption()
            meta.remove_caption()
            logger.log(f"{basename_fmt}: {caption or ' - '} →  - ")
        except FileFormatError:
            logger.log('{}:  -  (not an image file)'.format(basename_fmt))
