# -*- coding: utf-8 -*-


from __future__ import division

import os
import shlex
from time import time

from sh import avconv
from send2trash import send2trash

from elk import config
from elk.utils import list_files, notify


def optimize(directory):
    print "Optimizing JPG files..."
    # optimize_jpg(directory)
    print "Optimizing MOV files..."
    optimize_mov(directory)


def optimize_mov(directory):
    params = shlex.split(config.get('video', 'mov'))
    output_format = params[params.index('-f') + 1]

    for original_filename in list_files(directory, exts=['mov']):
        # prepare name and saze of the input file
        original_basename = os.path.basename(original_filename)
        original_size = os.path.getsize(original_filename) / 1024 / 1024  # MB

        # build name of the output file
        base, _ = os.path.splitext(original_basename)
        new_basename = '{0}.{1}'.format(base, output_format)
        new_filename = os.path.join(directory, new_basename)

        # convert video
        params = ['-i', original_filename] + params + [new_filename]
        start = time()
        avconv(*params)
        t = time() - start

        # calculate statistics, etc.
        new_size = os.path.getsize(new_filename) / 1024 / 1024  # MB
        compression = (original_size / new_size)

        # print summary
        line = u'{0}: {1:.1f}MB → {2} {3:.1f}MB, {4:.1f}min, {5:.1f}x'.format(
            original_basename, original_size,
            new_basename, new_size,
            t / 60, compression
        )
        print line
        notify("Video conversion is complete", line)

        # trash the original file
        try:
            send2trash(original_filename)
        except OSError:
            pass  # permission denied
