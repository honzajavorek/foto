# -*- coding: utf-8 -*-


import os

from elk.utils import list_files
from elk.metadata import Metadata


def captions(directory):
    for filename in list_files(directory, ext='jpg'):
        basename = os.path.basename(filename)

        meta = Metadata(filename)
        caption = meta.get('Headline', meta['Caption-Abstract'])

        print u'{0}: {1}'.format(basename, caption or ' - ')


def captions_fix(directory):
    for filename in list_files(directory, ext='jpg'):
        basename = os.path.basename(filename)

        meta = Metadata(filename)
        caption = meta.get('Headline', meta['Caption-Abstract'])
        caption = unicode(caption or '')

        if caption:
            old_caption = caption

            single_quoted = caption[0] in "'" and caption[-1] == "'"
            double_quoted = caption[0] in '"' and caption[-1] == '"'

            if single_quoted or double_quoted:
                caption = caption[1:-1]

            meta['Headline'] = caption
            del meta['Caption-Abstract']

            print u'{0}: {1} -> {2}'.format(basename, old_caption, caption)
