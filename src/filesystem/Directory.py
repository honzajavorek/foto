#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from filesystem.File import File
from glob import glob



class Directory(object):
    """Album directory abstraction."""
    
    
    
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
    
    
    
    def get_name(self):
        """Provides directory basename."""
        
        return self.name
    
    
    
    def get_files(self):
        """Provides all image files in directory."""
        
        files = glob(os.path.join(self.path, '*.[jJ][pP][gG]'))
        files.sort()
        for f in files:
            yield File(f)
            
            
            
    def wipe_captions(self):
        """Wipes captions of all files in directory."""
        
        for f in self.get_files():
            f.set_caption('')



if __name__ == '__main__':
    pass



