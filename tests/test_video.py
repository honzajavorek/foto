# -*- coding: utf-8 -*-


from elk import video, config
from .base import VideoTestCase


class VideoEditorTest(VideoTestCase):

    def test_convert(self):
        c = dict(config.Config().items('video'))

        ve = video.VideoEditor(c)
        orig = video.Video(self.filename)
        orig_bytes = orig.bytes

        new = ve.convert(orig)

        self.assertTrue(new.filename.endswith('avi'))
        self.assertGreater(orig_bytes, new.bytes)
