# -*- coding: utf-8 -*-


import os
import re

from elk.metadata import Metadata


class _CreationDateResolver(object):

    _numeric_re = re.compile(r'^(\D*)(\d+)$')

    def _gen_candidates(self, filename):
        yield filename

        base, ext = os.path.splitext(filename)
        yield base + '.jpg'
        yield base + '.JPG'

        # search for previous
        for _ in range(5):
            match = self._numeric_re.search(base)
            if match:
                base = match.group(1) + str(int(match.group(2)) - 1)
                yield base + '.jpg'
                yield base + '.JPG'

    def _find_in_tag(self, candidates, tag):
        for candidate in candidates:
            if os.path.exists(candidate):
                meta = Metadata(candidate)
                dt = meta[tag]
                if dt:
                    return dt.date()
        return None

    def resolve(self, filename):
        candidates = list(self._gen_candidates(filename))
        date = self._find_in_tag(candidates, 'CreateDate')
        if date:
            return date
        return self._find_in_tag(candidates, 'FileModifyDate')


def creation_date(filename):
    return _CreationDateResolver().resolve(filename)
