#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Photo file.
"""


import os
import re
import subprocess


class Photo:

    photo_file = None

    def __init__(self, photo_file):
        self.photo_file = photo_file

    def get_basename(self):
        return os.path.basename(self.photo_file)
    
    def set_caption(self, caption):
        subprocess.Popen(('exiftool', self.photo_file, '-charset', 'iptc=UTF8', '-Caption-Abstract=""', '-Headline="%s"' % caption), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    def get_caption(self):
        p = subprocess.Popen(('exiftool', self.photo_file, '-charset', 'iptc=UTF8', '-Caption-Abstract'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.communicate()[0]
        return self.__recode(re.sub(r'\s*$', '', re.sub(r'^[^:]+:\s*', '', output)), 'utf-8') # todo: utf-8 ... ???

    def __recode(self, contents, original_charset):
        """Recodes contents to UTF-8 and then to Unicode string"""
        
        if original_charset not in ['utf-8', 'UTF-8', 'U8', 'UTF', 'utf8', 'UTF8']:
            contents = contents.decode(original_charset)
        return self.__to_unicode(contents)
        
    def __to_unicode(self, object, encoding='utf-8'):
        """Recodes string to Unicode"""
        
        if isinstance(object, basestring):
            if not isinstance(object, unicode):
                object = unicode(object, encoding)
        return object

if __name__ == '__main__':
    pass
    
