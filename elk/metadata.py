# -*- coding: utf-8 -*-


import re
from sh import exiftool


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
