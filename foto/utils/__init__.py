import os
import shlex
import pipes
import datetime
from pathlib import Path
import subprocess

try:
    import pync
except (Exception, ImportError):
    pync = None

from send2trash import send2trash as to_trash

from .metadata import Metadata, FileFormatError
from .geo import location
from .creation_datetime import creation_datetime
from .format_datetime import format_datetime


__all__ = [
    'to_trash', 'Metadata', 'location', 'creation_datetime',
    'parse_cmd_args', 'list_dirs', 'list_files', 'notify',
    'FileFormatError', 'format_datetime',
]


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
    return sorted(Path(filename) for filename
                  in filenames if os.path.isdir(filename))


def list_files(directory, exts=None, recursive=False):
    if exts is not None:
        exts = frozenset('.' + ext.lstrip('.') for ext in exts)

    def list_dir(directory):
        for basename in os.listdir(directory):
            filename = os.path.join(directory, basename)
            if recursive and os.path.isdir(filename):
                for filename in list_files(filename, exts, recursive=True):
                    yield Path(filename)
                continue
            elif exts and not os.path.splitext(filename)[1].lower() in exts:
                continue
            yield Path(filename)

    return sorted(list_dir(directory))


def mimetype(filename):
    process = subprocess.run(['file', '--mime', '--brief', str(filename)], check=True, capture_output=True)
    return process.stdout.decode('utf-8').strip()


def is_corrupted_file(filename):
    return mimetype(filename) == 'application/octet-stream; charset=binary'


def notify(name, message):
    if pync:
        pync.Notifier.notify(message, title=name)


def to_naive(dt):
    if dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt


def shift_datetime(dt, days, hours):
    if isinstance(dt, datetime.time):
        return (
            datetime.datetime.combine(datetime.date(10, 10, 10), dt)
            + datetime.timedelta(hours=hours)
        ).time()
    return dt + datetime.timedelta(days=days, hours=hours)
