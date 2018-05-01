import os
import shlex
import pipes
import datetime

try:
    import pync
except (Exception, ImportError):
    pync = None

from plumbum.cmd import file as file_cmd
from send2trash import send2trash as to_trash

from .metadata import Metadata, FileFormatError
from .geo import location
from .creation_datetime import creation_datetime
from .format_datetime import format_datetime


__all__ = [
    'to_trash', 'Metadata', 'location', 'creation_datetime',
    'parse_cmd_args', 'list_dirs', 'list_files', 'notify',
    'FileFormatError', 'detect_camera', 'format_datetime',
]


def detect_camera(filename):
    _, ext = os.path.splitext(filename)
    ext = ext.lstrip('.').lower()

    meta = Metadata(filename)
    make, model = meta['Make'], meta['Model']

    if make and model:
        return (make, model)

    if ext == 'mov' and meta['VendorID'] == 'Panasonic':
        width = int(meta.get('SourceImageWidth', 0))
        height = int(meta.get('SourceImageHeight', 0))
        if width == 640 and height == 480:
            return ('Panasonic', 'DMC-FZ8')

    return None


def parse_cmd_args(s, **wildcards):
    wildcards = {
        wildcard: pipes.quote(value) for
        (wildcard, value) in wildcards.items()
    }
    s = s.format(**wildcards)
    return shlex.split(s.strip())


def list_dirs(directory):
    filenames = (os.path.join(directory, basename) for basename
                 in os.listdir(directory))
    return sorted(filename for filename
                  in filenames if os.path.isdir(filename))


def list_files(directory, exts=None, recursive=False):
    if exts is not None:
        exts = frozenset('.' + ext.lstrip('.') for ext in exts)

    def list_dir(directory):
        for basename in os.listdir(directory):
            filename = os.path.join(directory, basename)
            if recursive and os.path.isdir(filename):
                for filename in list_files(filename, exts, recursive=True):
                    yield filename
                continue
            elif exts and not os.path.splitext(filename)[1].lower() in exts:
                continue
            yield filename

    return sorted(list_dir(directory))


def is_corrupted_file(filename):
    return file_cmd(filename).strip() == '{}: data'.format(filename)


def notify(name, message):
    if pync:
        pync.Notifier.notify(message, title=name)


def to_naive(dt):
    if dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt


def shift_datetime(dt, hours):
    if isinstance(dt, datetime.time):
        return (
            datetime.datetime.combine(datetime.date(10, 10, 10), dt)
            + datetime.timedelta(hours=hours)
        ).time()
    return dt + datetime.timedelta(hours=hours)
