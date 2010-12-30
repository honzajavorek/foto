#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Photo file.
"""


import album
import config
import gdata.media #@UnresolvedImport
import log
import os
import re
import shutil
import stat
import subprocess


class Photo:

    photo_file = None
    remote_photo = None
    
    remote_upload_attempts = 0

    def __init__(self, photo_file, remote_photo=None):
        self.photo_file = photo_file
        self.remote_photo = remote_photo

    def get_basename(self):
        return os.path.basename(self.photo_file)
    
    def get_remote(self, album_id):
        if not self.remote_photo:
            remote = None
            a = album.Album(os.path.dirname(self.photo_file), album_id)
            photos = a.get_remote_photos()
            for p in photos:
                if self.__to_unicode(p.title.text) == self.__to_unicode(self.get_basename()):
                    remote = p
                    break
            self.remote_photo = remote
        return self.remote_photo
    
    def create_remote(self, album_id): # album.gphoto_id.text
        if self.remote_photo or self.get_remote(album_id):
            log.log('warning', 'Remote photo already exists.')
        else:
            log.log('ok', 'Uploading %s...' % self.get_basename())
            log.log('info', 'Preparing temporary copy...')
            
            tmp_photo = self.photo_file + '_uploaded'
            shutil.copyfile(self.photo_file, tmp_photo)
            
            scale = config.Config().get('settings', 'scale')
            log.log('info', 'Resizing temporary copy to %s...' % scale)
            subprocess.Popen(('convert', tmp_photo, '-resize', '%s>' % scale, tmp_photo), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            os.chmod(tmp_photo, stat.S_IREAD|stat.S_IWRITE|stat.S_IRGRP|stat.S_IROTH);
            
            #print album_url
            #print self.get_basename()
            #print self.get_caption()
            #print tmp_photo
            
            log.log('info', 'Creating remote photo...')
            self.remote_upload_attempts = 0
            self.__insert_remote(album_id, tmp_photo)
            log.log('ok', 'Remote photo created.')
    
    def __insert_remote(self, album_id, tmp_photo):
        picasa = config.Config().get('settings', 'picasa_client')
        try:
            album_url = '/data/feed/api/user/default/albumid/%s' % album_id
            self.remote_photo = picasa.InsertPhotoSimple(album_url, self.get_basename(), '' + self.get_caption(), tmp_photo, content_type='image/jpeg')
        except gdata.photos.service.GooglePhotosException as e:
            self.remote_upload_attempts += 1
            if self.remote_upload_attempts < 10:
                log.log('warning', 'Failed. Attempt No. %d.' % (self.remote_upload_attempts + 1))
                log.log('info', 'Deleting corrupted remote photo...')
                picasa.Delete(self.get_remote(album_id))
                self.__insert_remote(album_id, tmp_photo)
            else:
                raise e
    
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
    
    def __get_exiftool_tag(self, tag):
        try:
            p = subprocess.Popen(('exiftool', self.photo_file, '-charset', 'iptc=UTF8', '-%s' % tag), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = self.__to_unicode(p.communicate()[0])
        except UnicodeDecodeError as e: #@UnusedVariable
            p = subprocess.Popen(('exiftool', self.photo_file, '-%s' % tag), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = self.__to_unicode(p.communicate()[0])
        return output
    
    def get_caption(self):
        output = self.__get_exiftool_tag('Headline')
        if re.match('Warning', output):
            headline = ''
        else:
            headline = re.sub(r'^[^:]+:\s*', '', output).strip().strip('"')
        
        if not headline:
            output = self.__get_exiftool_tag('Caption-Abstract')
            if re.match('Warning', output):
                caption = ''
            else:
                caption = re.sub(r'^[^:]+:\s*', '', output).strip().strip('"')
            
            if caption:
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
    
