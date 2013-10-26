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

    def resolve(self, filename):
        for candidate in self._gen_candidates(filename):
            if os.path.exists(candidate):
                meta = Metadata(candidate)
                dt = meta.get('CreateDate', meta['FileModifyDate'])
                if dt:
                    return dt.date()
        return None


def creation_date(filename):
    return _CreationDateResolver().resolve(filename)
