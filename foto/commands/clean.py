import os

import click

from foto import config
from foto.logger import Logger
from foto.utils import list_files, to_trash, is_corrupted_file


__all__ = ['clean']


RUBBISH = [basename.lower() for basename in config['rubbish']]


def clean(directory):
    logger = Logger('clean')

    for filename in list_files(directory):
        basename = os.path.basename(filename)
        basename_fmt = click.style(basename, bold=True)

        if basename.lower() in RUBBISH:
            logger.log(basename_fmt + ' → trash (rubbish)')
            to_trash(filename)

        elif is_corrupted_file(filename):
            logger.log(basename_fmt + ' → trash (corrupted file)')
            to_trash(filename)
