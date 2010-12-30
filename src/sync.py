#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Synchronizer
"""


from getpass import getpass
import album
import config
import gdata.photos.service #@UnresolvedImport
import log


class Synchronizer:

    album = None

    def __init__(self, album_id):
        album_file = config.Config().get('application', 'workingDirectory')
        self.album = album.Album(album_file, album_id)
        
        log.log('info', 'Connecting to Picasa...')
        gd_client = gdata.photos.service.PhotosService()
        gd_client.email = config.Config().get('settings', 'user')
        gd_client.password = getpass()
        gd_client.source = 'Elk'
        gd_client.ProgrammaticLogin()
        log.log('ok', 'Connected to Picasa.')
        
        config.Config().set('settings', 'picasa_client', gd_client)

    def run(self):
        if not self.album.info_file_exists():
            log.log('ok', 'Info file does not exist. Creating...')
            self.album.create_info_file()
        else:
            log.log('ok', 'Info file exists. Synchronizing...')
            self.album.sync_info_file()
        
        photos = self.album.get_remote_photos()
        for p in photos:
            p = self.album.get_photo(p.title.text, p)
            p.sync_caption()


if __name__ == '__main__':
    pass

