# -*- coding: utf-8 -*-


import os

from elk import photo
from .base import FileTestCase, PhotoTestCase


class MetadataTest(PhotoTestCase):

    def test_get_empty(self):
        metadata = photo.Metadata(self.filename)
        self.assertEqual(metadata['Headline'], None)
        self.assertEqual(metadata['Caption-Abstract'], None)

    def test_set_get(self):
        metadata = photo.Metadata(self.filename)
        sample = '!!!'
        metadata['Caption-Abstract'] = sample
        self.assertEqual(metadata['Caption-Abstract'], sample)

    def test_in(self):
        metadata = photo.Metadata(self.filename)
        metadata['Caption-Abstract'] = '!!!'
        self.assertIn('Caption-Abstract', metadata)

    def test_del(self):
        metadata = photo.Metadata(self.filename)
        metadata['Headline'] = 'Ostrava'
        del metadata['Headline']
        self.assertEqual(metadata['Headline'], None)

    def test_set_update(self):
        metadata = photo.Metadata(self.filename)
        tags = {
            'Caption-Abstract': 'Hello World!',
            'Headline': 'Welcome.',
        }
        metadata.update(tags)
        self.assertEqual(metadata['Headline'],
                         tags['Headline'])
        self.assertEqual(metadata['Caption-Abstract'],
                         tags['Caption-Abstract'])

    def test_set_whitespace(self):
        metadata = photo.Metadata(self.filename)
        sample = 'Apples + bananas'
        metadata['Headline'] = sample
        self.assertEqual(metadata['Headline'], sample)

    def test_set_quotes(self):
        metadata = photo.Metadata(self.filename)
        sample = 'Gargamel\'s cat said: "I hate smurfs!"'
        metadata['Headline'] = sample
        self.assertEqual(metadata['Headline'], sample)

    def test_set_equal(self):
        metadata = photo.Metadata(self.filename)
        sample = '2 - 3 = -1'
        metadata['Headline'] = sample
        self.assertEqual(metadata['Headline'], sample)


class InfoTest(FileTestCase):

    def test_read_empty(self):
        i = photo.Info(self.filename)
        self.assertIsNone(i.title)
        self.assertEqual(i.locations, [])
        self.assertIsNone(i.description)

    def test_read_missing(self):
        os.remove(self.filename)
        i = photo.Info(self.filename)
        self.assertIsNone(i.title)
        self.assertEqual(i.locations, [])
        self.assertIsNone(i.description)

    def test_write(self):
        i = photo.Info(self.filename)

        i.title = u'Telefonní budky'
        i.locations = ['Brno']
        i.description = u'Sbírka telefonních budek.\nVážně!'

        self.assertEqual(i.title, u'Telefonní budky')
        self.assertEqual(i.locations, ['Brno'])
        self.assertEqual(i.description, u'Sbírka telefonních budek.\nVážně!')
        self.assertEqual(unicode(i), u'Telefonní budky\n'
                                     u'(Brno)\n'
                                     u'\nSbírka telefonních budek.\nVážně!\n')

    def test_write_partial(self):
        i = photo.Info(self.filename)

        i.title = u'Telefonní budky'
        i.description = u'Sbírka telefonních budek.\nVážně!'
        self.assertEqual(unicode(i), u'Telefonní budky\n'
                                     u'\nSbírka telefonních budek.\nVážně!\n')

        i.locations = ['Brno', 'Ostrava']
        i.description = None
        self.assertEqual(unicode(i), u'Telefonní budky\n'
                                     u'(Brno, Ostrava)\n')

    def test_read_none(self):
        with open(self.filename, 'w') as f:
            f.write(u'Titulek\n(None)\n\nPopisek.'.encode('utf-8'))

        i = photo.Info(self.filename)
        self.assertEqual(i.locations, [])
        self.assertEqual(unicode(i), u'Titulek\n'
                                     u'\nPopisek.\n')


class PhotoTest(PhotoTestCase):

    def test_caption(self):
        p = photo.Photo(self.filename)
        self.assertIsNone(p.caption)

        caption = u'Telefonní budka a nikde žádný kůň.'
        p.caption = caption
        self.assertEqual(p.metadata['Headline'], caption)
        self.assertEqual(p.caption, caption)
        self.assertIsNone(p.metadata['Caption-Abstract'])

    def test_datetime(self):
        p = photo.Photo(self.filename)
        self.assertEqual(p.datetime, self.datetime)

    def test_size(self):
        p = photo.Photo(self.filename)
        self.assertEqual(p.size, self.size)


class PhotoEditorTest(PhotoTestCase):

    def test_resize(self):
        pe = photo.PhotoEditor()
        p = photo.Photo(self.filename)

        size = (30, 20)
        p = pe.resize(p, *size)
        self.assertEqual(size, p.size)

    def test_fix_caption(self):
        pe = photo.PhotoEditor()
        caption = u'Řeřicha řekla: "Miluji tě!"'
        caption_single_quoted = u"'Řeřicha řekla: \"Miluji tě!\"'"
        caption_double_quoted = u'"Řeřicha řekla: "Miluji tě!""'

        p = photo.Photo(self.filename)

        p.metadata['Caption-Abstract'] = caption
        p = pe.fix_caption(p)
        self.assertEqual(p.metadata['Headline'], caption)
        self.assertIsNone(p.metadata['Caption-Abstract'])

        p.metadata['Headline'] = caption
        p = pe.fix_caption(p)
        self.assertEqual(p.metadata['Headline'], caption)
        self.assertIsNone(p.metadata['Caption-Abstract'])

        p.metadata['Caption-Abstract'] = caption_single_quoted
        p = pe.fix_caption(p)
        self.assertEqual(p.metadata['Headline'], caption)
        self.assertIsNone(p.metadata['Caption-Abstract'])

        p.metadata['Headline'] = caption_double_quoted
        p = pe.fix_caption(p)
        self.assertEqual(p.metadata['Headline'], caption)
        self.assertIsNone(p.metadata['Caption-Abstract'])
