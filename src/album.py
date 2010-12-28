#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Directory as album.
"""


from glob import glob
import config
import os
import photo
import re
import sys


class Album:

    album_file = None
    album_id = None
    
    remote_album = None

    def __init__(self, album_file, album_id=None):
        self.album_file = album_file
        if not album_id:
            album_name = os.path.basename(os.path.dirname(album_file + '/..'))
            self.album_id = re.sub(r'^[\d\-]+\s*', '', album_name)
        else:
            self.album_id = album_id

    def get_remote(self):
        if (self.remote_album):
            return self.remote_album 
        
        picasa = config.Config().get('picasa', 'client')
        
        albums = picasa.GetUserFeed(user=config.Config().get('picasa', 'user'))
        album = None
        for a in albums.entry:
            if a and (self.__to_unicode(a.gphoto_id.text) == self.__to_unicode(self.album_id) or self.__to_unicode(a.title.text) == self.__to_unicode(self.album_id)):
                album = a
                break
        
        if not album:
            raise Exception('Album %s does not exist.' % self.album_id)
        
        self.remote_album = album
        return album
    
    def get_photo(self, photo_file):
        return photo.Photo(self.album_file + '/' + photo_file)
    
    def get_remote_photos(self):
        picasa = config.Config().get('picasa', 'client')
        album = self.get_remote()
        photos = picasa.GetFeed('/data/feed/api/user/default/albumid/%s?kind=photo' % album.gphoto_id.text)
        return photos.entry
        
        #for photo in photos.entry:
            #photo.media.description.text
            #photo.title.text
            
    def get_photos(self):
        #os.chdir(config.Config().get('application', 'workingDirectory'))
        return glob(os.path.join(self.album_file, '*.[jJ][pP][gG]'))

        #for file in glob...:
            #photo_file = os.path.basename(file)
            #print self.__get_caption(photo_file)
            
    def __to_unicode(self, object, encoding='utf-8'):
        """Recodes string to Unicode"""
        
        if isinstance(object, basestring):
            if not isinstance(object, unicode):
                object = unicode(object, encoding)
        return object

if __name__ == '__main__':
    pass
    
