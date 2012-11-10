# -*- coding: utf-8 -*-


import os

from elk import cache
from .utils import FileTestCase


class CacheTest(FileTestCase):

    def test_get_empty(self):
        c = cache.Cache(self.filename)
        self.assertEqual(c.get('whatever', None), None)

    def test_set_get(self):
        c = cache.Cache(self.filename)
        sample = {'!!!': 59596, 'Ostrava': True}
        c['whatever'] = sample
        c.save()
        self.assertGreater(os.path.getsize(self.filename), 0)

        c = cache.Cache(self.filename)
        self.assertEqual(c['whatever'], sample)

    def test_non_existing(self):
        os.unlink(self.filename)
        c = cache.Cache(self.filename)
        sample = [True, False]
        c['whatever'] = sample
        c.save()
        self.assertGreater(os.path.getsize(self.filename), 0)

        c = cache.Cache(self.filename)
        self.assertEqual(c['whatever'], sample)
