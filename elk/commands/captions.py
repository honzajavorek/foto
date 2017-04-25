import os

import click

from elk.logger import Logger
from elk.utils import list_files, Metadata, FileFormatError


__all__ = ['captions', 'captions_fix']


def captions(directory):
    logger = Logger('captions')

    for filename in list_files(directory, exts=['jpg']):
        basename = os.path.basename(filename)

        meta = Metadata(filename)
        basename_formatted = click.style('{}'.format(basename), bold=True)

        try:
            caption = meta.get('Headline', meta['Caption-Abstract'])
            logger.log('{}: {}'.format(basename_formatted, caption or ' - '))
        except FileFormatError:
            logger.log('{}:  -  (not an image file)'.format(basename_formatted))


def captions_fix(directory):
    logger = Logger('captions:fix')

    for filename in list_files(directory, exts=['jpg']):
        basename = os.path.basename(filename)

        meta = Metadata(filename)
        try:
            caption = meta.get('Headline', meta['Caption-Abstract']) or ''

            if not caption:
                continue

            old_caption = caption

            single_quoted = caption[0] in "'" and caption[-1] == "'"
            double_quoted = caption[0] in '"' and caption[-1] == '"'

            if single_quoted or double_quoted:
                caption = caption[1:-1]

            meta['Headline'] = caption
            del meta['Caption-Abstract']

            logger.log('{}: {} → {}'.format(
                click.style(basename, bold=True),
                old_caption,
                click.style(caption, fg='green'),
            ))

        except FileFormatError:
            continue
