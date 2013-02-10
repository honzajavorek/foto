# -*- coding: utf-8 -*-


import os
import shlex
from sh import avconv
from send2trash import send2trash

from elk.filesystem import File, FileEditor


class Video(File):
    """Video abstraction object based on :class:`~elk.filesystem.File`."""
    pass


class VideoEditor(FileEditor):
    """Manipulates :class:`Video` objects."""

    def __init__(self, config):
        assert 'avocnv' in config
        assert 'format' in config
        super(VideoEditor, self).__init__(config)

    def convert(self, video):
        """Converts video to more optimized format. Converted
        files are not immediately removed, but sent to trash.
        """
        params = self.config['avocnv']
        params = shlex.split(params)

        name, _ = os.path.splitext(video.filename)
        new_video = video.__class__(name + '.' + self.config['format'],
                                    new_unique=True)

        params = ['-i', video.filename] + params + [new_video.filename]
        avconv(*params)

        try:
            send2trash(video.filename)
        except OSError:
            pass  # permission denied
        return new_video
