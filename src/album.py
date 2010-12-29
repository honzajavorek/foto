#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Directory as album.
"""


from glob import glob
import config
import gdata.photos #@UnresolvedImport
import log
import os
import photo
import re


class Album:

    album_file = None
    album_id = None
    info_file = None
    
    remote_album = None

    def __init__(self, album_file, album_id=None):
        self.album_file = album_file
        if not album_id:
            album_name = os.path.basename(os.path.dirname(album_file + '/..'))
            self.album_id = re.sub(r'^[\d\-]+\s*', '', album_name)
        else:
            self.album_id = album_id
            
        self.info_file = self.album_file + '/' + config.Config().get('settings', 'info_file')

    def get_remote(self):
        if (self.remote_album):
            return self.remote_album 
        
        picasa = config.Config().get('settings', 'picasa_client')
        
        albums = picasa.GetUserFeed(user=config.Config().get('settings', 'user'))
        album = None
        for a in albums.entry:
            if a and (self.__to_unicode(a.gphoto_id.text) == self.__to_unicode(self.album_id) or self.__to_unicode(a.title.text) == self.__to_unicode(self.album_id)):
                album = a
                break
        
        if not album:
            raise Exception('Album %s does not exist.' % self.album_id)
        
        self.remote_album = album
        return album
    
    def get_photo(self, photo_file, remote_photo=None):
        return photo.Photo(self.album_file + '/' + photo_file, remote_photo)
    
    def get_remote_photos(self):
        picasa = config.Config().get('settings', 'picasa_client')
        album = self.get_remote()
        photos = picasa.GetFeed('/data/feed/api/user/default/albumid/%s?kind=photo' % album.gphoto_id.text)
        return photos.entry
        
    def get_photos(self):
        return glob(os.path.join(self.album_file, '*.[jJ][pP][gG]'))

    def info_file_exists(self):
        return os.path.exists(self.info_file)
    
    def create_info_file(self):
        log.log('info', 'Creating new info file.')
        remote_album = self.get_remote()
        contents = "%s\n(%s)\n\n%s\n" % (remote_album.title.text, remote_album.location.text, remote_album.summary.text)
        
        info_file = open(self.info_file, 'w')
        info_file.write(contents)
        info_file.close()
        log.log('info', 'New info file created.')
        
    def parse_info_file(self):
        log.log('info', 'Parsing info file.')
        contents = file(self.info_file).read()
        matches = re.compile(r'([^\n]+)\n(\((.+)\)\n)?(\n([^\n]+))?\s*', re.MULTILINE|re.DOTALL).match(contents)
        return { 'title': matches.group(1), 'location': matches.group(3), 'summary': matches.group(5) }
        
    def sync_info_file(self):
        contents = self.parse_info_file()
        remote_album = self.get_remote()
        
        log.log('info', 'Synchronizing info file values.')
        remote_changed = False
        local_changed = False
        # if local value does not exist in remote album, update this attribute in remote album (and vv)
        for key in contents.iterkeys():
            if (not remote_album.__dict__[key].text) and contents[key]:
                log.log('info', 'Value "%s" updated remotely.' % key)
                remote_album.__dict__[key].text = contents[key]
                remote_changed = True
            elif (not contents[key]) and remote_album.__dict__[key].text:
                log.log('info', 'Value "%s" updated locally.' % key)
                contents[key] = remote_album.__dict__[key].text
                local_changed = True
            else:
                log.log('info', 'Value "%s" left without changes.' % key)
        
        if remote_changed:
            log.log('info', 'Saving info remotely.')
            picasa = config.Config().get('settings', 'picasa_client')
            self.remote_album = picasa.Put(remote_album, remote_album.GetEditLink().href, converter=gdata.photos.AlbumEntryFromString)

        if local_changed:
            self.create_info_file()

    def __to_unicode(self, object, encoding='utf-8'):
        """Recodes string to Unicode"""
        
        if isinstance(object, basestring):
            if not isinstance(object, unicode):
                object = unicode(object, encoding)
        return object

if __name__ == '__main__':
    pass
    
