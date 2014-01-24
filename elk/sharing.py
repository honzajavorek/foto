# -*- coding: utf-8 -*-


import re
import os
import urllib

from elk import config


def dropbox_dir(directory):
    return os.path.join(
        os.path.expanduser(config.get('general', 'dropbox_dir')),
        os.path.basename(directory)
    )


def dropbox_path(directory):
    dp_re = re.compile(r'^.+dropbox', re.I)
    dp_dir = dropbox_dir(directory)

    if not dp_re.match(dp_dir):
        raise ValueError
    return dp_re.sub('', dp_dir).lstrip('/')


def share(directory):
    try:
        os.symlink(directory, dropbox_dir(directory))
    except OSError as e:
        if e.errno != 17:  # already exists
            raise
    print 'https://www.dropbox.com/home/{}'.format(
        urllib.quote(dropbox_path(directory).encode('utf-8'))
    )


def unshare(directory):
    os.unlink(dropbox_dir(directory))
