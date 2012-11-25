# -*- coding: utf-8 -*-


"""Elk.

Usage:
    elk organize [-d]
    elk auto [-d]
    elk upload [-d]
    elk sync [-d]
    elk video [-d]
    elk panorama [-d]
    elk info [-d]
    elk captions [-d]
    elk wipe [info|captions] [-d]
    elk -h|--help
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
    -d                  Debug mode.
"""


import os
import logging as log
from docopt import docopt
from itertools import permutations

from elk import commands
from elk import __version__
from elk.config import Config


def parse_args():
    """Parses arguments and returns them in a list."""
    args = docopt(__doc__, version=__version__)
    args = [cmd for (cmd, is_present) in
            args.items() if is_present]  # keep only names of truthy args
    return args


def setup_logging(debug=False):
    """Basic logging setup."""
    log_format = '[%(levelname)s] %(message)s'
    log_level = log.DEBUG if debug else log.INFO
    log.basicConfig(format=log_format, level=log_level)


def find_command(args):
    """In elk.commands module tries to find a command correspoding
    to given args.
    """
    args_count = len(args)
    if args_count < 1:
        return None
    if args_count == 1:
        return args[0]
    else:
        for ordered_args in permutations(args):
            cmd_name = '_'.join(ordered_args)  # construct function name
            log.debug('Looking for command %s.', cmd_name)
            if hasattr(commands, cmd_name):
                return cmd_name
    return None


def main():
    """Handles arguments parsing and command execution."""
    args = parse_args()
    setup_logging('-d' in args)
    args.remove('-d')
    log.debug('Given args: %r', args)

    cmd_name = find_command(args)
    if cmd_name:
        config = Config()
        current_dir = os.getcwdu()

        log.debug('Current directory is: %s', current_dir)
        log.debug('Executing %r.', cmd_name)

        fn = getattr(commands, cmd_name)
        fn(current_dir, config=config)
    else:
        raise NotImplementedError('No implementation found for given args.')


if __name__ == '__main__':
    main()
