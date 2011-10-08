#!/usr/bin/python
# -*- coding: utf-8 -*-
from subprocess import CalledProcessError
from tools.ExifTool import ExifTool
import log
import os
import re
import stat
import subprocess
import tempfile


class FileTypeError(Exception):
    pass


class FileName(unicode):
    
    def __new__(cls, path):
        name, ext = os.path.splitext(path)
        path = name + ext.lower()
        return super(FileName, cls).__new__(FileName, path)
    

class File(object):
    """Album file abstraction."""
    
    PHOTO_FORMATS = ['jpg']
    VIDEO_FORMATS = ['mov']
    CONVERSION_TIME_EST_PER_KB = 0.00495652174 # dummy estimate for my computer (empiric)
    
    def __init__(self, path):
        self.path = self._normalize(path)
        self.name = FileName(os.path.basename(self.path))
        self.extension = os.path.splitext(self.name)[1].strip('.')
        
        self.is_photo = self.extension in File.PHOTO_FORMATS
        self.is_video = self.extension in File.VIDEO_FORMATS
    
    def _normalize(self, path):
        name, ext = os.path.splitext(path)
        with_lower_ext = name + ext.lower()
        with_upper_ext = name + ext.upper()
        
        if os.path.isfile(with_upper_ext):
            log.warning('File extension is uppercase! Performing autocorrection.')
            os.rename(path, with_lower_ext)
            
        if not os.path.isfile(with_lower_ext):
            raise IOError('File %s does not exist.' % with_lower_ext)
            
        return with_lower_ext
    
    def __str__(self):
        return self.name
    
    def get_date(self):
        if not self.is_photo:
            raise NotImplementedError()
        datetime = ExifTool(self.path).get_tag('DateTimeOriginal')
        matches = re.match(r'(\d{4})\W(\d{2})\W(\d{2})', datetime)
        return '%s-%s-%s' % (matches.group(1), matches.group(2), matches.group(3))
    
    @property
    def size(self):
        return os.path.getsize(self.path) / 1024 # kB
    
    @property
    def caption(self):
        """Provides caption of the file. In case of incorrect tags autocorrection takes place."""
        if not self.is_photo:
            raise NotImplementedError()
        
        et = ExifTool(self.path)
        headline = et.get_tag('Headline')
        
        if not headline:
            caption = et.get_tag('Caption-Abstract')
            if caption:
                log.warning('Caption is not placed correctly in tags! Performing autocorrection.')
                self.caption = caption
            return caption
        
        return headline
    
    @caption.setter
    def caption(self, caption):
        """Correctly sets caption."""
        if not self.is_photo:
            raise NotImplementedError()
        et = ExifTool(self.path)
        et.set_tag('Headline', caption)
        et.set_tag('Caption-Abstract', '')
            
    def convert(self):
        if not self.is_video:
            raise FileTypeError()
        
        mov_size = self.size # kB
        avi_filename = os.path.splitext(self.path)[0] + '.avi'
        
        command = ('ffmpeg', '-i', self.path, '-vcodec', 'libx264', '-crf', '25.5', '-acodec', 'libmp3lame',
                   '-ab', '64kb', '-ac', '1', '-ar', '8000', '-aspect', '4:3', '-r', '30', '-coder', '1',
                   '-flags2', '+dct8x8', '-flags', '+loop', '-deblockalpha', '0', '-deblockbeta', '0', '-cmp',
                   '+chroma', '-partitions', '+parti4x4+parti8x8+partp8x8', '-me_method', 'umh', '-subq', '9',
                   '-me_range', '16', '-g', '250', '-keyint_min', '25', '-sc_threshold', '40', '-i_qfactor', '0.714',
                   '-qblur', '0.5', '-b_strategy', '1', '-threads', '2', '-trellis', '2', '-chromaoffset', '0',
                   '-qcomp', '0.60', '-qmin', '10', '-qmax', '51', '-qdiff', '4', '-y', '-f', 'avi', avi_filename)
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderrdata = process.communicate()
        
        if process.returncode > 0:
            log.error(stderrdata)
            raise CalledProcessError(process.returncode, 'ffmpeg')
        
        avi_size = os.path.getsize(avi_filename) / 1024 # kB
        percents = 0 if not avi_size else 100 - ((int(avi_size) * 100) / int(mov_size))
        
        return (avi_size, percents, avi_filename)
    
    def resize(self, scale):
        if not self.is_photo:
            raise FileTypeError()
        
        file, filename = tempfile.mkstemp()
        
        command = ('convert', self.path, '-resize', '%s>' % scale, filename) # ImageMagick
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderrdata = process.communicate()
        
        if process.returncode > 0:
            log.error(stderrdata)
            raise CalledProcessError(process.returncode, 'convert')
        
        return os.fdopen(file, 'r+b'), filename
        
        
