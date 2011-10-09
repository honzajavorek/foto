# -*- coding: utf-8 -*-


from filesystem.File import File, FileName
from glob import glob
from tools.VideoConverter import VideoConverter
from tools.ImageMagick import ImageMagick
from tools.API import Text
from tools.Config import Config
import log
import os
import re
import time


class Directory(object):
    """Album directory abstraction."""
    
    RE_INFO_FILE = re.compile(r'([^\n]+)\n(\(([^\)]+)\)\n)?(\n([^\n]+))?\s*', re.MULTILINE|re.DOTALL)

    def __init__(self, api, path):
        self.api = api
        self._initialize(path)
    
    def _initialize(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.info_file = os.path.join(path, Config().get('settings', 'info_file'))
    
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
        self._initialize(new)
    
    def get_files(self, ext='jpg'):
        """Provides all image files in directory."""
        ext_pattern = ''
        for ch in ext.strip('.'):
            ext_pattern += '[%s%s]' % (ch, ch.upper())  
        
        files = glob(os.path.join(self.path, '*.%s' % ext_pattern))
        files.sort()
        for f in files:
            yield File(f)

    def sync_info(self, album):
        """Synchronizes new info file."""
        if os.path.isfile(self.info_file):
            # sync existing info file
            local_info = self.get_info()

            # figure out timestamp
            timestamp = time.strptime(self.parse_name()[0], '%Y-%m-%d')

            # if local value does not exist in remote album, update this attribute in remote album (and vv)
            # local info has higher priority
            info = {
                'title': local_info['title'] or Text(album.title),
                'location': local_info['location'] or Text(album.location),
                'summary': local_info['summary'] or Text(album.summary),
            }
            self.set_info(**info)
            self.api.set_info(album=album, timestamp=timestamp, **info)
            
        else:
            # create a brand new info file
            self.set_info(album.title.text, album.location.text, album.summary.text)
            
    def set_info(self, title, location, summary):
        if len(summary) > 1000:
            raise ValueError('Description has %d characters, has to be up to 1000.' % len(summary))
        contents = '%s\n(%s)\n\n%s\n' % (title, location, summary)
        with open(self.info_file, 'w') as f:
            f.write(contents)
            
    def get_info(self):
        try:
            with open(self.info_file, 'r') as f:
                matches = Directory.RE_INFO_FILE.match(f.read())
            return {'title': matches.group(1), 'location': matches.group(3), 'summary': matches.group(5)}
        except IOError:
            return {'title': '', 'location': '', 'summary': ''}
            
    def wipe_captions(self):
        """Wipes captions of all files in directory."""
        for f in self.get_files():
            f.caption = ''
            
    def convert_videos(self):
        """Converts all videos from Panasonic DMC-FZ8 MOV to x264 AVI."""
        for file in self.get_files('mov'):
            size = file.size
            time_est = File.CONVERSION_TIME_EST_PER_KB * size / 60 # min
            log.info("Converting %s to AVI (%.2f MB), estimated time %.2f min." % (file.name, file.size / 1024, time_est))
            avi_size, percents, _ = VideoConverter().convert(file)
            log.info("Done: %.2f MB, %d %% compression." % (avi_size / 1024, percents))
            
    
    def fetch_date(self):
        """Tries to find out date of this album."""
        date = self.parse_name()[0]
        if not date:
            for f in self.get_files():
                date = f.get_date()
        return date
    
    def get_album(self):
        return self.api.get_album(self.parse_name()[1])
    
    def upload(self):
        # if date is missing in directory name, add it
        new_name = '%s %s' % (self.fetch_date(), self.parse_name()[1])
        log.info("Renaming folder to %s." % new_name)
        self.rename(new_name)
        
        # check remote album existence
        album = self.get_album()
        if album:
            log.info("Album exists remotely.")
        else:
            log.error("Album doesn't exist remotely, creating a new one.") # TODO create
            album = self.api.create_album(self.parse_name()[1])
    
        # create/sync info file
        log.info("Synchronizing info.")
        self.sync_info(album)
    
        # prepare scale for resizing
        scale = Config().get('settings', 'scale')
        
        # process photos
        remote_photos = [FileName(Text(photo.title)) for photo in self.api.get_photos(album)]
        for file in self.get_files():
            if file.name in remote_photos:
                log.info('%s    =    Picasa' % file.name)
            else:
                # resize
                log.info('%s   ==>   %s' % (file.name, scale))
                tmp_file, tmp_filename = ImageMagick().resize(file, scale)
                
                log.info('%s   ==>   Picasa' % file.name)
                try:
                    self.api.upload_file(album, tmp_file, file.name)
                except Exception as e:
                    # try again
                    log.error("%s - trying again." % str(e))
                    self.api.upload_file(album, tmp_file, file.name)
                
                try:
                    tmp_file.close()
                    os.unlink(tmp_filename)
                except OSError:
                    pass
        
        # finished
        log.info("Done.")
                
    
    def sync(self):
        # if date is missing in directory name, add it
        new_name = '%s %s' % (self.fetch_date(), self.parse_name()[1])
        log.info("Renaming folder to %s." % new_name)
        self.rename(new_name)
        
        # check remote album existence
        album = self.get_album()
        if not album:
            log.error("Album doesn't exist remotely, nothing to synchronize.")
            return
        log.info("Album exists remotely.")
        
        # create/sync info file
        log.info("Synchronizing info.")
        self.sync_info(album)
    
        # checking captions of remote photos and synchronizing them
        log.info("Synchronizing captions.")
        for photo in self.api.get_photos(album):
            file = File(os.path.join(self.path, FileName(Text(photo.title))))
            
            local_caption = file.caption
            remote_caption = Text(photo.media.description)
            
            if not local_caption and remote_caption:
                file.caption = remote_caption
                log.info(('%s   <==   Picasa   %s' % (file.name, remote_caption))[0:70])
            elif local_caption and not remote_caption:
                self.api.set_caption(photo, local_caption)
                log.info(('%s   ==>   Picasa   %s' % (file.name, local_caption))[0:70])
            else:
                log.info(('%s    ?    Picasa   %s - %s' % (file.name, local_caption, remote_caption))[0:70])
        
        # finished
        log.info("Done.")

