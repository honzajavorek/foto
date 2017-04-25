import os

from elk.logger import Logger
from elk.commands.convert import convert
from elk.commands.clean import clean
from elk.commands.info import info_restore
from elk.commands.captions import captions_fix
from elk.commands.names import names_fix, names_sort


__all__ = ['auto']


def auto(directory):
    logger = Logger('auto')

    logger.log('Restoring album info')
    info_restore(directory)

    logger.log('Removing rubbish')
    clean(directory)

    logger.log('Fixing filenames')
    names_fix(directory)

    logger.log('Sorting filenames')
    names_sort(directory)

    logger.log('Fixing captions')
    captions_fix(directory)

    logger.log('Converting')
    convert(directory)
