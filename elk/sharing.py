# -*- coding: utf-8 -*-


import re
import os
import shutil
import urllib

from elk import config
from elk.utils import list_files
from elk.metadata import Metadata


def dropbox_dir(directory):
    return os.path.join(
        os.path.expanduser(config.get('dropbox', 'dir')),
        os.path.basename(directory)
    )


def dropbox_path(directory):
    dp_re = re.compile(r'^.+dropbox', re.I)
    dp_dir = dropbox_dir(directory)

    if not dp_re.match(dp_dir):
        raise ValueError
    return dp_re.sub('', dp_dir).lstrip('/')


def share(directory):
    new_directory = dropbox_dir(directory)
    try:
        shutil.copytree(directory, new_directory)
    except OSError as e:
        if e.errno != 17:  # already exists
            raise

    for filename in list_files(new_directory):
        basename = os.path.basename(filename)

        meta = Metadata(filename)
        caption = meta.get('Headline', meta['Caption-Abstract'])
        caption = unicode(caption or config.get('dropbox', 'default_caption'))
        caption = caption.replace('/', '|')  # special character in UNIX fs

        base, ext = os.path.splitext(basename)
        new_basename = u"{name}:{padding}{caption}{padding}{ext}".format(
            name=base,
            caption=caption,
            ext=ext.lower(),
            padding=u'\xa0' * 10,
        )

        print u'{0} → {1}'.format(basename, new_basename)
        os.rename(filename, os.path.join(new_directory, new_basename))

    print 'https://www.dropbox.com/home/{}'.format(
        urllib.quote(dropbox_path(directory).encode('utf-8'))
    )


def unshare(directory):
    try:
        shutil.rmtree(dropbox_dir(directory))
    except OSError as e:
        if e.errno != 2:  # no such directory
            raise
