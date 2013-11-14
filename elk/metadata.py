# -*- coding: utf-8 -*-


import re
from datetime import datetime

import times
from sh import exiftool


class Metadata(object):
    """Photo's metadata abstraction with :class:`dict`-like interface.
    Uses subprocess calls to ExifTool.
    """

    _tag_re = re.compile(r'^[^:]+:\s*')
    _datetime_re = re.compile(
        r'^(\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?)([\-+]\d{2}:\d{2})?$'
    )

    def __init__(self, filename):
        self.filename = filename

    def _to_datetime(self, s):
        if s.startswith('0000:00:00'):
            return None
        # strip off the timezone information so we always get
        # tz-unaware local time
        return datetime.strptime(s[:19], '%Y:%m:%d %H:%M:%S')

    def _from_datetime(self, dt):
        if dt.tzinfo is not None:
            dt = times.from_local(dt)
        return dt.strftime('%Y:%m:%d %H:%M:%S+00:00')

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

        if tag and self._datetime_re.match(tag):
            return self._to_datetime(tag)
        return tag

    def get(self, tag, default):
        if tag in self:
            return self[tag]
        return default

    def __setitem__(self, tag, content):
        if content:
            if isinstance(content, datetime):
                content = self._from_datetime(content)
            else:
                content = unicode(content)
        else:
            content = ''

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
