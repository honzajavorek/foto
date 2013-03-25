# -*- coding: utf-8 -*-


import os
import re
import datetime
from sh import exiftool
from wand.image import Image

from elk import config
from elk.filesystem import File, FileEditor, Directory, DirectoryEditor


class Metadata(object):
    """Photo's metadata abstraction with :class:`dict`-like interface.
    Uses subprocess calls to ExifTool.
    """

    _tag_re = re.compile(r'^[^:]+:\s*')

    def __init__(self, filename):
        self.filename = filename

    def __getitem__(self, tag):
        tag_opt = '-' + tag
        try:
            # try IPTC first
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
    """Photo abstraction object based on :class:`~elk.filesystem.File`."""

    _datetime_re = re.compile(r'(\d{4})\W(\d{2})\W(\d{2})'
                              r'\s'
                              r'(\d{2})\W(\d{2})\W(\d{2})')

    def __init__(self, filename):
        super(Photo, self).__init__(filename)
        self.metadata = Metadata(filename)
        self._datetime = None

    @property
    def caption(self):
        """Returns photo's caption."""
        return self.metadata.get('Headline',
                                 self.metadata['Caption-Abstract'])

    @caption.setter
    def caption(self, value):
        """Sets photo's caption."""
        self.metadata['Headline'] = value
        del self.metadata['Caption-Abstract']

    @property
    def datetime(self):
        """Photo's date of creation."""
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
        """Returns tuple (width, height) of image's dimensions."""
        with Image(filename=self.filename) as img:
            return img.size


class PhotoEditor(FileEditor):
    """Manipulates :class:`Photo` objects."""

    def resize(self, photo, width, height):
        """Resizes photo to given dimensions."""
        with Image(filename=photo.filename) as img:
            img.resize(width, height)
            img.save(filename=photo.filename)
        return photo.__class__(photo.filename)

    def fix_caption(self, photo):
        """Fixes photo's caption if it is somehow corrupted.
        Removes redundant quoting, fixes encoding, saves
        caption to it's proper meta tag.
        """
        caption = unicode(photo.caption or '')

        single_quoted = caption[0] in "'" and caption[-1] == "'"
        double_quoted = caption[0] in '"' and caption[-1] == '"'

        if single_quoted or double_quoted:
            caption = caption[1:-1]

        photo.caption = caption or None
        return photo


class Info(object):
    """Album info object."""

    _parser_re = re.compile(r'([^\n]+)\n(\(([^\)]+)\)\n)?(\n([^\n]+))?\s*',
                            re.MULTILINE | re.DOTALL)

    def __init__(self, filename):
        f = File(filename)

        self._title = None
        self._locations = []
        self._description = None

        try:
            content = f.content.strip()
            match = self._parser_re.match(content)

            if match:
                self._title = match.group(1)
                self._locations = self._parse_locations(match.group(3))
                self._description = match.group(5)
        except IOError:
            pass

        self.file = f

    def _parse_locations(self, line):
        locations = map(unicode.strip, line.split(','))
        return filter(lambda x: not (x == 'None' or not x), locations)

    def __unicode__(self):
        s = (self._title or '') + '\n'
        if self._locations:
            s += '(' + ', '.join(self._locations) + ')\n'
        if self._description:
            s += '\n' + self._description + '\n'
        return s

    def _save(self):
        self.file.content = unicode(self)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        assert title
        self._title = title
        self._save()

    @property
    def locations(self):
        return self._locations

    @locations.setter
    def locations(self, locations):
        self._locations = locations
        self._save()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description
        self._save()


class Album(Directory):
    """Album object based on :class:`~elk.filesystem.Directory`."""

    _name_re = re.compile(r'(\d{4}\-\d{2}\-\d{2})?\s*(.+)')

    def __init__(self, path):
        super(Album, self).__init__(path)

        info_filename = os.path.join(self.path,
                                     config.get('album', 'info_basename'))
        cover_filename = os.path.join(self.path,
                                      config.get('album', 'cover_basename'))

        self.info = Info(info_filename)
        self._cover = File(cover_filename)
        self._date, title = self.parse_name()

        self.title = title
        self.info.title = title

    def list(self):
        """Lists only files of JPEG photos, returns
        :class:`Photo` instances.
        """
        return super(Album, self).list(ext='.jpg', cls=Photo)

    def parse_name(self):
        """Parses directory's name to get album's date and title."""
        date = None
        title = self.name

        match = self._name_re.match(self.name)
        if match and match.group(1):
            group = map(int, match.group(1).split('-'))
            date = datetime.date(*group)
            title = match.group(2)

        return date, title

    @property
    def date(self):
        """Provides date. In case it's missing,
        automatic detection from photos takes place.
        """
        if not self._date:
            dt = datetime.datetime.now()
            for photo in self.list():
                if photo.datetime:
                    dt = min(photo.datetime, dt)
            self._date = dt.date()
        return self._date

    @property
    def cover(self):
        """Provides cover photo."""
        try:
            filename = self._cover.content.strip()
            if not filename:
                return None
            photo = Photo(filename)
            if not photo.exists:
                self._cover.content = None
                return None
            return photo
        except IOError:
            return None

    @cover.setter
    def cover(self, photo):
        """Sets cover photo."""
        self._cover.content = photo.filename


class AlbumEditor(DirectoryEditor):
    """Manipulates :class:`Album` objects."""

    def fix_name(self, album):
        """Fixes album's name according to convention.
        Date is automatically detected from photos.
        """
        date, name = album.parse_name()
        if not date:
            new_name = str(album.date) + ' ' + name
            album = self.rename(album, new_name)
        return album

    def edit_info(self, album):
        """Opens album's info file in text editor."""
        editor = FileEditor()
        editor.edit(album.info.file)
