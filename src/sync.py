#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Synchronizer
"""


from getpass import getpass
import album
import config
import gdata.photos.service #@UnresolvedImport
import glob
import os
import photo



class Synchronizer:

    album = None

    def __init__(self, album_id):
        album_file = config.Config().get('application', 'workingDirectory')
        self.album = album.Album(album_file, album_id)
        
        gd_client = gdata.photos.service.PhotosService()
        gd_client.email = config.Config().get('picasa', 'user')
        gd_client.password = getpass()
        gd_client.source = 'Elk'
        gd_client.ProgrammaticLogin()
        
        config.Config().set('picasa', 'client', gd_client)

    def run(self):
        photos = self.album.get_remote_photos()
        for p in photos:
            photo_file = self.album.get_photo(p.title.text)
            photo_file.set_caption(p.media.description.text) # fixing captions, rewriting originals by remote versions


if __name__ == '__main__':
    pass

