#!/usr/bin/python
# -*- coding: utf-8 -*-
import os



class File(object):
    """Album file abstraction."""
    
    
    
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.extension = os.path.splitext(self.name)[1]
    
    
    
    def get_name(self):
        return self.name
    
    
    
    def get_caption(self):
        pass
        