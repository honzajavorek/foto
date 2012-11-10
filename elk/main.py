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
    auto                Do everything automatically.

    upload              Upload to remote storages.
    sync                Synchronize captions and info with remote storages.
    video               Convert all videos.
    panorama            Detect and convert all panoramas.
    info                Print info.
    captions            Print all captions.

    wipe info           Wipe info.
    wipe captions       Wipe all captions.

    -h --help           Show this screen.
    --version           Show version.
"""


from docopt import docopt

from elk import __version__


def main():
    args = docopt(__doc__, version=__version__)
    print args


if __name__ == '__main__':
    main()
