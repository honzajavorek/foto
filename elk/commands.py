# -*- coding: utf-8 -*-


from elk import parallel
from elk.photo import Album, PhotoEditor


def captions(dir, config):
    """Reads captions of photos."""
    config = dict(config.items('album'))
    album = Album(dir, config)

    photos = album.list()
    captions = parallel.map(lambda photo: photo.caption, photos)

    for photo, caption in zip(photos, captions):
        print u'{0}: {1}'.format(photo.name, caption or ' - ')


def fix_captions(dir, config):
    """Fixes captions of photos."""
    config = dict(config.items('album'))
    album = Album(dir, config)
    editor = PhotoEditor()

    def fix_caption(photo):
        caption = photo.caption
        if caption:
            photo = editor.fix_caption(photo)
            new_caption = photo.caption
            return caption, new_caption
        return None, None

    photos = album.list()
    captions = parallel.map(fix_caption, photos)

    for photo, (caption, new_caption) in zip(photos, captions):
        if caption and new_caption:
            print u'{0}: {1} -> {2}'.format(photo.name, caption, new_caption)


def wipe_captions(dir, config):
    """Wipes captions from photos."""
    config = dict(config.items('album'))
    album = Album(dir, config)

    def clear_caption(photo):
        photo.caption = None

    photos = album.list()
    parallel.map(clear_caption, photos)

    for photo in photos:
        print u'{0}:  - '.format(photo.name)
