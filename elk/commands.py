# -*- coding: utf-8 -*-


import time
from send2trash import send2trash

from elk import config, parallel
from elk.cache import Cache
from elk.filesystem import Directory
from elk.video import Video, VideoEditor
from elk.photo import Album, PhotoEditor, AlbumEditor


def captions(directory):
    """Reads captions of photos."""
    album = Album(directory)

    photos = album.list()
    captions = parallel.map(lambda photo: photo.caption, photos)

    for photo, caption in zip(photos, captions):
        print u'{0}: {1}'.format(photo.name, caption or ' - ')


def captions_fix(directory):
    """Fixes captions of photos."""
    album = Album(directory)
    editor = PhotoEditor()

    for photo in album.list():
        if not photo.caption:
            continue
        old_caption = photo.caption
        photo = editor.fix_caption(photo)
        new_caption = photo.caption or ' - '
        print u'{0}: {1} -> {2}'.format(photo.name, old_caption, new_caption)


def captions_edit(directory):
    """Automates editing captions."""
    album = Album(directory)
    editor = PhotoEditor()

    for photo in album.list():
        old_caption = photo.caption or ' - '
        photo = editor.edit_caption(photo)
        new_caption = photo.caption or ' - '
        print u'{0}: {1} -> {2}'.format(photo.name, old_caption, new_caption)


def captions_wipe(directory):
    """Wipes captions from photos."""
    album = Album(directory)

    def clear_caption(photo):
        photo.caption = None

    photos = album.list()
    parallel.map(clear_caption, photos)

    for photo in photos:
        print u'{0}:  - '.format(photo.name)


def info(directory):
    """Lists album info."""
    album = Album(directory)
    print unicode(album.info)


def info_edit(directory):
    """Automates editing album info."""
    AlbumEditor().edit_info(Album(directory))


def video(directory):
    """Converts all videos."""
    editor = VideoEditor()
    cache = Cache(config.getfilename('cache', 'filename'))

    old_videos = Directory(directory).list(ext='.MOV', cls=Video)

    factor = cache.get('last_mov_time_factor')
    if factor:
        total = 0
        for old_video in old_videos:
            time_est = (old_video.megabytes / factor) / 60
            total += time_est
            print u'{0} estimate: {1:.1f}min'.format(old_video.name, time_est)
        print u'Total estimate: {0:.1f}min\n'.format(total)

    def convert(video):
        start = time.time()
        return editor.convert(video), time.time() - start
    results = parallel.map(convert, old_videos)

    for old_video, (new_video, t) in zip(old_videos, results):
        compression = (old_video.megabytes / new_video.megabytes)
        factor = old_video.megabytes / t

        # print summary
        line = u'{0}: {1:.1f}MB -> {2} {3:.1f}MB, {4:.1f}min, {5:.1f}x'.format(
            old_video.name, old_video.megabytes, new_video.name,
            new_video.megabytes, t / 60, compression
        )
        print line

        # trash the original file
        try:
            send2trash(old_video.filename)
        except OSError:
            pass  # permission denied

    cache['last_mov_time_factor'] = factor
    cache.save()
