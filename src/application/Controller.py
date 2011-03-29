#!/usr/bin/python
# -*- coding: utf-8 -*-
import getopt
from tools.Config import Config
import log
import sys
from filesystem.Directory import Directory



class Controller(object):
    """Application controller."""



    def __init__(self, args):
        """Parses arguments and launches action."""
        
        self.dir = Directory(Config().get('application', 'workingDirectory'))
        
        action = self.__parse_args(args)
        action()
        
        
    
    def __parse_args(self, args):
        """Parses arguments and returns what action to launch."""
        
        try:
            opts = getopt.getopt(args, 'uslwd', ['upload', 'sync', 'list', 'wipe', 'debug'])[0]
            
            for opt, arg in opts: #@UnusedVariable
                if opt in ('-d', '--debug'):
                    log.info('Debug mode.')
                    Config().set('application', 'debug', str(True))
            
            action = None
            for opt, arg in opts: #@UnusedVariable
                if opt in ('-u', '--upload'):
                    log.info('Starting upload of current directory.')
                    action = self.upload
                    
                elif opt in ('-s', '--sync'):
                    log.info('Starting synchronization of captions.')
                    action = self.sync
                    
                elif opt in ('-l', '--list'):
                    log.info('Listing all captions in current directory.')
                    action = self.list
                    
                elif opt in ('-w', '--wipe'):
                    log.info('Wiping all captions in current directory.')
                    action = self.wipe
        
        except getopt.GetoptError:
            log.info('Bad arguments.')
            self.__print_help()
            
        if not action:
            log.info('Missing action.')
            self.__print_help()
        return action
    
    
    
    def upload(self):
        raise NotImplementedError()
    
    
    
    def sync(self):
        raise NotImplementedError()
    
    
    
    def list(self):
        for file in self.dir.get_files():
            print '%s\t%s' % (file.get_name(), file.get_caption())
    
    
    
    def wipe(self):
        self.dir.wipe_captions()
    
    
    
    def __print_help(self):
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
    
    -d, --debug             debug mode
'''
        sys.exit(1)



if __name__ == '__main__':
    pass


