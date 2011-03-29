#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from tools.ExifTool import ExifTool
import log
import re



class File(object):
    """Album file abstraction."""
    
    
    
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.extension = os.path.splitext(self.name)[1]
    
    
    
    def get_name(self):
        """Provides file basename."""
        
        return self.name
    
    
    
    def get_date(self):
        datetime = ExifTool(self.path).get_tag('DateTimeOriginal')
        matches = re.match(r'(\d{4})\W(\d{2})\W(\d{2})', datetime)
        return '%s-%s-%s' % (matches.group(1), matches.group(2), matches.group(3))
        
        
        
    def get_caption(self):
        """Provides caption of the file. In case of incorrect tags autocorrection takes place."""
        
        et = ExifTool(self.path)
        headline = et.get_tag('Headline')
        if not headline:
            
            caption = et.get_tag('Caption-Abstract')
            if caption:
                log.warning('Caption is not placed correctly in tags! Starting autocorrection...')
                self.set_caption(caption)
            return caption
        
        return headline
    
    
    
    def set_caption(self, caption):
        """Correctly sets caption."""
        
        et = ExifTool(self.path)
        et.set_tag('Headline', caption)
        et.set_tag('Caption-Abstract', '')



if __name__ == '__main__':
    pass



