# -*- coding: utf-8 -*-


import os
import shlex
from sh import avconv

from elk import config
from elk.filesystem import File, FileEditor


class Video(File):
    """Video abstraction object based on :class:`~elk.filesystem.File`."""
    pass


class VideoEditor(FileEditor):
    """Manipulates :class:`Video` objects."""

    def convert(self, video):
        """Converts video to more optimized format. Converted
        files are not immediately removed, but sent to trash.
        """
        if not config.has_option('video', video.extension):
            message = ('No configuration for '
                       'encoding of {0}.'.format(video.extension))
            raise NotImplementedError(message)

        params = config.get('video', video.extension)

        params = shlex.split(params)
        output_format = params[params.index('-f') + 1]

        name, _ = os.path.splitext(video.filename)
        new_video = video.__class__(name + '.' + output_format,
                                    new_unique=True)

        params = ['-i', video.filename] + params + [new_video.filename]
        avconv(*params)

        return new_video
