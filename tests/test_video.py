# -*- coding: utf-8 -*-


from elk import video, config
from .utils import VideoTestCase


class VideoEditorTest(VideoTestCase):

    def test_resize(self):
        c = dict(config.Config().items('video'))

        ve = video.VideoEditor(c)
        orig_v = video.Video(self.filename)

        new_v = ve.convert(orig_v)

        self.assertTrue(new_v.filename.endswith(c['format']))
        self.assertGreater(orig_v.bytes, new_v.bytes)
