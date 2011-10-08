# -*- coding: utf-8 -*-


from filesystem.Directory import Directory
from tools.API import API
from tools.Config import Config
import getopt
import log
import sys


class Controller(object):
    """Application controller."""

    def __init__(self, args):
        """Parses arguments and launches action."""
        self.api = API()
        self.dir = Directory(self.api, Config().get('application', 'workingDirectory'))
        
        actions = self._parse_args(args)
        try:
            for action in actions:
                action()
        except Exception as e:
            if Config().get('application', 'debug'):
                raise
            log.error('Error (%s).' % str(e))
        
    
    def _parse_args(self, args):
        """Parses arguments and returns what action to launch."""
        try:
            opts = getopt.getopt(args, 'uslwvq', ['upload', 'sync', 'list', 'wipe', 'video', 'quiet'])[0]
            
            for opt, _ in opts:
                if opt in ('-q', '--quiet'):
                    log.info('Quiet mode.')
                    Config().set('application', 'quiet', str(True))
            
            actions = []
            for opt, _ in opts:
                if opt in ('-u', '--upload'):
                    log.info('Starting upload of current directory.')
                    actions.append(self.upload)
                    
                elif opt in ('-s', '--sync'):
                    log.info('Starting synchronization of captions and info.')
                    actions.append(self.sync)
                    
                elif opt in ('-l', '--list'):
                    log.info('Listing all captions in current directory.')
                    actions.append(self.list)
                    
                elif opt in ('-v', '--video'):
                    log.info('Converting videos from MOV to AVI in current directory.')
                    actions.append(self.video)
                    
                elif opt in ('-w', '--wipe'):
                    log.info('Wiping all captions in current directory.')
                    actions.append(self.wipe)
        
        except getopt.GetoptError:
            log.info('Bad arguments.')
            self._print_help()
            
        if not actions:
            log.info('Missing action.')
            self._print_help()
        return actions
    
    def upload(self):
        self.dir.upload()
    
    def sync(self):
        self.dir.sync()
    
    def list(self):
        for file in self.dir.get_files():
            print '%s\t%s' % (file.name, file.caption)
    
    def wipe(self):
        self.dir.wipe_captions()
        
    def video(self):
        self.dir.convert_videos()
    
    def _print_help(self):
        """Prints usage help screen."""
        
        print '''
Usage:
    elk [OPTIONS]
    Always works with current directory (considered then as album).

    OPTIONS:
    -u, --upload            uploads directory to Picasa
    -s, --sync              synchronizes captions with remote album in Picasa
    -l, --list              list all captions
    -w, --wipe              wipes all captions
    -v, --video             converts all Panasonic DMC-FZ8 vids from MOV to AVI
    
    -q, --quiet             no log output
'''
        sys.exit(1)

