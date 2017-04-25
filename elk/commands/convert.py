import os
import shutil
from time import time
from collections import namedtuple
from tempfile import NamedTemporaryFile
from slugify import slugify

import click
from plumbum import local

from elk import config
from elk.logger import Logger
from elk.utils import list_files, notify, to_trash, parse_cmd_args, Metadata


__all__ = ['convert', 'convert_images', 'convert_audio', 'convert_video']


Names = namedtuple(
    'Names',
    'in_filename in_basename out_filename out_basename dir'
)


def convert(directory):
    logger = Logger('convert')
    logger.log('Converting images')
    convert_images(directory)
    logger.log('Converting video files')
    convert_video(directory)
    logger.log('Converting audio')
    convert_audio(directory)


def convert_images(directory):
    logger = Logger('convert:images')
    convert_multimedia_files(logger, directory, ['jpg'])


def convert_audio(directory):
    logger = Logger('convert:audio')
    convert_multimedia_files(logger, directory, ['amr'])


def convert_multimedia_files(logger, directory, exts):
    for ext in exts:
        for filename in list_files(directory, exts=[ext]):
            options = config['converting'].get(ext)
            if options:
                convert_multimedia(logger, filename, options)
            else:
                logger.log("Unable to find configuration for '{}'".format(ext))
            convert_multimedia(logger, filename, ext)


def convert_video(directory):
    logger = Logger('convert:video')
    for filename in list_files(directory, exts=['mov', 'mp4']):
        config_key = detect_camera(filename)
        if config_key:
            options = config['converting'].get(config_key)
            if options:
                convert_multimedia(logger, filename, options)
            else:
                message = "Unable to find configuration for '{}'"
                logger.log(message.format(config_key))
        else:
            message = "Unable to detect camera model of '{}'"
            logger.log(message.format(os.path.basename(filename)))


def detect_camera(filename):
    _, ext = os.path.splitext(filename)
    ext = ext.lstrip('.').lower()

    meta = Metadata(filename)
    make, model = meta['Make'], meta['Model']

    if make and model:
        return slugify('-'.join([ext, make, model]))

    if ext == 'mov' and meta['VendorID'] == 'Panasonic':
        width = int(meta.get('SourceImageWidth', 0))
        height = int(meta.get('SourceImageHeight', 0))
        if width == 640 and height == 480:
            return 'mov-panasonic-dmc-fz8'

    return None


def convert_multimedia(logger, filename, options):
    in_ext = os.path.splitext(filename)[1].lstrip('.')
    out_ext = options['out_ext']

    # prepare name and size of the input file
    names = prepare_names(filename, out_ext)
    in_size = os.path.getsize(names.in_filename) / 1024 / 1024  # MB

    # command
    command_name = options['command']
    command = local[command_name]
    stdout = options.get('stdout')

    # prepare tmp file
    with NamedTemporaryFile(delete=False) as f:
        tmp_filename = f.name

    # arguments
    wildcards = {
        'in_filename': names.in_filename,
        'out_filename': tmp_filename,
    }
    args = parse_cmd_args(options['params'], **wildcards)
    for arg in args:
        command = command[arg]  # binding arguments to the command
    if stdout:
        command = (command > tmp_filename)  # redirect output to a temp file

    # convert
    logger.log('{} {}'.format(command_name, ' '.join(args)))
    start = time()
    command()
    t = time() - start

    # calculate statistics, etc.
    out_size = os.path.getsize(tmp_filename) / 1024 / 1024  # MB
    compression = 100 - (100 * out_size / in_size)

    # trash the original file, move result
    if in_ext == out_ext and in_size <= out_size:
        # converting within the same format and the conversion had no
        # possitive effect => we can keep the original
        os.unlink(tmp_filename)
    else:
        to_trash(names.in_filename)
        shutil.move(tmp_filename, names.out_filename)

    # print summary
    line = '{0}: {1:.1f}MB → {2} {3:.1f}MB, {4:.1f}min, {5:.1f}%'.format(
        click.style(names.in_basename, bold=True), in_size,
        names.out_basename, out_size,
        t / 60, compression
    )
    logger.log(line)
    if t > 60:  # longer than one minute
        notify('Conversion is complete', line)


def prepare_names(filename, out_ext):
    # original input file
    directory = os.path.dirname(filename)
    basename = os.path.basename(filename)

    # new output file
    base, _ = os.path.splitext(basename)
    out_basename = '{}.{}'.format(base, out_ext)
    out_filename = os.path.join(directory, out_basename)

    return Names(filename, basename, out_filename, out_basename, directory)
