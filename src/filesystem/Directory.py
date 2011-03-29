#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from filesystem.File import File
from glob import glob
import re



class Directory(object):
    """Album directory abstraction."""
    
    
    
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
    
    
    
    def get_name(self):
        """Provides directory basename."""
        
        return self.name
    
    
    
    def parse_name(self):
        matches = re.match(r'(\d{4}\-\d{2}\-\d{2})?\s*(.+)', self.name)
        return (matches.group(1), matches.group(2))
    
    
    
    def rename(self, new_basename):
        old = self.path
        new = os.path.join(os.path.split(old)[0], new_basename)
        os.rename(old, new)
    
    
    
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
            
            
    
    def fetch_date(self):
        """Tries to find out date of this album."""
        
        date = self.parse_name()[0]
        if not date:
            for f in self.get_files():
                date = f.get_date()
        return date
    
    
    
    def upload(self):
        # if date is missing in directory name, add it
        self.rename('%s %s' % (self.fetch_date(), self.parse_name()[1]))
        
        # check remote album existence (if missing, create it)
        pass
        
        # create/sync info file
        pass
    
        # rename all photos *.JPG to *.jpg
        pass
    
        # resize photos
        pass
    
        # uploading temporary files and removing them in case of success
        pass
    
        # UNDER CONSTRUCTION
        raise NotImplementedError()
    
    
    
    def sync(self):
        # check remote album existence (if missing, create it)
        pass
    
        # create/sync info file
        pass
    
        # checking captions of remote photos and synchronizing them
        pass
    
        # UNDER CONSTRUCTION
        raise NotImplementedError()



if __name__ == '__main__':
    pass



