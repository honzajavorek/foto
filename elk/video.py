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
        avconv_params = self.config['avocnv']
        avconv_params = shlex.split(avconv_params)

        name, _ = os.path.splitext(video.filename)
        filename = '.'.join([name, self.config['format']])

        avconv_params = ['-i', video.filename] + avconv_params + [filename]
        avconv(*avconv_params)

        try:
            send2trash(video.filename)
        except OSError:
            pass  # permission denied
        return video.__class__(filename)
