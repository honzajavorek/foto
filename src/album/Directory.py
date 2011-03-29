#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from image.File import File
from glob import glob



class Directory(object):
    """Album directory abstraction."""
    
    
    
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
    
    
    
    def get_name(self):
        return self.name
    
    
    
    def get_files(self):
        for f in glob(os.path.join(self.path, '*.[jJ][pP][gG]')):
            yield File(f)