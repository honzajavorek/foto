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
    elk info:edit
    elk captions
    elk captions:wipe
    elk captions:fix
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
    info:edit           Edit current directory info.
    captions            Print all captions in current directory.
    captions:wipe       Wipe all captions in current directory.
    captions:fix        Fix all captions in current directory.
    -h --help           Show this screen.
    --version           Show elk version.
"""


import os
import sys
import logging
from docopt import docopt
from contextlib import contextmanager

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
    """Basic :mod:`logging` setup."""
    format = '[%(levelname)s] %(message)s'
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(format=format, level=level)


def find_command(args):
    """Tries to find a command correspoding to given args
    in :mod:`elk.commands` module.
    """
    args_count = len(args)
    if args_count < 1:
        return None
    if args_count == 1:
        return args[0].replace(':', '_')
    return None


def run_command(cmd_name, directory=None):
    """Runs command from :mod:`elk.commands` module."""
    config = Config()
    directory = directory or os.getcwdu()

    logging.debug('Directory: %s', directory)
    logging.debug('Executing %r.', cmd_name)

    try:
        fn = getattr(commands, cmd_name)
    except AttributeError:
        raise NotImplementedError('No implementation found.')
    fn(directory, config=config)


@contextmanager
def exc_capture():
    """Exception capturing wrapper."""
    try:
        yield
    except Exception as e:
        logging.exception(e)
        sys.exit(1)


def main():
    """Handles arguments parsing and command execution."""
    args = parse_args()

    setup_logging(os.getenv('ELK_DEBUG'))
    logging.debug('Given args: %r', args)

    with exc_capture():
        cmd_name = find_command(args)
        if cmd_name:
            run_command(cmd_name)
        else:
            raise NotImplementedError('No implementation found.')


if __name__ == '__main__':
    main()
