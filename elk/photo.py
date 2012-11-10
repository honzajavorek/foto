# -*- coding: utf-8 -*-


import re
import datetime
from sh import exiftool
from wand.image import Image

from elk.filesystem import File, FileEditor


class Metadata(object):

    _tag_re = re.compile(r'^[^:]+:\s*')

    def __init__(self, filename):
        self.filename = filename

    def __getitem__(self, tag):
        tag_opt = '-' + tag
        try:
            output = str(exiftool(self.filename, '-charset', 'iptc=UTF8',
                         tag_opt))
            if re.match('Warning', output):
                return None
            output = unicode(output, 'utf8')

        except UnicodeDecodeError:
            output = str(exiftool(self.filename, tag_opt))
            if re.match('Warning', output):
                return None
            output = unicode(output, 'utf8')

        tag = self._tag_re.sub('', output).strip() or None
        return tag

    def get(self, tag, default):
        if tag in self:
            return self[tag]
        return default

    def __setitem__(self, tag, content):
        content = '' if content is None else unicode(content)
        tag_opt = u"-{tag}={content}".format(tag=tag, content=content)

        exiftool(self.filename, '-charset', 'iptc=UTF8',
                 '-overwrite_original_in_place', tag_opt)

    def update(self, tags):
        tag_opts = []
        for tag, content in tags.items():
            content = '' if content is None else unicode(content)
            tag_opt = u"-{tag}={content}".format(tag=tag, content=content)
            tag_opts.append(tag_opt)

        if tag_opts:
            exiftool(self.filename, '-charset', 'iptc=UTF8',
                     '-overwrite_original_in_place', *tag_opts)

    def __delitem__(self, tag):
        self[tag] = None

    def __contains__(self, tag):
        return self[tag] is not None


class Photo(File):

    _datetime_re = re.compile(r'(\d{4})\W(\d{2})\W(\d{2})'
                              r'\s'
                              r'(\d{2})\W(\d{2})\W(\d{2})')

    def __init__(self, filename):
        super(Photo, self).__init__(filename)
        self.metadata = Metadata(filename)
        self._datetime = None

    @property
    def caption(self):
        return self.metadata.get('Headline',
                                 self.metadata['Caption-Abstract'])

    @caption.setter
    def caption(self, value):
        self.metadata['Headline'] = value
        del self.metadata['Caption-Abstract']

    @property
    def datetime(self):
        if not self._datetime:
            dt = self.metadata.get('DateTimeOriginal',
                                   self.metadata['CreateDate'])
            if dt:
                match = self._datetime_re.match(dt)
                groups = map(int, match.groups())
                self._datetime = datetime.datetime(*groups)
        return self._datetime

    @property
    def size(self):
        with Image(filename=self.filename) as img:
            return img.size


class PhotoEditor(FileEditor):

    def resize(self, photo, width, height):
        with Image(filename=photo.filename) as img:
            img.resize(width, height)
            img.save(filename=photo.filename)
        return photo.__class__(photo.filename)

    def fix_caption(self, photo):
        caption = unicode(photo.caption or '')

        single_quoted = caption[0] in "'" and caption[-1] == "'"
        double_quoted = caption[0] in '"' and caption[-1] == '"'

        if single_quoted or double_quoted:
            caption = caption[1:-1]

        photo.caption = caption or None
        return photo
