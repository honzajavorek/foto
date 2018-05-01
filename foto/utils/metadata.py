import re
import string
from datetime import datetime, time

from plumbum.cmd import exiftool
from plumbum.commands.processes import ProcessExecutionError

from .format_datetime import format_datetime


__all__ = ['FileFormatError', 'Metadata']


class FileFormatError(Exception):

    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename


class Metadata(object):
    """Photo/video metadata abstraction with :class:`dict`-like interface.
    Uses subprocess calls to ExifTool.
    """

    read_charsets = ('iptc=UTF8', 'iptc=latin2', 'UTF8')

    _tag_re = re.compile(r'^[^:]+:\s*')
    _datetime_re = re.compile(
        r'^(\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?)([\-+]\d{2}:\d{2})?$'
    )
    _time_re = re.compile(
        r'^(\d{2}:\d{2}:\d{2}(\.\d+)?)([\-+]\d{2}:\d{2})?$'
    )
    _timezone_re = re.compile(r'([+\-])(\d{2}):(\d{2})$')

    _correct_encoding_re = re.compile(
        r'^[\w\s' + re.escape(string.punctuation) + r']+$',
        re.U
    )
    _incorrect_encoding_char_mapping = {
        frozenset(['ř', 'ø']): 'ř',
        frozenset(['ě', 'ì']): 'ě',
        frozenset(['č', 'è']): 'č',
        frozenset(['ů', 'ù']): 'ů',
        frozenset(['ň', 'ò']): 'ň',
    }

    class TagDoesNotExist(Exception):
        pass

    def __init__(self, filename):
        self.filename = filename

    def __getitem__(self, tag):
        try:
            values = [
                self._get_tag(tag, charset)
                for charset in self.read_charsets
            ]
        except self.TagDoesNotExist:
            return None

        value = self._detect_correct_charset(values)

        if value:
            if self._datetime_re.match(value):
                return self._to_datetime(value)
            if self._time_re.match(value):
                return self._to_time(value)
        return value

    def get(self, tag, default=None):
        if tag in self:
            return self[tag]
        return default

    def getfirst(self, tags):
        for tag in tags:
            value = self.get(tag)
            if value:
                return tag, value
        return None, None

    def _get_tag(self, tag, charset=None):
        args = [self.filename, '-preserve', '-' + tag]
        if charset:
            args += ['-charset', charset]

        output = self._exiftool(*args)
        if re.match('Warning', output):
            raise self.TagDoesNotExist()

        value = self._tag_re.sub('', output).strip()
        if not value:
            raise self.TagDoesNotExist()

        return value

    def _detect_correct_charset(self, values):
        values_are_identical = len(frozenset(values)) == 1
        if values_are_identical:
            return values[0]

        # Gather detailed information about cadidate values
        values_details = [
            {
                'value': value,
                'has_correct_encoding': bool(self._correct_encoding_re.search(value)),  # NOQA
                'length': len(value),
            }
            for value in values
        ]

        # Exclude candidates with incorrect encoding
        values_details = [
            details for details in values_details
            if details['has_correct_encoding']
        ]
        if not len(values_details):
            raise RuntimeError(
                'The Metadata._correct_encoding_re RE '
                'resulted in false positive'
            )
        if len(values_details) == 1:
            return values_details[0]['value']

        # Exclude candidates with diacritics encoded as two chars
        min_length = min(*[
            details['length'] for details in values_details
        ])
        min_length_values_details = [
            details for details in values_details
            if details['length'] == min_length
        ]
        if len(min_length_values_details) == 1:
            min_length_details = min_length_values_details[0]
            non_ascii_length = len([
                char for char in min_length_details['value']
                if ord(char) > 127
            ])
            ascii_length = min_length_details['length'] - non_ascii_length
            wrong_length = 2 * non_ascii_length + ascii_length

            other_values_details_have_wrong_length = all([
                details['length'] == wrong_length
                for details in values_details
                if details['value'] != min_length_details['value']
            ])
            if other_values_details_have_wrong_length:
                return min_length_details['value']

        # Exclude candidates with missing characters
        max_length = max(*[
            details['length'] for details in values_details
        ])
        values_details = [
            details for details in values_details
            if details['length'] == max_length
        ]
        if len(values_details) == 1:
            return values_details[0]['value']

        # Exclude candidates with improperly decoded characters
        unknown_differences = []
        for char_position in range(max_length):
            chars = [
                details['value'][char_position]
                for details in values_details
            ]
            chars_set = frozenset(chars)
            if len(chars_set) == 1:
                continue  # identical characters
            elif chars_set in self._incorrect_encoding_char_mapping:
                correct_char = self._incorrect_encoding_char_mapping[chars_set]
                index = chars.index(correct_char)
                return values_details[index]['value']
            else:
                unknown_differences.append(chars_set)

        # Couldn't detect correct value
        unknown_differences_formatted = ', '.join([
            '{} - {}'.format(*chars_set)
            for chars_set in unknown_differences
        ])
        raise RuntimeError((
            'The Metadata._incorrect_encoding_char_mapping '
            'does not contain following differences: {}'
        ).format(unknown_differences_formatted))

    def _to_datetime(self, s):
        if s.startswith('0000:00:00'):
            return None

        timezone_match = self._timezone_re.search(s)
        if timezone_match:
            s = self._timezone_re.sub(r'\1\2\3', s)
            formats = [
                '%Y:%m:%d %H:%M:%S.%f%z',
                '%Y:%m:%d %H:%M:%S%z',
            ]
        else:
            formats = [
                '%Y:%m:%d %H:%M:%S.%f',
                '%Y:%m:%d %H:%M:%S',
                '%Y:%m:%d',
            ]
        for fmt in formats:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                pass
        raise ValueError('Unable to parse as datetime: {}'.format(s))

    def _to_time(self, s):
        if s.startswith('00:00'):
            return None

        timezone_match = self._timezone_re.search(s)
        if timezone_match:
            s = self._timezone_re.sub(r'\1\2\3', s)
            formats = ['%H:%M:%S.%f%z', '%H:%M:%S%z']
        else:
            formats = ['%H:%M:%S.%f', '%H:%M:%S']
        for fmt in formats:
            try:
                dt = datetime.strptime(s, fmt)
                if timezone_match:
                    return dt.timetz()
                return dt.time()
            except ValueError:
                pass
        raise ValueError('Unable to parse as datetime: {}'.format(s))

    def __setitem__(self, tag, content):
        if content:
            if isinstance(content, datetime) or isinstance(content, time):
                content = format_datetime(content)
        else:
            content = ''
        self.update({tag: content})

    def update(self, tags):
        tag_opts = []
        for tag, content in tags.items():
            content = content or ''
            tag_opt = "-{tag}={content}".format(tag=tag, content=content)
            tag_opts.append(tag_opt)

        if tag_opts:
            self._exiftool(self.filename, '-preserve',
                           '-overwrite_original_in_place',
                           '-charset', 'iptc=UTF8',
                           '-iptc:codedcharacterset=UTF8', *tag_opts)

    def setdefault(self, tag, content):
        if tag not in self:
            self[tag] = content

    def __delitem__(self, tag):
        self[tag] = None

    def __contains__(self, tag):
        try:
            self._get_tag(tag, self.read_charsets[0])
        except self.TagDoesNotExist:
            return False
        else:
            return True

    def _exiftool(self, *args, **kwargs):
        try:
            return exiftool(*args, **kwargs)
        except ProcessExecutionError as e:
            if 'file format error' in e.stderr.lower():
                _, filename = e.stderr.strip().split('format error - ')
                raise FileFormatError(filename)
            else:
                raise
