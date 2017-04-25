import os

import click

from elk import config
from elk.logger import Logger
from elk.utils import list_files, to_trash, is_corrupted_file


__all__ = ['clean']


RUBBISH = [basename.lower() for basename in config['rubbish']]


def clean(directory):
    logger = Logger('clean')

    for filename in list_files(directory):
        basename = os.path.basename(filename)
        if basename.lower() in RUBBISH:
            logger.log(click.style(basename, bold=True) + ' → trash (rubbish)')
            to_trash(filename)
        elif is_corrupted_file(filename):
            logger.log(click.style(basename, bold=True) + ' → trash (corrupted file)')
            to_trash(filename)
