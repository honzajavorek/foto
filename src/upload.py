#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Uploader
"""


from getpass import getpass
import album
import config
import gdata.photos.service #@UnresolvedImport
import log



class Uploader:

    album = None

    def __init__(self):
        album_file = config.Config().get('application', 'workingDirectory')
        self.album = album.Album(album_file)
        
        log.log('info', 'Connecting to Picasa...')
        gd_client = gdata.photos.service.PhotosService()
        gd_client.email = config.Config().get('settings', 'user')
        gd_client.password = getpass()
        gd_client.source = 'Elk'
        gd_client.ProgrammaticLogin()
        log.log('ok', 'Connected to Picasa.')
        
        config.Config().set('settings', 'picasa_client', gd_client)
        
    def run(self):
        self.album.create_remote()
        for p in self.album.get_photos():
            p = self.album.get_photo(p)
            print p.get_basename()
        
        # vezme fotky co jsou v albu a udela nejakou tmp slozku, kam je nakopiruje
        # v tmp slozce vsem predela popisky z headline do caption-abstract
        # v tmp slozce vsechny predela imagemagickem na mensi (fit to 480×640) ... convert dragon.gif    -resize 64x64\>  shrink_dragon.gif
        # vsechno musi mit stejny nazev jak melo, uploadne na net
        # smaze tmp


if __name__ == '__main__':
    pass

