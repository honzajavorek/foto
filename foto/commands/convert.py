import os
import re
import shutil
from time import time
from collections import namedtuple
from tempfile import NamedTemporaryFile

import click
from plumbum import local
from slugify import slugify

from foto import config
from foto.logger import Logger
from foto.utils import (list_files, notify, to_trash, parse_cmd_args, Metadata)


__all__ = ['convert', 'convert_images', 'convert_audio', 'convert_video']


MOTOROLA_RE = re.compile(r'\d{4}\-\d{2}\-\d{2} \d{2}\.\d{2}\.\d{2}')


Names = namedtuple(
    'Names',
    'in_filename in_basename out_filename out_basename dir metadata'
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
    convert_multimedia_files(logger, directory, config['photo_exts'])


def convert_audio(directory):
    logger = Logger('convert:audio')
    convert_multimedia_files(logger, directory, config['audio_exts'])


def convert_multimedia_files(logger, directory, exts):
    for ext in exts:
        for filename in list_files(directory, exts=[ext]):
            options = config['converting'].get(ext)
            if options:
                options.setdefault('export_metadata', False)
                convert_multimedia(logger, filename, options)
            else:
                logger.log("Unable to find configuration for '{}'".format(ext))


def convert_video(directory):
    logger = Logger('convert:video')
    for filename in list_files(directory, exts=config['video_exts']):
        basename = os.path.basename(filename)

        converted = False
        for config_key in get_config_key(filename):
            message = "{}: Trying configuration '{}'"
            logger.log(message.format(click.style(basename, bold=True),
                                      config_key))
            options = config['converting'].get(config_key)
            if options:
                options.setdefault('export_metadata', True)
                convert_multimedia(logger, filename, options)
                converted = True
                break

        if not converted:
            message = "{}: Unable to detect configuration"
            logger.log(message.format(click.style(basename, bold=True)))


def get_config_key(filename):
    basename, ext = os.path.splitext(os.path.basename(filename))
    ext = ext.lstrip('.').lower()

    meta = Metadata(filename)
    make, model = meta['Make'], meta['Model']

    if make and model:
        parts = [ext, make, model]
        yield slugify('-'.join(parts))

    elif ext == 'mp4' and MOTOROLA_RE.match(basename):
        width = int(meta.get('SourceImageWidth', 0))
        height = int(meta.get('SourceImageHeight', 0))
        if width == 1920 and height == 1080:
            yield 'mp4-motorola-xt1069'

    elif ext == 'mov' and meta['VendorID'] == 'Panasonic':
        width = int(meta.get('SourceImageWidth', 0))
        height = int(meta.get('SourceImageHeight', 0))
        if width == 640 and height == 480:
            yield 'mov-panasonic-dmc-fz8'

    yield ext


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

    if in_ext == out_ext and in_size <= out_size:
        # converting within the same format and the conversion had no
        # possitive effect => we can keep the original
        os.unlink(tmp_filename)
    else:
        # write metadata file
        if options.get('export_metadata'):
            meta = Metadata(names.in_filename)
            logger.log('{0}: writing metadata backup'.format(
                click.style(names.metadata, bold=True)
            ))
            with open(names.metadata, 'w') as f:
                f.write(meta.to_xml())

        # trash the original file, move result
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
    metadata = '{}.xml'.format(base)

    return Names(filename, basename, out_filename, out_basename,
                 directory, metadata)
