# -*- coding: utf-8 -*-


"""Elk.

Usage:
    elk arrange
    elk auto [-r]
    elk convert [-r]
    elk convert:jpg [-r]
    elk convert:mov [-r]
    elk convert:amr [-r]
    elk captions [-r]
    elk captions:fix [-r]
    elk names:fix [-r]
    elk names:sort [-r]
    elk cover <photo> [-r]
    elk -h|--help
    elk --version

Options:
    arrange             Take all mess in current directory and place
                        it into directories where each of them represents
                        a single day.
    auto                Does all standard operations with photos and videos
                        in current directory.
    convert             Converts all photos and videos in current directory.
    convert:jpg         Optimizes all JPG photos in current directory.
    convert:mov         Converts all MOV videos to AVIs in current directory.
    convert:amr         Converts all AMR sounds to MP3s in current directory.
    captions            Print all captions in current directory.
    captions:fix        Fix all captions in current directory.
    names:fix           Fix all filenames in current directory.
    names:sort          Rename all files in current directory so they are
                        sorted by date & time.
    cover               Set given photo as cover photo.
    -r                  Perform given command for each album in current
                        directory.
    -h --help           Show this screen.
    --version           Show elk version.
"""


import os
from docopt import docopt

from elk import __version__
from elk.utils import list_dirs


command_map = {
    'arrange': 'elk.arrange.arrange',
    'auto': 'elk.auto.auto',
    'convert': 'elk.convert.convert',
    'convert:jpg': 'elk.convert.convert_jpg',
    'convert:mov': 'elk.convert.convert_mov',
    'convert:amr': 'elk.convert.convert_amr',
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

    if '-r' in args:
        args.remove('-r')
        dirs = list_dirs(os.getcwdu())
    else:
        dirs = [os.getcwdu()]

    cmd = import_command(command_map[args[0]])
    try:
        for directory in dirs:
            print 'DIRECTORY:', os.path.basename(directory)
            cmd(directory, *args[1:])
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
