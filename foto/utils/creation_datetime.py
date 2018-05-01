import re
import os

from .metadata import Metadata


_numeric_re = re.compile(r'^(\D*)(\d+)$')


def creation_datetime(filename):
    candidates = list(_gen_candidates(filename))
    for tag in [
        'SubSecCreateDate',
        'CreateDate',
        'SubSecDateTimeOriginal',
        'DateTimeOriginal',
        'SubSecModifyDate',
        'ModifyDate',
    ]:
        dt = _find_in_tag(candidates, tag)
        if dt:
            return dt
    return _find_in_tag(candidates, 'FileModifyDate')


def _gen_candidates(filename):
    yield filename

    base, ext = os.path.splitext(filename)
    yield base + '.jpg'
    yield base + '.JPG'

    # search for previous
    for _ in range(5):
        match = _numeric_re.search(base)
        if match:
            base = match.group(1) + str(int(match.group(2)) - 1)
            yield base + '.jpg'
            yield base + '.JPG'


def _find_in_tag(candidates, tag):
    for candidate in candidates:
        if os.path.exists(candidate):
            meta = Metadata(candidate)
            dt = meta[tag]
            if dt:
                return dt
    return None
