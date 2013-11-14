# -*- coding: utf-8 -*-


from __future__ import division

import os
import shlex
from time import time
from collections import namedtuple

from sh import avconv

from elk import config
from elk.utils import list_files, notify, to_trash


Names = namedtuple('Names', [
    'in_filename',
    'in_basename',
    'out_filename',
    'out_basename',
    'directory',
])


def prepare_names(filename, out_ext):
    # original input file
    directory = os.path.dirname(filename)
    basename = os.path.basename(filename)

    # new output file
    base, _ = os.path.splitext(basename)
    out_basename = '{0}.{1}'.format(base, out_ext)
    out_filename = os.path.join(directory, out_basename)

    return Names(
        filename,
        basename,
        out_filename,
        out_basename,
        directory,
    )


def convert_multimedia(filename, out_ext, params=None):
    params = params or []

    # prepare name and size of the input file
    names = prepare_names(filename, out_ext)
    in_size = os.path.getsize(names.in_filename) / 1024 / 1024  # MB

    if os.path.exists(names.out_filename):
        print u'EXISTS! {0} → {1}'.format(
            names.in_basename,
            names.out_basename
        )
        return

    # convert
    params = ['-i', names.in_filename] + params + [names.out_filename]
    start = time()
    avconv(*params)
    t = time() - start

    # calculate statistics, etc.
    out_size = os.path.getsize(names.out_filename) / 1024 / 1024  # MB
    compression = (in_size / out_size)

    # print summary
    line = u'{0}: {1:.1f}MB → {2} {3:.1f}MB, {4:.1f}min, {5:.1f}x'.format(
        names.in_basename, in_size,
        names.out_basename, out_size,
        t / 60, compression
    )
    print line
    if t > 60:  # longer than one minute
        notify("Conversion is complete", line)

    # trash the original file
    to_trash(names.in_filename)


def convert(directory):
    print "Converting JPG files..."
    # convert_jpg(directory)
    print "Converting MOV files..."
    convert_mov(directory)
    print "Converting AMR files..."
    convert_amr(directory)


def convert_amr(directory):
    for filename in list_files(directory, exts=['amr']):
        convert_multimedia(filename, 'mp3')


def convert_mov(directory):
    params = shlex.split(config.get('video', 'mov'))
    out_ext = params[params.index('-f') + 1]

    for filename in list_files(directory, exts=['mov']):
        convert_multimedia(filename, out_ext, params=params)
