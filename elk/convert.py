# -*- coding: utf-8 -*-


from __future__ import division

import os
import shutil
from time import time
from collections import namedtuple
from tempfile import NamedTemporaryFile

from sh import Command

from elk import config
from elk.utils import list_files, notify, to_trash, parse_cmd_args


Names = namedtuple(
    'Names',
    'in_filename in_basename out_filename out_basename dir'
)


def prepare_names(filename, out_ext):
    # original input file
    directory = os.path.dirname(filename)
    basename = os.path.basename(filename)

    # new output file
    base, _ = os.path.splitext(basename)
    out_basename = '{0}.{1}'.format(base, out_ext)
    out_filename = os.path.join(directory, out_basename)

    return Names(filename, basename, out_filename, out_basename, directory)


def convert_multimedia(filename):
    in_ext = os.path.splitext(filename)[1].lstrip('.')
    out_ext = config.get(in_ext, 'out_ext')

    # prepare name and size of the input file
    names = prepare_names(filename, out_ext)
    in_size = os.path.getsize(names.in_filename) / 1024 / 1024  # MB

    # command
    command = Command(config.get(in_ext, 'command'))
    stdout = config.getboolean(in_ext, 'stdout')

    # prepare tmp file
    with NamedTemporaryFile(delete=False) as f:
        tmp_filename = f.name

    # arguments
    args = parse_cmd_args(
        config.get(in_ext, 'params'),
        in_filename=names.in_filename,
        out_filename=tmp_filename
    )
    kwargs = {}
    if stdout:
        kwargs['_out'] = tmp_filename

    # convert
    start = time()
    command(*args, **kwargs)
    t = time() - start

    # calculate statistics, etc.
    out_size = os.path.getsize(names.out_filename) / 1024 / 1024  # MB
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
    line = u'{0}: {1:.1f}MB → {2} {3:.1f}MB, {4:.1f}min, {5:.1f}%'.format(
        names.in_basename, in_size,
        names.out_basename, out_size,
        t / 60, compression
    )
    print line
    if t > 60:  # longer than one minute
        notify("Conversion is complete", line)


def convert(directory):
    print "Converting JPG files..."
    convert_jpg(directory)
    print "Converting MOV files..."
    convert_mov(directory)
    print "Converting AMR files..."
    convert_amr(directory)


def convert_jpg(directory):
    for filename in list_files(directory, exts=['jpg']):
        convert_multimedia(filename)


def convert_amr(directory):
    for filename in list_files(directory, exts=['amr']):
        convert_multimedia(filename)


def convert_mov(directory):
    for filename in list_files(directory, exts=['mov']):
        convert_multimedia(filename)
