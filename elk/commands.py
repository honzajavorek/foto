# -*- coding: utf-8 -*-


import time
from send2trash import send2trash

from elk import parallel
from elk.cache import Cache
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


def captions_fix(directory, config):
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


def captions_wipe(directory, config):
    """Wipes captions from photos."""
    config = dict(config.items('album'))
    album = Album(directory, config)

    def clear_caption(photo):
        photo.caption = None

    photos = album.list()
    parallel.map(clear_caption, photos)

    for photo in photos:
        print u'{0}:  - '.format(photo.name)


def info(directory, config):
    """Lists album info."""
    config = dict(config.items('album'))
    album = Album(directory, config)
    print unicode(album.info)


def video(directory, config):
    """Converts all videos."""
    editor = VideoEditor(config=dict(config.items('video')))
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
