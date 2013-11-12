# -*- coding: utf-8 -*-


"""Elk.

Usage:
    elk arrange
    elk auto
    elk optimize
    elk optimize:jpg
    elk optimize:mov
    elk captions
    elk captions:fix
    elk names:fix
    elk names:sort
    elk cover <photo>
    elk -h|--help
    elk --version

Options:
    arrange             Take all mess in current directory and place
                        it into directories where each of them represents
                        a single day.
    auto                Does all standard operations with photos and videos
                        in current directory.
    optimize            Optimizes all photos and videos in current directory.
    optimize:jpg        Optimizes all photos in current directory.
    optimize:mov        Optimizes all videos in current directory.
    captions            Print all captions in current directory.
    captions:fix        Fix all captions in current directory.
    names:fix           Fix all filenames in current directory.
    names:sort          Rename all files in current directory so they are
                        sorted by date & time.
    cover               Set given photo as cover photo.
    -h --help           Show this screen.
    --version           Show elk version.
"""


import os
from docopt import docopt

from elk import __version__


command_map = {
    'arrange': 'elk.arrange.arrange',
    'auto': 'elk.auto.auto',
    'optimize': 'elk.optimize.optimize',
    'optimize:mov': 'elk.optimize.optimize_mov',
    'captions': 'elk.captions.captions',
    'captions:fix': 'elk.captions.captions_fix',
    'captions:edit': 'elk.captions.captions_edit',
    'names:fix': 'elk.names.names_fix',
    'names:sort': 'elk.names.names_sort',
}


def parse_args():
    """Parses arguments and returns them in a list."""
    args = docopt(__doc__, version=__version__)
    args = [cmd for (cmd, is_present) in
            args.items() if is_present]  # keep only names of truthy args
    return args


def import_command(full_name):
    components = full_name.split('.')
    mod_name = '.'.join(components[0:-1])
    func_name = components[-1]
    module = __import__(mod_name, fromlist=[func_name])
    return getattr(module, func_name)


def main():
    """Handles parsing of arguments and execution of command."""
    args = parse_args()
    directory = os.getcwdu()

    cmd = import_command(command_map[args[0]])
    try:
        cmd(directory, *args[1:])
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
