#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Photo file.
"""


import config
import gdata.media #@UnresolvedImport
import log
import os
import re
import subprocess


class Photo:

    photo_file = None
    remote_photo = None

    def __init__(self, photo_file, remote_photo=None):
        self.photo_file = photo_file
        self.remote_photo = remote_photo

    def get_basename(self):
        return os.path.basename(self.photo_file)
    
    def set_caption(self, caption):
        log.log('ok', 'Setting caption to %s file.' % self.get_basename())
        subprocess.Popen(('exiftool', self.photo_file, '-charset', 'iptc=UTF8', '-Caption-Abstract=""', '-Headline="%s"' % caption), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    def set_remote_caption(self, caption):
        if not self.remote_photo.media:
            self.remote_photo.media = gdata.media.Group()
        if not self.remote_photo.media.description:
            self.remote_photo.media.description = gdata.media.Description()
        self.remote_photo.media.description.text = caption
        self.remote_photo.summary.text = caption
        
        log.log('info', 'Saving caption remotely...')
        picasa = config.Config().get('settings', 'picasa_client')
        self.remote_photo = picasa.UpdatePhotoMetadata(self.remote_photo)
    
    def get_caption(self):
        p = subprocess.Popen(('exiftool', self.photo_file, '-charset', 'iptc=UTF8', '-Headline'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.communicate()[0]
        headline = self.__recode(re.sub(r'\s*$', '', re.sub(r'^[^:]+:\s*', '', output)), 'utf-8').strip('"')
        
        if not headline:
            p = subprocess.Popen(('exiftool', self.photo_file, '-charset', 'iptc=UTF8', '-Caption-Abstract'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = p.communicate()[0]
            caption = self.__recode(re.sub(r'\s*$', '', re.sub(r'^[^:]+:\s*', '', output)), 'utf-8').strip('"')
            
            log.log('warning', 'Caption is not placed correctly in tags! Starting autocorrection...')
            self.set_caption(caption)
            
            return caption
        return headline

    def sync_caption(self):
        if self.remote_photo:
            log.log('ok', 'Synchronizing caption of %s.' % self.get_basename())
            
            local_caption = self.get_caption()
            remote_caption = self.remote_photo.summary.text
        
            if (not local_caption) and remote_caption:
                self.set_caption(self.remote_photo.media.description.text)
                log.log('info', 'Caption updated locally.')
            elif local_caption and (not remote_caption):
                self.set_remote_caption(local_caption)
                log.log('info', 'Caption updated remotely.')
            else:
                log.log('info', 'Caption left without changes.')
        else:
            log.log('warning', 'Unable to synchronize caption of a photo without remote data.')

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
    
