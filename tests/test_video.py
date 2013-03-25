# -*- coding: utf-8 -*-


from elk import video
from .base import VideoTestCase


class VideoEditorTest(VideoTestCase):

    def test_convert(self):
        ve = video.VideoEditor()
        orig = video.Video(self.filename)
        orig_bytes = orig.bytes

        new = ve.convert(orig)

        self.assertTrue(new.filename.endswith('avi'))
        self.assertGreater(orig_bytes, new.bytes)
