# -*- coding: utf-8 -*-


"""Elk.

Usage:
    elk organize
    elk auto
    elk upload
    elk sync
    elk video
    elk panorama
    elk info
    elk captions
    elk wipe [ info | captions ]
    elk -h | --help
    elk --version

Options:
    organize            Take all mess in current directory and place
                        it into directories where each of them represents
                        a single day.
    auto                Automatically process current directory.
    upload              Upload current directory to remote storages.
    sync                Synchronize captions and info in current directory
                        with remote storages.
    video               Convert all videos in current directory.
    panorama            Detect and convert all panoramas in current directory.
    info                Print current directory info.
    captions            Print all captions in current directory.
    wipe info           Wipe current directory info.
    wipe captions       Wipe all captions in current directory.
    -h --help           Show this screen.
    --version           Show elk version.
"""


import os
import logging as log
from docopt import docopt
from itertools import permutations

from elk import commands
from elk import __version__
from elk.config import Config


def main():
    # setup logging
    log_format = '[%(levelname)s] %(message)s'
    log_level = log.DEBUG
    log.basicConfig(format=log_format, level=log_level)

    # parse arguments
    args = docopt(__doc__, version=__version__)
    args = [cmd for (cmd, is_present) in
            args.items() if is_present]  # keep only names of truthy args
    log.debug('Given args: %r', args)

    # look for valid combination of arguments
    for ordered_args in permutations(args):
        cmd_name = '_'.join(ordered_args)  # construct function name
        log.debug('Looking for command %s.', cmd_name)
        if hasattr(commands, cmd_name):
            # function name exists, call it as a command
            config = Config()
            current_dir = os.getcwdu()

            log.debug('Current directory is: %s', current_dir)
            log.debug('Executing %r.', cmd_name)

            fn = getattr(commands, cmd_name)
            fn(current_dir, config=config)
            return

    # function name not found
    raise NotImplementedError('No implementation found for given arguments.')


if __name__ == '__main__':
    main()
