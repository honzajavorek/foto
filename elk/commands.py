# -*- coding: utf-8 -*-


from elk import parallel
from elk.filesystem import Directory
from elk.photo import Album, PhotoEditor
from elk.video import Video, VideoEditor


def captions(directory, config):
    """Reads captions of photos."""
    config = dict(config.items('album'))
    album = Album(directory, config)

    photos = album.list()
    captions = parallel.map(lambda photo: photo.caption, photos)

    for photo, caption in zip(photos, captions):
        print u'{0}: {1}'.format(photo.name, caption or ' - ')


def fix_captions(directory, config):
    """Fixes captions of photos."""
    config = dict(config.items('album'))
    album = Album(directory, config)
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


def wipe_captions(directory, config):
    """Wipes captions from photos."""
    config = dict(config.items('album'))
    album = Album(directory, config)

    def clear_caption(photo):
        photo.caption = None

    photos = album.list()
    parallel.map(clear_caption, photos)

    for photo in photos:
        print u'{0}:  - '.format(photo.name)


def video(directory, config):
    """Converts all videos."""
    config = dict(config.items('video'))
    editor = VideoEditor(config=config)

    directory = Directory(directory)

    def convert(video):
        return editor.convert(video)

    old_videos = directory.list(ext='.MOV', cls=Video)
    new_videos = parallel.map(convert, old_videos)

    for old_video, new_video in zip(old_videos, new_videos):
        print u'{0}: {1}'.format(old_video.name, new_video.name)
