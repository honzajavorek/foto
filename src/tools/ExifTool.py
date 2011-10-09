# -*- coding: utf-8 -*-


import subprocess
import re
import os


class ExifTool(object):
    """ExifTool python wrapper."""

    def __init__(self, file):
        self.file = file
    
    def get_tag(self, tag):
        try:
            output = subprocess.Popen(('exiftool', self.file, '-charset', 'iptc=UTF8', '-%s' % tag), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
            if re.match('Warning', output):
                return ''
            output = self._to_unicode(output)
            
        except UnicodeDecodeError:
            output = subprocess.Popen(('exiftool', self.file, '-%s' % tag), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
            if re.match('Warning', output):
                return ''
            output = self._to_unicode(output)
                
        
        # parse out the value
        tag = re.sub(r'^[^:]+:\s*', '', output).strip().strip('"')
        return tag
    
    def set_tag(self, tag, content):
        subprocess.Popen(('exiftool', self.file, '-charset', 'iptc=UTF8', '-%s="%s"' % (tag, content)), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        
        tmp_file = '%s_original' % self.file
        if os.path.isfile(tmp_file):
            os.unlink(tmp_file)
    
    def _to_unicode(self, object, encoding='utf-8'):
        """Recodes string to Unicode."""
        
        if isinstance(object, basestring):
            if not isinstance(object, unicode):
                object = unicode(object, encoding)
        return object

