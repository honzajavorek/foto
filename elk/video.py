# -*- coding: utf-8 -*-


import os
import shlex
from sh import avconv
from send2trash import send2trash

from elk.filesystem import File, FileEditor


class Video(File):
    pass


class VideoEditor(FileEditor):

    def __init__(self, config):
        if 'avocnv' not in config:
            raise ValueError("Key 'avocnv' is missing in config given.")
        if 'format' not in config:
            raise ValueError("Key 'format' is missing in config given.")
        super(VideoEditor, self).__init__(config)

    def convert(self, video):
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
